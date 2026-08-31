# TraceGuard X — Agent Use Disclosure

## Coding-Agent Use

Coding-agent assistance was used during development of TraceGuard X.

**Coding agent used:** OpenAI ChatGPT

The coding agent was used to assist with implementation, debugging, test
execution, documentation, evaluation workflow development, and iterative
refinement.

## Agent Roles in the Final Workflow

The final TraceGuard X verification workflow uses the following
specialized stages:

1. **Trace Analyst** — normalizes the coding-agent trajectory and
   extracts claims and candidate code.

2. **Requirement Agent** — converts requirements into explicit
   verification targets.

3. **Verification Planner** — creates a bounded verification plan.

4. **Adversarial Verifier** — selects high-value edge and adversarial
   cases within the verification budget.

5. **Static Analyzer** — performs deterministic syntax/static
   validation before execution.

6. **Execution Agent** — runs candidate code independently inside the
   Docker sandbox.

7. **Auditor** — reconciles claims with independent evidence and
   determines whether human review is required.

### Agent Design Philosophy

TraceGuard X deliberately does not use an LLM as the final authority on
correctness.

Agents are used for interpretation, requirement analysis, verification
planning, and bounded adversarial reasoning. Deterministic components are
used for static analysis, sandbox execution, evidence reconciliation, and
final scoring because these stages require reproducible and independently
verifiable evidence.

This separation is intentional: agent reasoning helps determine what should
be verified, while deterministic verification determines what the evidence
actually shows.

## Trajectory Evidence

Representative trajectories for every agent are included under:

```text
trajectories/

├── trace_analyst.jsonl
├── requirement_agent.jsonl
├── verification_planner.jsonl
├── adversarial_verifier.jsonl
├── static_analyzer.jsonl
├── execution_agent.jsonl
└── auditor.jsonl
```

The trajectory files are generated from the recorded
`agent_runtime.events` produced by the advanced evaluation run.

They contain structured evidence such as:

- agent actions;
- inputs and outputs;
- reasons for actions;
- tool responses;
- feedback;
- retries;
- human checkpoints.

The trajectory artifacts can be regenerated with:

```bash
python scripts/export_trajectories.py
```

## Independence of Verification

The coding agent's claims are **not treated as independent proof of
correctness**.

TraceGuard X separates:

```text
Agent claim
    ↓
Requirement target
    ↓
Independent verification
    ↓
Observed evidence
    ↓
Claim/evidence reconciliation
    ↓
Deterministic scoring
    ↓
Human review when evidence is insufficient
```

Execution results are produced independently inside the Docker sandbox.

Hard verification decisions are based on observed execution and
deterministic checks rather than allowing an agent narrative to override
contradictory evidence.

## Benchmark Disclosure

The final V3 benchmark contains 40 synthetic cases. Baseline and
advanced evaluation use the same benchmark files.

Generated benchmark and validation artifacts include:

```text
artifacts/baseline_results.json
artifacts/advanced_results.json
artifacts/comparison.json
artifacts/benchmark_validation.json
artifacts/mutation_report.json
artifacts/preflight.json
artifacts/evaluator_challenge.json
```

No benchmark percentages are manually inserted into these generated
artifacts.

### Benchmark Validation Metric

The synthetic executor validation and final TraceGuard X verdict accuracy
measure different things.

The synthetic executor validation reports 95% validation accuracy for the
benchmark execution fixture.

The final TraceGuard X comparison reports 100% verdict accuracy across the
40-case benchmark after the complete evidence-reconciliation pipeline.

The two metrics are therefore retained and reported separately rather than
being conflated.

## Data and Credentials

The included benchmark data is synthetic.

No real credentials, API keys, passwords, or private user information
are included in the submission.

Environment secrets such as `.env` files are excluded from the
submission.

## Development Assistance vs. Evaluation Evidence

Coding-agent assistance during development should not be confused with
the evidence used to evaluate TraceGuard X.

Development assistance helped build and refine the system. The final
benchmark evaluation is performed by the submitted evaluation
pipeline using the fixed benchmark, deterministic checks, property
verification, and independent Docker execution. Agent-generated
interpretation and planning are treated as inputs to the verification
workflow rather than authoritative correctness evidence.

## Disclosure Summary

TraceGuard X was developed with coding-agent assistance, and that use is
explicitly disclosed here. The submitted trajectory artifacts provide
inspectable evidence of the specialized agents used by the final
verification workflow.

The central design principle is that **agent-generated claims are
evidence candidates, not proof**. Independent verification remains the
basis for the final evaluation decision.
