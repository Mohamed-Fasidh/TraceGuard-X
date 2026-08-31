# TraceGuard X — Competition Edition V3 Checklist

## Required implementation

- [x] Baseline
- [x] Advanced multi-stage verification pipeline
- [x] Requirement graph
- [x] Bounded adversarial verifier
- [x] Static analysis
- [x] Secure Docker sandbox
- [x] Property verification infrastructure
- [x] Evidence graph
- [x] Claim/evidence reconciliation
- [x] Deterministic scoring
- [x] Human-review gate
- [x] Mutation testing
- [x] Evaluator self-challenge

## Benchmark

- [x] 40 fixed cases
- [x] Fixed seed documented
- [x] Same cases for baseline/advanced
- [x] Ground truth included
- [x] Benchmark manifest included

## Measurement

- [x] Precision/recall/F1
- [x] Confusion matrix
- [x] Mutation detection metric
- [x] Prior experiment preserved
- [x] V3 Docker baseline result generated
- [x] V3 Docker advanced result generated
- [x] V3 comparison artifact generated

## Final presentation

- [x] Architecture document
- [x] Changelog
- [x] Reproduction guide
- [x] Agent instructions
- [x] Agent disclosure
- [x] Security documentation
- [x] Loom script
- [ ] Record final ≤5-minute video using actual V3 metrics

## Integrity

The V3 benchmark was executed using the fixed 40-case dataset.

Generated benchmark evidence is stored in:

- `artifacts/baseline_results.json`
- `artifacts/advanced_results.json`
- `artifacts/comparison.json`
- `artifacts/mutation_report.json`
- `artifacts/preflight.json`

The final benchmark metrics must always be taken from the generated artifacts
and must not be manually fabricated.

## Final V3 Result

- Benchmark cases: **40**
- Baseline verdict accuracy: **20.00%**
- Advanced verdict accuracy: **100.00%**
- Absolute improvement: **+80 percentage points**
- Advanced incorrect verdicts: **0**

## Qualification

- [x] Repository tests pass
- [x] Docker binary available
- [x] Docker daemon running
- [x] Comparison artifact validated
- [x] Mutation artifact validated
- [x] Preflight qualification passed

## Remaining Submission Task

- [ ] Record and submit the final ≤5-minute competition video

> Do not claim that hidden or official acceptance tests have passed unless those
> tests are provided and successfully executed.