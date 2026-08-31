
# TraceGuard X — Competition Edition V3 Checklist

## Required implementation
- [x] Baseline
- [x] Advanced multi-stage verification pipeline
- [x] Requirement graph
- [x] Bounded adversarial verifier
- [x] Static analysis
- [x] Secure Docker sandbox
- [x] Property verification
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
- [ ] V3 Docker baseline result generated
- [ ] V3 Docker advanced result generated
- [ ] V3 comparison artifact generated

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
Never claim the V3 benchmark is complete until `artifacts/comparison.json`
has been generated from the V3 Docker run.
