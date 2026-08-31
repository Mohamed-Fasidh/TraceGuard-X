# TraceGuard X Architecture

## Design principles

1. **Evidence before persuasion** — claims do not count as proof.
2. **Strongest available oracle** — deterministic checks beat qualitative judgment when available.
3. **Bounded agency** — verification agents have explicit budgets and timeouts.
4. **Independent execution** — candidate code runs outside the agent's narrative.
5. **Auditable decisions** — verdicts are connected to evidence.
6. **Human escalation** — ambiguity becomes review, not fabricated certainty.
7. **Evaluator testing** — mutation testing measures whether the evaluator can detect realistic faults.

## Agent roles

### Trace Analyst
Normalizes the trajectory and extracts claims.

### Requirement Analyst
Builds a requirement graph and assigns verification priority.

### Verification Planner
Turns requirements into concrete checks.

### Adversarial Verifier
Attempts to break the candidate using a bounded test budget.

### Execution Tool
Runs candidate code inside a restricted Docker sandbox.

### Evidence Reconciler
Compares claims with independently observed evidence.

### Auditor
Produces an explainable result and decides whether human review is needed.

## Why not one giant agent?

A single agent has correlated failure modes. Separating planning, execution and reconciliation creates an opportunity for one component to falsify another component's claims.

## Trust boundary

```text
UNTRUSTED
Candidate code
Agent narrative
Agent-reported test results
        |
        v
--------------------------------
Verification boundary
--------------------------------
        |
        v
TRUSTEDER EVIDENCE
Static result
Sandbox exit code
Observed output
Deterministic assertions
        |
        v
Decision
```

No component is treated as infallible. Human review remains available for ambiguity.
