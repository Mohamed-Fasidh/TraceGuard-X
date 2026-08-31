
# Competition Provenance

## What was known before kickoff
The public handbook established:
- two distinct versions: baseline and advanced;
- meaningful improvement;
- reproducibility;
- an improvement changelog;
- a reproduction guide;
- a solution video up to five minutes;
- representative agent trajectories;
- sandbox/human-approval requirements for consequential actions.

## What this submission adds
TraceGuard X implements an evidence-first evaluator with:
- requirement graph;
- bounded verification planning;
- adversarial verification;
- static analysis;
- independent sandbox execution;
- property checks;
- evidence graph;
- claim/evidence reconciliation;
- deterministic scoring;
- evaluator mutation testing;
- targeted human-review gate.

## Critical boundary
The official challenge materials available in this workspace describe the framework and submission requirements, but they do not contain a distinct final problem specification/starter repository/acceptance-test suite for a different target problem. Therefore this package must not claim that it satisfies undisclosed acceptance tests.

If the official kickoff package contains additional required APIs, starter files, runtime limits or acceptance tests, those must be copied into the benchmark and integrated before final submission.

## Integrity rule
No performance number is considered a final competition result until it is produced by the supplied benchmark scripts on the same benchmark for baseline and advanced versions.
