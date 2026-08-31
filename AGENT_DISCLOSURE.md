# TraceGuard X — Agent Use Disclosure

## Overview

TraceGuard X uses a staged, inspectable evaluation workflow.

The system separates:

1. what the coding agent claims;
2. what TraceGuard independently verifies;
3. what evidence is produced;
4. how that evidence is reconciled and scored.

Coding-agent assistance was used during development of the project.

Representative agent-stage records are stored under:

```text
trajectories/
```

These records make the evaluator workflow inspectable.

---

## Agent Pipeline

The advanced evaluator uses the following stages:

```text
Trace
  ↓
Trace Analyst
  ↓
Requirement Agent
  ↓
Verification Planner
  ↓
Adversarial Verifier
  ↓
Static Analyzer
  ↓
Independent Execution Agent
  ↓
Auditor
  ↓
Deterministic Scoring
```

Each stage has a specific responsibility and produces structured information
for the next stage.

---

## 1. Trace Analyst

### Purpose

Extract and normalize information contained in the coding-agent trajectory.

### Responsibilities

- identify the claimed verdict;
- extract claimed test counts;
- extract claimed exit codes;
- extract claimed output;
- extract candidate code;
- preserve original trace information.

### Evidence Principle

The Trace Analyst records claims but does not treat those claims as proof of
correctness.

### Instruction

```text
agents/trace_analyst.md
```

### Trajectory

```text
trajectories/trace_analyst.jsonl
```

---

## 2. Requirement Agent

### Purpose

Convert declared requirements into explicit verification targets.

### Responsibilities

- identify individual requirements;
- make requirements inspectable;
- assign verification priorities;
- preserve the intended meaning of the requirement.

### Evidence Principle

A requirement describes what must be satisfied. It does not prove that the
candidate implementation satisfies it.

### Instruction

```text
agents/requirement_agent.md
```

### Trajectory

```text
trajectories/requirement_agent.jsonl
```

---

## 3. Verification Planner

### Purpose

Create a verification plan from the trace and requirements.

### Responsibilities

- select verification strategies;
- identify relevant test cases;
- determine static-analysis requirements;
- determine independent execution requirements;
- identify useful adversarial checks.

### Evidence Principle

The verification plan must be independent of the candidate's claimed success.

### Instruction

```text
agents/verification_planner.md
```

### Trajectory

```text
trajectories/verification_planner.jsonl
```

---

## 4. Adversarial Verifier

### Purpose

Generate bounded high-value adversarial cases intended to expose weaknesses
in candidate implementations.

### Responsibilities

- generate boundary cases;
- generate representative edge cases;
- prioritize requirement-relevant failure modes;
- deduplicate candidates;
- enforce an explicit verification budget.

### Verification Budget

The adversarial verifier operates under a fixed case budget to avoid
unbounded test generation.

### Evidence Principle

Adversarial cases provide additional independent evidence. They do not replace
the benchmark ground truth.

### Instruction

```text
agents/adversarial_verifier.md
```

### Trajectory

```text
trajectories/adversarial_verifier.jsonl
```

---

## 5. Static Analyzer

### Purpose

Check candidate code before independent execution.

### Responsibilities

- validate syntax/compilation;
- capture compilation errors;
- produce structured static evidence;
- prevent invalid code from being treated as executable evidence.

### Evidence Principle

Static evidence is independent of the coding agent's execution narrative.

### Instruction

```text
agents/static_analyzer.md
```

### Trajectory

```text
trajectories/static_analyzer.jsonl
```

---

## 6. Execution Agent

### Purpose

Generate independent runtime evidence by executing candidate code inside
the sandbox.

### Responsibilities

- execute candidate code;
- run independent verification cases;
- capture exit code;
- capture stdout/stderr;
- detect timeouts;
- record test pass/fail counts;
- record observed outputs.

### Sandbox

Candidate code is treated as untrusted.

The execution environment uses Docker isolation and resource controls
including:

- network isolation;
- read-only filesystem where configured;
- dropped capabilities;
- `no-new-privileges`;
- CPU limits;
- memory limits;
- process limits;
- execution timeout;
- disposable workspace.

Docker is a practical containment boundary and is not claimed to be a formal
security proof.

### Evidence Principle

Independent execution evidence takes precedence over candidate narrative
claims.

### Instruction

```text
agents/execution_agent.md
```

### Trajectory

```text
trajectories/execution_agent.jsonl
```

---

## 7. Auditor

### Purpose

Reconcile independent evidence with the coding agent's claims and determine
whether human review is appropriate.

### Responsibilities

- inspect findings;
- identify claim/evidence contradictions;
- distinguish candidate failures from infrastructure failures;
- identify verification gaps;
- recommend human review when evidence is incomplete or ambiguous.

### Evidence Principle

The auditor cannot override hard execution evidence.

### Instruction

```text
agents/auditor.md
```

### Trajectory

```text
trajectories/auditor.jsonl
```

---

# Agent Runtime

TraceGuard records the staged workflow using:

```text
src/traceguard/agent_runtime.py
```

The runtime records structured events containing:

- step;
- agent;
- action;
- reason;
- input;
- output;
- feedback;
- retry status;
- human-checkpoint status.

This provides an auditable representation of the evaluator's agentic workflow.

---

# Evidence Hierarchy

TraceGuard follows an evidence-first hierarchy:

```text
Independent execution evidence
        ↓
Static evidence
        ↓
Verification findings
        ↓
Agent claims / trajectory narrative
```

Agent claims are preserved for comparison but cannot override contradictory
independent evidence.

Example:

```text
Agent claim:
PASS — 6/6 tests passed

Independent evidence:
Behavior mismatch detected

Result:
FAIL + claim/evidence contradiction
```

---

# Human Review

TraceGuard does not attempt to make every ambiguous case automatically
conclusive.

Human review may be recommended when:

- independent execution is unavailable;
- verification evidence is incomplete;
- infrastructure failure prevents verification;
- evidence conflicts with the available claim;
- the requirement cannot be completely verified.

The human-review recommendation is an evidence-based escalation mechanism.

It is not a consequential automated decision.

---

# Development Disclosure

Coding-agent assistance was used during development for implementation,
debugging, documentation and iteration.

The evaluator itself is designed to prevent the coding agent's own claims
from being treated as independent verification evidence.

The final benchmark results are generated by the deterministic evaluation
pipeline and are stored in:

```text
artifacts/baseline_results.json
artifacts/advanced_results.json
artifacts/comparison.json
```

---

# Reproducibility

The benchmark is synthetic and version-controlled.

The final V3 benchmark contains:

```text
40 cases
```

Both baseline and advanced systems consume the same trace dataset.

The benchmark and generated results can be reproduced using the commands in:

```text
REPRODUCTION.md
```

---

# Trajectory Inventory

The final representative trajectory directory should contain:

```text
trajectories/
├── trace_analyst.jsonl
├── requirement_agent.jsonl
├── verification_planner.jsonl
├── adversarial_verifier.jsonl
├── static_analyzer.jsonl
├── execution_agent.jsonl
└── auditor.jsonl
```

Each trajectory corresponds to a stage in the advanced evaluation workflow.

---

# Important Integrity Statement

TraceGuard does not claim that an agent's reported success is correct merely
because the agent reported successful execution.

The central design principle is:

> Claims are recorded. Evidence is independently generated. Findings are
> reconciled deterministically.

Final benchmark metrics must be taken from generated artifacts and must not be
manually fabricated.
