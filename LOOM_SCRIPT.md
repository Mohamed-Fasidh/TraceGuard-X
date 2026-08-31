# TraceGuard X — 5 Minute Loom

## 0:00–0:30 — Problem
"An AI coding agent can report success even when its implementation fails. TraceGuard X turns that claim into a verification problem."

Show a false-success trajectory.

## 0:30–1:00 — Baseline
Run the baseline.

"The baseline trusts the agent narrative. This is our control."

Show its verdict.

## 1:00–2:00 — Agentic pipeline
Show:

Trace Analyst
→ Requirement Graph
→ Verification Planner
→ Adversarial Verifier
→ Static Analysis
→ Sandbox
→ Property Check
→ Evidence Reconciliation
→ Score

"Verification has a budget. The system prioritizes high-value edge cases instead of generating unlimited tests."

## 2:00–3:00 — Evidence graph
Open the evidence graph.

"Every important conclusion is connected to a claim, a verification step, and observed evidence."

Show a contradiction:
CLAIM = PASS
OBSERVED = failure.

## 3:00–3:40 — Mutation testing
Show mutation report.

"We also test the evaluator itself. We introduce realistic bugs and measure whether TraceGuard kills those mutations."

## 3:40–4:20 — Benchmark
Show `artifacts/comparison.json`.

"These are the actual generated results on the same benchmark. We never hard-code improvement numbers."

## 4:20–4:40 — Changelog
"The biggest improvement was independent evidence. We also removed an LLM judge debate experiment because its cost and complexity outweighed its measured benefit."

## 4:40–5:00 — Close
"TraceGuard X does not ask whether the agent sounds convincing. It asks what can be proven. The final output gives reviewers the claim, evidence, contradiction, score, confidence and human-review trigger."
