
# Experiment V2 — Docker benchmark

Source: user-provided Windows + Docker execution log.

Benchmark cases: 15

| Metric | Result |
|---|---:|
| Baseline verdict accuracy | 33.33% |
| Advanced verdict accuracy | 66.67% |
| Absolute improvement | +33.33 percentage points |
| Relative improvement | +100% |
| Critical failure precision | 33.33% |
| Critical failure recall | 100% |
| Claim/evidence contradiction detection | 14.29% |

Decision:
KEEP the evidence-first architecture, but do not use these numbers as the final
competition result. They exposed a precision/contradiction-model weakness.

Next hypothesis:
Separate candidate failure from claim contradiction, expand the benchmark,
and evaluate the evaluator with mutation testing.
