import argparse
import json
from pathlib import Path

from src.traceguard.agents.trace_analyst import analyze
from src.traceguard.agents.verification_planner import plan
from src.traceguard.agents.requirements import build_requirement_graph
from src.traceguard.agents.adversarial_verifier import generate_cases
from src.traceguard.tools.static_analyzer import analyze as static_analyze
from src.traceguard.tools.sandbox import run_sandbox
from src.traceguard.tools.reconcile import reconcile
from src.traceguard.scoring.scorer import score
from src.traceguard.evidence_graph import build_evidence_graph
from src.traceguard.agent_runtime import AgentRuntime
from src.traceguard.llm_provider import LLMProvider


def evaluate_one(raw):

    # =========================================================
    # 1. TRACE ANALYSIS
    # =========================================================

    trace = analyze(raw)

    runtime = AgentRuntime(
        trace.trace_id
    )

    provider = LLMProvider()

    runtime.run_agent(
        "trace_analyst",
        "extract_claims",
        "Normalize the trajectory before any verification.",
        {
            "claimed_verdict": trace.claimed_verdict,
            "claimed_tests": trace.claimed_tests,
        },
        lambda _: {
            "claims_extracted": True,
            "claim": trace.claimed_verdict,
            "claimed_tests": trace.claimed_tests,
        },
        feedback=(
            "Claims are treated as hypotheses, not proof."
        ),
    )

    # =========================================================
    # 2. REQUIREMENTS
    # =========================================================

    requirements = build_requirement_graph(
        trace
    )

    runtime.run_agent(
        "requirement_agent",
        "build_requirement_graph",
        "Convert requirements into independently verifiable targets.",
        {
            "requirements": trace.requirements,
        },
        lambda _: {
            "requirement_count": len(
                requirements
            ),
            "requirements": [
                {
                    "id": r.requirement_id,
                    "text": r.text,
                    "priority": r.verification_priority,
                }
                for r in requirements
            ],
        },
        feedback=(
            "Deterministic or executable checks are preferred."
        ),
    )

    # =========================================================
    # 3. VERIFICATION PLAN
    # =========================================================

    verification_plan = plan(
        trace
    )

    runtime.run_agent(
        "verification_planner",
        "create_verification_plan",
        (
            "Plan checks that do not depend solely "
            "on the agent's reported tests."
        ),
        {
            "requirements": trace.requirements,
        },
        lambda _: {
            "verification_plan": verification_plan
        },
        feedback=(
            "Independent evidence will outrank narrative claims."
        ),
    )

    # =========================================================
    # 4. ADVERSARIAL CASE GENERATION
    # =========================================================

    adversarial_cases = generate_cases(
        trace,
        budget=8,
    )

    runtime.run_agent(
        "adversarial_verifier",
        "generate_adversarial_cases",
        (
            "Attempt to falsify the implementation "
            "within a fixed verification budget."
        ),
        {
            "budget": 8
        },
        lambda _: {
            "adversarial_budget": len(
                adversarial_cases
            ),
            "adversarial_cases": [
                {
                    "id": c.case_id,
                    "rationale": c.rationale,
                    "input": c.input_value,
                    "expected": getattr(
                        c,
                        "expected_output",
                        None,
                    ),
                }
                for c in adversarial_cases
            ],
        },
        feedback=(
            "High-value counterexamples are prioritized."
        ),
    )

    # =========================================================
    # 5. STATIC ANALYSIS
    # =========================================================

    static = static_analyze(
        trace.code
    )

    runtime.run_agent(
        "static_analyzer",
        "compile_candidate",
        (
            "Catch syntax/compilation failures "
            "before execution."
        ),
        {},
        lambda _: {
            "syntax_ok": static.syntax_ok,
            "compile_error": static.compile_error,
        },
        feedback=(
            "Static failure prevents unsafe execution."
        ),
        retry=not static.syntax_ok,
    )

    # =========================================================
    # 6. DECLARED TEST CASES
    # =========================================================

    declared_cases = list(
        trace.test_cases
    )

    # =========================================================
    # 7. EXECUTABLE ADVERSARIAL CASES
    # =========================================================

    executable_adversarial_cases = []

    for case in adversarial_cases:

        expected_output = getattr(
            case,
            "expected_output",
            None,
        )

        if expected_output is None:
            continue

        executable_adversarial_cases.append(
            {
                "input": case.input_value,
                "expected": expected_output,
            }
        )

    # =========================================================
    # 8. FINAL VERIFICATION SET
    # =========================================================

    verification_cases = (
        declared_cases
        + executable_adversarial_cases
    )

    # =========================================================
    # 9. DOCKER SANDBOX
    # =========================================================

    if static.syntax_ok:

        execution = run_sandbox(
            trace.code,
            test_cases=verification_cases,
        )

    else:

        from src.traceguard.schemas import ExecutionEvidence

        execution = ExecutionEvidence(
            executed=False,
            stderr=(
                "Skipped after static compilation failure."
            ),
        )

    # =========================================================
    # 10. EXECUTION AGENT
    # =========================================================

    runtime.run_agent(
        "execution_agent",
        "execute_in_sandbox",
        (
            "Generate evidence independently "
            "of the agent trajectory."
        ),
        {
            "sandbox": "docker",
            "network": "none",
        },
        lambda _: {
            "executed": execution.executed,
            "exit_code": execution.exit_code,
            "tests_passed": execution.tests_passed,
            "tests_total": execution.tests_total,
            "property_passed": execution.property_passed,
        },
        feedback=(
            "Execution evidence is immutable input to reconciliation."
        ),
    )

    # =========================================================
    # 11. RECONCILIATION
    # =========================================================

    findings = reconcile(
        trace,
        static,
        execution,
    )

    contradiction = any(
        finding["category"]
        == "claim_evidence_contradiction"
        for finding in findings
    )

    runtime.run_agent(
        "auditor",
        "reconcile_evidence",
        (
            "Determine whether claims agree with "
            "independently generated evidence."
        ),
        {
            "findings": findings,
        },
        lambda _: {
            "finding_count": len(
                findings
            ),
            "contradiction": contradiction,
            "human_review": bool(
                findings
            ),
        },
        feedback=(
            "Claim contradicted by independent evidence."
            if contradiction
            else
            "No claim/evidence contradiction detected."
        ),
        human_checkpoint=bool(
            findings
        ),
    )

    # =========================================================
    # 12. EVIDENCE COVERAGE
    # =========================================================

    if not execution.executed:

        evidence_coverage = 0.0

    elif not verification_cases:

        evidence_coverage = 1.0

    else:

        evidence_coverage = (
            1.0
            if (
                execution.tests_total
                == len(verification_cases)
            )
            else 0.0
        )

    # =========================================================
    # 13. SCORE
    # =========================================================

    scored = score(
        trace,
        static,
        execution,
        findings,
         property_evidence={
        "passed": execution.property_passed
    },
        evidence_coverage=evidence_coverage,
    )

    # =========================================================
    # 14. EVIDENCE GRAPH
    # =========================================================

    graph = build_evidence_graph(
        trace,
        verification_plan,
        static,
        execution,
        findings,
    )

    # =========================================================
    # 15. RESULT
    # =========================================================

    return {
        "trace_id": trace.trace_id,

        "llm_provider": provider.status(),

        "agent_runtime": runtime.to_dict(),

        "requirements": [
            {
                "id": r.requirement_id,
                "text": r.text,
                "priority": r.verification_priority,
            }
            for r in requirements
        ],

        "verification_plan": verification_plan,

        "declared_test_count": len(
            declared_cases
        ),

        "adversarial_budget": len(
            adversarial_cases
        ),

        "adversarial_executable_count": len(
            executable_adversarial_cases
        ),

        "verification_case_count": len(
            verification_cases
        ),

        "adversarial_cases": [
            {
                "id": c.case_id,
                "rationale": c.rationale,
                "input": c.input_value,
                "expected": getattr(
                    c,
                    "expected_output",
                    None,
                ),
                "executed": (
                    getattr(
                        c,
                        "expected_output",
                        None,
                    )
                    is not None
                ),
            }
            for c in adversarial_cases
        ],

        **scored,

        "static_evidence": (
            static.model_dump()
        ),

        "execution": (
            execution.model_dump()
        ),

        "findings": findings,

        "evidence_graph": graph,
    }


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--data",
        required=True,
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    args = parser.parse_args()

    data_path = Path(
        args.data
    )

    output_path = Path(
        args.output
    )

    trace_files = sorted(
        data_path.glob("*.json")
    )

    results = []

    for path in trace_files:

        raw = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        results.append(
            evaluate_one(raw)
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            results,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "traces": len(results),
                "output": str(
                    output_path
                ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()