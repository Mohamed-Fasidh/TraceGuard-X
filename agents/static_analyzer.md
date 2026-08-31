
---

# 2. `agents/static_analyzer.md`

```markdown
# Static Analyzer Agent

## Purpose

Perform static validation of candidate code before it is executed in the
independent sandbox.

The static-analysis stage is an early safety and correctness gate.

## Input

The agent receives the candidate implementation extracted from the trajectory.

Example:

```python
def solve(x):
    return x.strip() if isinstance(x, str) else x