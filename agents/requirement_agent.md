# Requirement Agent

## Purpose

Convert the requirements extracted from a coding-agent trajectory into explicit,
independently verifiable targets.

The requirement agent helps TraceGuard determine what the candidate implementation
must satisfy before execution evidence is evaluated.

## Input

The agent receives the requirements extracted from the trace.

Example:

```text
Implement solve(x) so that it returns the input unchanged for every supplied
test case.