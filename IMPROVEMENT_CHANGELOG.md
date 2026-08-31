# Improvement Changelog

## 0 — Baseline
**Hypothesis:** A single evaluator can judge a coding-agent trajectory from its narrative.

**Evidence:** This control condition has no independent execution evidence.

**Decision:** Keep as the baseline.

## 1 — Trace normalization
**Hypothesis:** Structured fields make claims auditable.

**Evidence:** Verdict, test claims, output claims and code can be compared consistently.

**Decision:** Keep.

## 2 — Static verification
**Hypothesis:** Syntax/compilation checks cheaply catch obvious failures.

**Evidence:** Broken code can be rejected before sandbox execution.

**Decision:** Keep.

## 3 — Independent sandbox
**Hypothesis:** Independent execution catches false success narratives.

**Evidence:** Runtime-error and output-mismatch cases produce evidence independent of the agent's report.

**Decision:** Keep. This is the most important improvement.

## 4 — Claim/evidence reconciliation
**Hypothesis:** Contradictions should be explicit, not buried in prose.

**Evidence:** Reported success can be directly compared with observed exit codes, test counts and output.

**Decision:** Keep.

## 5 — Deterministic scoring
**Hypothesis:** Numeric scoring should be reproducible.

**Evidence:** Scores are calculated from observable dimensions rather than generated freely by a model.

**Decision:** Keep.

## 6 — Verification planning
**Hypothesis:** Running only claimed tests is insufficient.

**Evidence:** Requirements and edge-case patterns generate additional checks.

**Decision:** Keep.

## Removed experiment — LLM judge debate
**Hypothesis:** Two model judges debating every case would improve reliability.

**Observed tradeoff:** More latency, cost and complexity without enough measured benefit.

**Decision:** Remove.

**Lesson:** More model reasoning is not automatically more reliable; independent evidence was more valuable.
