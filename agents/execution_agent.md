
---

# 3. `agents/execution_agent.md`

```markdown
# Execution Agent

## Purpose

Generate independent execution evidence for candidate implementations.

The execution stage is the primary separation between what the coding agent
claims and what TraceGuard can independently observe.

## Input

The execution stage receives:

- candidate code;
- declared verification cases;
- adversarial verification cases with executable expected outputs when available.

## Responsibilities

The execution agent:

1. Executes candidate code in the sandbox.
2. Uses the independent verification cases prepared by TraceGuard.
3. Records exit status.
4. Records standard output and standard error.
5. Records timeout information.
6. Records test pass/fail counts.
7. Records observed outputs.
8. Provides execution evidence to the reconciliation stage.

## Sandbox

Candidate code is treated as untrusted.

The execution environment is configured with isolation controls including:

- Docker execution;
- disabled network access;
- read-only filesystem where supported;
- dropped Linux capabilities;
- `no-new-privileges`;
- CPU limits;
- memory limits;
- process limits;
- execution timeout;
- disposable execution workspace.

Docker is treated as a practical containment boundary rather than a formal
security proof.

## Output

The execution stage produces structured evidence such as:

```json
{
  "executed": true,
  "exit_code": 0,
  "tests_passed": 11,
  "tests_total": 14,
  "property_passed": false
}