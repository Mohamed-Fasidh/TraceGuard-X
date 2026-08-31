# TraceGuard X — 5 Minute Loom

## 0:00–0:30 — Problem

"An AI coding agent can report success even when its implementation fails.

TraceGuard X turns that claim into an independent verification problem.

Instead of trusting what the agent says, we collect evidence about what the
implementation actually does."

### Show

Open a representative false-success trajectory, preferably `trace_011`.

Show:

```text
CLAIMED VERDICT: PASS
CLAIMED TESTS: 6/6
```

Then explain that TraceGuard independently verifies the candidate.

---

## 0:30–1:00 — Baseline

Run or open the baseline result.

"The baseline is intentionally simple. It primarily trusts the agent's
reported verdict and execution narrative.

This gives us a control system that we can compare against the evidence-first
advanced evaluator."

Show:

```text
artifacts/baseline_results.json
```

Then briefly show the generated baseline result.

---

## 1:00–2:00 — Advanced Agentic Verification Pipeline

Show the architecture:

```text
Trajectory
    ↓
Trace Analyst
    ↓
Requirement Graph
    ↓
Verification Planner
    ↓
Bounded Adversarial Verifier
    ↓
Static Analysis
    ↓
Independent Docker Sandbox
    ↓
Evidence Reconciliation
    ↓
Deterministic Scoring
    ↓
Human Review
```

"The advanced system separates the agent's claims from independently generated
evidence.

First, the Trace Analyst extracts the claims.

The Requirement Agent turns requirements into explicit verification targets.

The Verification Planner determines how those targets should be checked.

The bounded Adversarial Verifier adds high-value edge cases under an explicit
test budget.

Static Analysis checks the candidate before execution.

Then the candidate is executed independently inside the Docker sandbox.

Finally, TraceGuard reconciles the claims with the observed evidence and
produces a deterministic score and human-review recommendation."

### Important point

"Verification is bounded. The system does not generate unlimited tests.
Adversarial verification is constrained by an explicit budget."

---

## 2:00–3:00 — Evidence and Contradiction

Open the result for `trace_011`.

Show the agent claim:

```text
CLAIMED VERDICT = PASS
CLAIMED TESTS = 6/6
```

Then show the independent evidence and findings.

"This is the important part.

The agent claimed that the implementation passed.

But independent verification found a behavioral mismatch.

TraceGuard therefore records a claim/evidence contradiction instead of trusting
the narrative."

Show:

```text
behavior_failure
claim_evidence_contradiction
```

Then show:

```text
FINAL VERDICT = FAIL
HUMAN REVIEW = true
```

"The evaluator does not hide the contradiction. It preserves the claim,
the evidence, the finding and the resulting decision."

---

## 3:00–3:40 — Mutation Testing

Open:

```text
artifacts/mutation_report.json
```

"We also test TraceGuard itself.

Mutation testing introduces realistic faults into the evaluator and checks
whether our tests can detect those faults.

This gives us evidence about the strength of the evaluator rather than only
testing the candidates."

Show the generated mutation result.

Highlight:

```text
24 / 24 mutations killed
100% mutation detection rate
```

---

## 3:40–4:20 — Final V3 Benchmark

Open:

```text
artifacts/comparison.json
```

"Now we compare the baseline and advanced systems on the same fixed V3
benchmark.

The benchmark contains 40 synthetic cases.

These are the actual generated results. We do not manually type or fabricate
the percentages."

Show:

```text
Benchmark cases:       40
Baseline accuracy:     20.00%
Advanced accuracy:    100.00%
Improvement:          +80 percentage points
```

Then briefly show the secondary metrics:

```text
Critical failure detection
Precision: 100.00%
Recall:     81.25%
F1:        89.66%

Claim/evidence contradiction
Precision: 52.00%
Recall:    65.00%
F1:        57.78%
```

"The advanced evaluator correctly classified all 40 benchmark cases in this
generated V3 run."

---

## 4:20–4:40 — Changelog and Key Learning

Open:

```text
IMPROVEMENT_CHANGELOG.md
```

"The biggest improvement was moving from narrative trust to independent
evidence.

We also tested alternative evaluator approaches during development and removed
an LLM-judge debate experiment because its cost and complexity did not provide
enough measured benefit.

The result was a simpler and more inspectable architecture where deterministic
evidence has priority."

---

## 4:40–5:00 — Closing

Show the complete architecture one final time.

"TraceGuard X does not ask whether an AI coding agent sounds convincing.

It asks what can actually be verified.

The final result connects the agent's claim with independent evidence,
findings, score, confidence and a human-review trigger.

The core idea is simple:

Claims are recorded.

Evidence is independently generated.

Contradictions are surfaced.

And the final evaluation is deterministic and auditable."

End on:

```text
TraceGuard X

Evidence over narrative.
```

---

# Demo Files

Use these files during the video:

```text
artifacts/baseline_results.json
artifacts/advanced_results.json
artifacts/comparison.json
artifacts/mutation_report.json
artifacts/preflight.json
```

Recommended demonstration trace:

```text
data/traces/trace_011.json
```

If the filename differs in the local environment, use the corresponding
trace containing the false-success `PASS` claim and independent behavioral
failure.

---

# Final Video Integrity

Use only generated benchmark values from:

```text
artifacts/comparison.json
```

Do not manually fabricate benchmark metrics.

The final V3 benchmark result demonstrated in the video is:

```text
40 benchmark cases
Baseline accuracy: 20.00%
Advanced accuracy: 100.00%
Improvement: +80 percentage points
```

The video must remain within the competition's five-minute limit.
