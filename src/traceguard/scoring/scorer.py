def score(
    trace,
    static,
    execution,
    findings,
    property_evidence=None,
    evidence_coverage=1.0,
):

    # =========================================================
    # TEST PASS RATE
    # =========================================================

    if (
        execution.tests_total is not None
        and execution.tests_total > 0
        and execution.tests_passed is not None
    ):
        test_rate = (
            execution.tests_passed
            / execution.tests_total
        )

    elif (
        execution.executed
        and execution.exit_code == 0
    ):
        test_rate = 1.0

    else:
        test_rate = 0.0

    # =========================================================
    # PROPERTY RATE
    # =========================================================
    #
    # Property testing is supplementary evidence.
    #
    # If no actual property evidence exists, do not punish
    # the candidate for property_passed=False.
    #
    # Only use the property result when the property check
    # was actually executed.
    # =========================================================

    if property_evidence is None:
        property_rate = 1.0

    elif not property_evidence.get("executed", False):
        property_rate = 1.0

    else:
        property_rate = (
            1.0
            if property_evidence.get("passed", False)
            else 0.0
        )

    # =========================================================
    # FINDING CLASSIFICATION
    # =========================================================

    finding_categories = {
        f.get("category")
        for f in findings
    }

    contradiction = (
        "claim_evidence_contradiction"
        in finding_categories
    )

    mismatch = bool(
        finding_categories
        & {
            "test_count_mismatch",
            "output_mismatch",
        }
    )

    # Genuine candidate failures
    blocking_findings = {
        "syntax_error",
        "runtime_error",
        "timeout",
        "behavior_failure",
    }

    # Verification infrastructure failures
    verification_blockers = {
        "sandbox_timeout",
        "verification_gap",
    }

    has_blocking_failure = bool(
        finding_categories
        & blocking_findings
    )

    has_verification_blocker = bool(
        finding_categories
        & verification_blockers
    )

    # =========================================================
    # CLAIM CONSISTENCY
    # =========================================================

    claim_consistency = (
        0.2
        if contradiction
        else (
            0.4
            if mismatch
            else 1.0
        )
    )

    # =========================================================
    # QUALITY METRICS
    # =========================================================

    # Deterministic execution is the primary source of
    # functional correctness.
    functional = test_rate

    # Property testing is supplementary robustness evidence.
    robustness = (
        0.7 * test_rate
        + 0.3 * property_rate
    )

    code_quality = (
        1.0
        if static.syntax_ok
        else 0.0
    )

    # =========================================================
    # OVERALL SCORE
    # =========================================================

    total = (
        0.30 * functional
        + 0.15 * evidence_coverage
        + 0.15 * test_rate
        + 0.10 * property_rate
        + 0.10 * claim_consistency
        + 0.10 * robustness
        + 0.10 * code_quality
    ) * 100

    # =========================================================
    # FINAL VERDICT
    # =========================================================

    verdict = (
        "PASS"
        if (
            functional == 1.0
            and evidence_coverage == 1.0
            and not has_blocking_failure
            and not has_verification_blocker
        )
        else "FAIL"
    )

    # =========================================================
    # HUMAN REVIEW
    # =========================================================

    human_review_required = (
        bool(findings)
        or evidence_coverage < 1
    )

    # =========================================================
    # CONFIDENCE
    # =========================================================

    if (
        execution.executed
        and not has_verification_blocker
    ):
        confidence = (
            0.97
            if not findings
            else 0.90
        )
    else:
        confidence = 0.60

    # =========================================================
    # RESULT
    # =========================================================

    return {
        "score": round(
            total,
            2,
        ),

        "verdict": verdict,

        "claim_consistency": round(
            claim_consistency,
            3,
        ),

        "requirement_coverage": round(
            evidence_coverage,
            3,
        ),

        "evidence_coverage": round(
            evidence_coverage,
            3,
        ),

        "test_pass_rate": round(
            test_rate,
            3,
        ),

        "property_pass_rate": round(
            property_rate,
            3,
        ),

        "functional_correctness": round(
            functional,
            3,
        ),

        "robustness": round(
            robustness,
            3,
        ),

        "code_quality": round(
            code_quality,
            3,
        ),

        "human_review_required": (
            human_review_required
        ),

        "confidence": confidence,
    }