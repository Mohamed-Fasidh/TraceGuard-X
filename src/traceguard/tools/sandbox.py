import json
import subprocess
import tempfile
import time
from pathlib import Path

from src.traceguard.schemas import ExecutionEvidence


DOCKER_STARTUP_TIMEOUT = 10
CANDIDATE_TIMEOUT = 5


def _harness(test_cases):
    cases_json = json.dumps(test_cases)

    return f"""
import candidate
import json
import signal


CASES = {cases_json!r}
CASES = json.loads(CASES)


def timeout_handler(signum, frame):
    raise TimeoutError("candidate execution exceeded {CANDIDATE_TIMEOUT}s")


signal.signal(signal.SIGALRM, timeout_handler)


results = []
passed = 0


for case in CASES:

    inp = case.get("input")
    expected = case.get("expected")

    try:

        signal.alarm({CANDIDATE_TIMEOUT})

        actual = candidate.solve(inp)

        signal.alarm(0)

        ok = actual == expected

        if ok:
            passed += 1

        results.append({{
            "input": inp,
            "expected": expected,
            "actual": actual,
            "ok": ok
        }})

    except TimeoutError as exc:

        signal.alarm(0)

        results.append({{
            "input": inp,
            "expected": expected,
            "ok": False,
            "timeout": True,
            "exception": str(exc)
        }})

    except Exception as exc:

        signal.alarm(0)

        results.append({{
            "input": inp,
            "expected": expected,
            "ok": False,
            "exception": f"{{type(exc).__name__}}: {{exc}}"
        }})


print(json.dumps({{
    "tests_passed": passed,
    "tests_total": len(CASES),
    "cases": results
}}))
"""


def _parse_harness_output(stdout: str):

    if not stdout or not stdout.strip():

        return None, "Docker container produced no stdout."

    lines = stdout.strip().splitlines()

    payload = lines[-1]

    try:

        obj = json.loads(payload)

    except json.JSONDecodeError as exc:

        return None, (
            "Harness output was not valid JSON: "
            f"{exc}. Raw output: {stdout[-2000:]}"
        )

    required = {
        "tests_passed",
        "tests_total",
        "cases",
    }

    missing = required - obj.keys()

    if missing:

        return None, (
            "Harness JSON is missing required fields: "
            f"{sorted(missing)}"
        )

    return obj, None


def run_sandbox(
    code: str,
    test_cases=None,
    timeout_seconds: int = DOCKER_STARTUP_TIMEOUT,
) -> ExecutionEvidence:

    test_cases = test_cases or [
        {
            "input": "hello",
            "expected": "hello",
        },
        {
            "input": "",
            "expected": "",
        },
    ]

    with tempfile.TemporaryDirectory(
        prefix="traceguard-"
    ) as td:

        work = Path(td)

        candidate_file = work / "candidate.py"

        harness_file = work / "harness.py"

        candidate_file.write_text(
            code,
            encoding="utf-8",
        )

        harness_file.write_text(
            _harness(test_cases),
            encoding="utf-8",
        )

        cmd = [
            "docker",
            "run",
            "--rm",

            # Network isolation
            "--network",
            "none",

            # Filesystem isolation
            "--read-only",

            # Drop Linux capabilities
            "--cap-drop",
            "ALL",

            "--security-opt",
            "no-new-privileges",

            # Resource limits
            "--memory",
            "128m",

            "--cpus",
            "0.50",

            "--pids-limit",
            "32",

            # Read-only source mount
            "-v",
            f"{work.resolve()}:/work:ro",

            "-w",
            "/work",

            # Controlled runtime
            "python:3.11-slim",

            "python",
            "harness.py",
        ]

        start = time.perf_counter()

        try:

            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )

            duration = (
                time.perf_counter() - start
            ) * 1000

            stdout = proc.stdout or ""
            stderr = proc.stderr or ""

            parsed, parse_error = (
                _parse_harness_output(stdout)
            )

            # -------------------------------------------------
            # Docker / harness infrastructure failure
            # -------------------------------------------------

            if parse_error:

                return ExecutionEvidence(
                    executed=False,
                    exit_code=proc.returncode,
                    stdout=stdout[-6000:],
                    stderr=(
                        stderr[-4000:]
                        + "\n"
                        + parse_error
                    )[-6000:],
                    duration_ms=duration,
                )

            passed = parsed["tests_passed"]

            total = parsed["tests_total"]

            cases = parsed["cases"]

            observed_outputs = [
                case.get("actual")
                for case in cases
                if "actual" in case
            ]

            candidate_timeout = any(
                case.get("timeout") is True
                for case in cases
            )

            return ExecutionEvidence(
                executed=True,
                exit_code=proc.returncode,
                stdout=stdout[-6000:],
                stderr=stderr[-6000:],
                duration_ms=duration,
                tests_passed=passed,
                tests_total=total,
                observed_outputs=observed_outputs,
                cases=cases,
                timed_out=candidate_timeout,
            )

        except subprocess.TimeoutExpired as exc:

            duration = (
                time.perf_counter() - start
            ) * 1000

            stdout = exc.stdout or ""
            stderr = exc.stderr or ""

            return ExecutionEvidence(
                executed=False,
                timed_out=True,
                stdout=str(stdout)[-4000:],
                stderr=(
                    str(stderr)
                    + "\n"
                    + (
                        "Docker infrastructure timeout: "
                        f"container did not complete within "
                        f"{timeout_seconds}s."
                    )
                )[-5000:],
                duration_ms=duration,
            )

        except FileNotFoundError:

            duration = (
                time.perf_counter() - start
            ) * 1000

            return ExecutionEvidence(
                executed=False,
                stderr=(
                    "Docker executable was not found on PATH."
                ),
                duration_ms=duration,
            )

        except subprocess.SubprocessError as exc:

            duration = (
                time.perf_counter() - start
            ) * 1000

            return ExecutionEvidence(
                executed=False,
                stderr=(
                    "Docker subprocess failed: "
                    f"{type(exc).__name__}: {exc}"
                ),
                duration_ms=duration,
            )

        except Exception as exc:

            duration = (
                time.perf_counter() - start
            ) * 1000

            return ExecutionEvidence(
                executed=False,
                stderr=(
                    "Unexpected sandbox infrastructure error: "
                    f"{type(exc).__name__}: {exc}"
                ),
                duration_ms=duration,
            )