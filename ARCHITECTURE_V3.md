# TraceGuard X V3

## Trust model

```text
Agent claim ──────┐
                  │
Requirement ──────┼──> Verification Plan
                  │           │
                  │           ├── Static Analysis
                  │           ├── Adversarial Tests
                  │           └── Docker Execution
                  │
                  └──────────────> Evidence
                                     │
                                     ▼
                              Reconciliation
                                     │
                                     ▼
                               Auditor Agent
                                     │
                           ┌─────────┴─────────┐
                           ▼                   ▼
                         PASS                REVIEW
```

## Key principle

No language-model-generated claim can override deterministic execution evidence.

## Agent handoff protocol

Every handoff contains:
- input facts;
- action;
- rationale;
- output;
- feedback;
- retry flag;
- human checkpoint flag.

This makes the trajectory inspectable rather than a black-box transcript.

## Security boundary

Candidate code is mounted read-only into a disposable container with:
- no network;
- read-only root filesystem;
- all Linux capabilities dropped;
- no-new-privileges;
- CPU limit;
- memory limit;
- process limit;
- non-executable temporary filesystem.

This is a competition-grade containment approach, not a formal proof of multi-tenant isolation.
