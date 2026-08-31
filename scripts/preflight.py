import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
checks = []


def check(name, ok, detail):
    checks.append(
        {
            "check": name,
            "passed": bool(ok),
            "detail": detail,
        }
    )


# =========================================================
# Required project files
# =========================================================

required = [
    "README.md",
    "REPRODUCTION.md",
    "IMPROVEMENT_CHANGELOG.md",
    "AGENT_DISCLOSURE.md",
    "SECURITY.md",
    "Dockerfile",
    "requirements.txt",
    "baseline/baseline.py",
    "src/traceguard/pipeline.py",
    "evaluation/compare.py",
    "data/ground_truth.json",
]


for rel in required:
    p = ROOT / rel

    check(
        f"required:{rel}",
        p.exists(),
        "present" if p.exists() else "missing",
    )


# =========================================================
# Benchmark integrity
# =========================================================

trace_dir = ROOT / "data/traces"

trace_count = len(
    list(trace_dir.glob("*.json"))
)

check(
    "benchmark_cases",
    trace_count == 40,
    f"{trace_count} cases",
)


# =========================================================
# Python
# =========================================================

python_ok = sys.version_info >= (3, 10)

check(
    "python",
    python_ok,
    sys.version.split()[0],
)


# =========================================================
# Docker binary
# =========================================================

docker_path = shutil.which("docker")

check(
    "docker_binary",
    docker_path is not None,
    "found" if docker_path else "not found",
)


# =========================================================
# Docker daemon
# =========================================================

docker_ok = False

if docker_path:

    try:
        docker_ok = (
            subprocess.run(
                ["docker", "info"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=20,
            ).returncode
            == 0
        )

    except Exception:
        docker_ok = False


check(
    "docker_daemon",
    docker_ok,
    "running" if docker_ok else "unavailable",
)


# =========================================================
# Comparison artifact
# =========================================================

comparison_path = (
    ROOT / "artifacts/comparison.json"
)


if comparison_path.exists():

    try:

        obj = json.loads(
            comparison_path.read_text(
                encoding="utf-8"
            )
        )

        benchmark = obj.get(
            "benchmark",
            {}
        )

        benchmark_cases = benchmark.get(
            "cases"
        )

        baseline_cases = benchmark.get(
            "baseline_cases"
        )

        advanced_cases = benchmark.get(
            "advanced_cases"
        )

        same_benchmark = benchmark.get(
            "same_benchmark"
        )

        comparison_valid = (
            benchmark_cases == trace_count
            and baseline_cases == trace_count
            and advanced_cases == trace_count
            and same_benchmark is True
        )

        detail = (
            f"cases={benchmark_cases} "
            f"baseline={baseline_cases} "
            f"advanced={advanced_cases} "
            f"benchmark={trace_count} "
            f"same_benchmark={same_benchmark}"
        )

        check(
            "comparison_artifact",
            comparison_valid,
            detail,
        )

    except Exception as exc:

        check(
            "comparison_artifact",
            False,
            f"invalid JSON: {exc}",
        )

else:

    check(
        "comparison_artifact",
        False,
        "missing; generate comparison.json before submission",
    )


# =========================================================
# Mutation report
# =========================================================

mutation_path = (
    ROOT / "artifacts/mutation_report.json"
)


if mutation_path.exists():

    try:

        mutation = json.loads(
            mutation_path.read_text(
                encoding="utf-8"
            )
        )

        check(
            "mutation_artifact",
            isinstance(mutation, dict),
            "present and valid JSON",
        )

    except Exception as exc:

        check(
            "mutation_artifact",
            False,
            f"invalid JSON: {exc}",
        )

else:

    check(
        "mutation_artifact",
        False,
        "missing",
    )


# =========================================================
# Final qualification
# =========================================================

# Docker binary is intentionally informational here because
# docker_daemon performs the stronger availability check.
#
# Every other check must pass.

passed = all(
    item["passed"]
    for item in checks
    if item["check"] != "docker_binary"
)


report = {
    "qualification_passed": passed,
    "checks": checks,
}


# =========================================================
# Write preflight artifact
# =========================================================

artifacts_dir = ROOT / "artifacts"

artifacts_dir.mkdir(
    exist_ok=True
)


preflight_path = (
    artifacts_dir / "preflight.json"
)


preflight_path.write_text(
    json.dumps(
        report,
        indent=2,
    ),
    encoding="utf-8",
)


print(
    json.dumps(
        report,
        indent=2,
    )
)


sys.exit(
    0 if passed else 1
)