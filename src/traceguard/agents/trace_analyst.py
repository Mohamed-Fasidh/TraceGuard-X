import re

from src.traceguard.schemas import Trace


def analyze(raw: dict) -> Trace:

    claimed_tests = raw.get("claimed_tests", "")

    if not claimed_tests:
        match = re.search(
            r"(\d+)\s*/\s*(\d+)",
            raw.get("trajectory", "")
        )

        claimed_tests = (
            match.group(0)
            if match
            else ""
        )

    return Trace(
        trace_id=raw["trace_id"],
        task=raw["task"],
        requirements=raw.get(
            "requirements",
            []
        ),
        code=raw["code"],
        trajectory=raw.get(
            "trajectory",
            ""
        ),
        claimed_verdict=raw.get(
            "claimed_verdict",
            "UNKNOWN"
        ),
        claimed_tests=claimed_tests,
        claimed_exit_code=raw.get(
            "claimed_exit_code"
        ),
        claimed_output=raw.get(
            "claimed_output",
            ""
        ),
        case_type=raw.get(
            "case_type",
            "unknown"
        ),
        test_cases=raw.get(
            "test_cases",
            []
        ),
    )