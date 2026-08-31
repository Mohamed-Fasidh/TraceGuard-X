import re


SUCCESS_VERDICTS = {
    "PASS",
    "SUCCESS",
    "SOLVED",
    "OK",
}


def _case_exceptions(execution):
    """
    Extract exceptions captured by the sandbox harness.

    The harness catches candidate exceptions inside each test case,
    so Docker itself may still exit with code 0.
    """
    exceptions = []

    for case in execution.cases or []:
        exception = case.get("exception")

        if exception:
            exceptions.append({
                "input": case.get("input"),
                "expected": case.get("expected"),
                "exception": str(exception),
            })

    return exceptions


def _dependency_exceptions(exceptions):
    """
    Identify likely dependency/import failures separately from
    ordinary candidate runtime failures.
    """

    dependency_markers = (
        "ModuleNotFoundError",
        "ImportError",
        "No module named",
        "cannot import name",
    )

    return [
        item
        for item in exceptions
        if any(
            marker in item["exception"]
            for marker in dependency_markers
        )
    ]


def reconcile(trace, static, execution):

    findings = []

    claimed_success = (
        trace.claimed_verdict.upper()
        in SUCCESS_VERDICTS
    )

    # =========================================================
    # 1. STATIC ANALYSIS
    # =========================================================

    observed_fail = False

    if not static.syntax_ok:

        observed_fail = True

        findings.append({
            "category": "syntax_error",
            "severity": "critical",
            "message": (
                "Candidate failed static compilation."
            ),
            "evidence": {
                "error": static.compile_error,
            },
        })

    # =========================================================
    # 2. SANDBOX / INFRASTRUCTURE TIMEOUT
    # =========================================================

    if (
        not execution.executed
        and execution.timed_out
    ):

        findings.append({
            "category": "sandbox_timeout",
            "severity": "critical",
            "message": (
                "The Docker sandbox did not complete within "
                "the infrastructure timeout."
            ),
            "evidence": {
                "duration_ms": execution.duration_ms,
                "stderr": execution.stderr[-1500:],
            },
        })

    # =========================================================
    # 3. CANDIDATE TIMEOUT
    # =========================================================

    if (
        execution.executed
        and execution.timed_out
    ):

        observed_fail = True

        findings.append({
            "category": "timeout",
            "severity": "critical",
            "message": (
                "Candidate execution exceeded the "
                "execution time limit."
            ),
            "evidence": {
                "duration_ms": execution.duration_ms,
            },
        })

    # =========================================================
    # 4. PROCESS-LEVEL RUNTIME FAILURE
    # =========================================================

    if (
        execution.executed
        and execution.exit_code not in (0, None)
    ):

        observed_fail = True

        findings.append({
            "category": "runtime_error",
            "severity": "critical",
            "message": (
                "Independent execution returned a "
                "non-zero exit code."
            ),
            "evidence": {
                "exit_code": execution.exit_code,
                "stderr": execution.stderr[-1500:],
            },
        })

    # =========================================================
    # 5. CASE-LEVEL EXCEPTIONS
    # =========================================================

    case_exceptions = _case_exceptions(
        execution
    )

    dependency_exceptions = _dependency_exceptions(
        case_exceptions
    )

    ordinary_runtime_exceptions = [
        item
        for item in case_exceptions
        if item not in dependency_exceptions
    ]

    # ---------------------------------------------------------
    # Dependency failure
    # ---------------------------------------------------------

    if dependency_exceptions:

        observed_fail = True

        findings.append({
            "category": "dependency_error",
            "severity": "critical",
            "message": (
                "Independent execution encountered a "
                "candidate dependency/import failure."
            ),
            "evidence": {
                "exceptions": dependency_exceptions,
            },
        })

    # ---------------------------------------------------------
    # Runtime failure captured by harness
    # ---------------------------------------------------------

    if ordinary_runtime_exceptions:

        observed_fail = True

        findings.append({
            "category": "runtime_error",
            "severity": "critical",
            "message": (
                "Candidate raised an exception during "
                "independent test execution."
            ),
            "evidence": {
                "exceptions": ordinary_runtime_exceptions,
            },
        })

    # =========================================================
    # 6. BEHAVIOR FAILURE
    # =========================================================

    if (
        execution.executed
        and execution.tests_total is not None
        and execution.tests_passed is not None
        and execution.tests_passed < execution.tests_total
    ):

        observed_fail = True

        findings.append({
            "category": "behavior_failure",
            "severity": "high",
            "message": (
                "Independent tests found one or more "
                "behavior mismatches."
            ),
            "evidence": {
                "passed": execution.tests_passed,
                "total": execution.tests_total,
                "cases": execution.cases,
            },
        })

    # =========================================================
    # 7. TEST COUNT CLAIM VERIFICATION
    # =========================================================

    if trace.claimed_tests:

        nums = re.findall(
            r"\d+",
            trace.claimed_tests,
        )

        if len(nums) >= 2:

            claimed_passed = int(nums[0])
            claimed_total = int(nums[1])

            declared_total = len(
                trace.test_cases
            )

            #
            # Compare the original agent claim only against
            # the original declared test suite.
            #
            # Adversarial cases added by TraceGuard must not
            # create a false test-count mismatch.
            #

            if claimed_total == declared_total:

                declared_passed = None

                if execution.executed:

                    declared_cases = execution.cases[
                        :declared_total
                    ]

                    declared_passed = sum(
                        1
                        for case in declared_cases
                        if case.get("ok") is True
                    )

                if (
                    declared_passed is not None
                    and claimed_passed != declared_passed
                ):

                    findings.append({
                        "category": "test_count_mismatch",
                        "severity": "high",
                        "message": (
                            "Claimed test results differ from "
                            "independently observed results for "
                            "the originally declared test suite."
                        ),
                        "evidence": {
                            "claimed": {
                                "passed": claimed_passed,
                                "total": claimed_total,
                            },
                            "observed_declared": {
                                "passed": declared_passed,
                                "total": declared_total,
                            },
                        },
                    })

    # =========================================================
    # 8. OUTPUT CLAIM VERIFICATION
    # =========================================================

    if (
        trace.claimed_output
        and execution.executed
    ):

        observed_text = " ".join(
            str(value)
            for value in execution.observed_outputs
        )

        if (
            trace.claimed_output.strip()
            not in observed_text
        ):

            findings.append({
                "category": "output_mismatch",
                "severity": "high",
                "message": (
                    "Claimed output was not observed "
                    "in independent execution."
                ),
                "evidence": {
                    "claimed_output": (
                        trace.claimed_output
                    ),
                    "observed_outputs": (
                        execution.observed_outputs
                    ),
                },
            })

    # =========================================================
    # 9. CLAIM / EVIDENCE CONTRADICTION
    # =========================================================

    #
    # A contradiction is independent of severity.
    #
    # Example:
    #
    #   PASS claim + behavior failure
    #       => contradiction
    #
    #   PASS claim + runtime failure
    #       => contradiction
    #
    #   PASS claim + syntax failure
    #       => contradiction
    #
    #   PASS claim + dependency failure
    #       => contradiction
    #
    #   PASS claim + candidate timeout
    #       => contradiction
    #
    # A sandbox timeout alone is NOT treated as candidate
    # evidence because the candidate may never have executed.
    #

    candidate_failure_categories = {
        "syntax_error",
        "runtime_error",
        "dependency_error",
        "timeout",
        "behavior_failure",
    }

    candidate_failure_evidence = any(
        finding["category"]
        in candidate_failure_categories
        for finding in findings
    )

    if (
        claimed_success
        and candidate_failure_evidence
    ):

        findings.append({
            "category": "claim_evidence_contradiction",
            "severity": "critical",
            "message": (
                "Agent claimed success but independent "
                "candidate evidence indicates failure."
            ),
            "evidence": {
                "claimed_verdict": (
                    trace.claimed_verdict
                ),
                "tests_passed": (
                    execution.tests_passed
                ),
                "tests_total": (
                    execution.tests_total
                ),
                "exit_code": (
                    execution.exit_code
                ),
                "timed_out": (
                    execution.timed_out
                ),
                "static_syntax_ok": (
                    static.syntax_ok
                ),
                "case_exceptions": case_exceptions,
            },
        })

    # =========================================================
    # 10. VERIFICATION GAP
    # =========================================================

    #
    # Static failure is already sufficient evidence.
    #

    if (
        not execution.executed
        and not static.syntax_ok
    ):

        pass

    #
    # Infrastructure timeout is represented separately.
    #

    elif (
        not execution.executed
        and execution.timed_out
    ):

        pass

    #
    # No execution and no candidate/static failure:
    # insufficient evidence.
    #

    elif not execution.executed:

        findings.append({
            "category": "verification_gap",
            "severity": "high",
            "message": (
                "Independent candidate execution did not "
                "produce sufficient evidence for a correctness verdict."
            ),
            "evidence": {
                "executed": execution.executed,
                "timed_out": execution.timed_out,
                "stderr": execution.stderr[-1500:],
            },
        })

    return findings