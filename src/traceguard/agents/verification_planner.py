def plan(trace):
    text = (trace.task + " " + " ".join(trace.requirements)).lower()
    checks = ["python -m py_compile candidate.py"]
    if "empty" in text or "missing" in text:
        checks.append("edge-case: empty/missing input")
    if "nested" in text:
        checks.append("edge-case: missing nested object")
    if "status" in text:
        checks.append("edge-case: missing status")
    if len(checks) == 1:
        checks.append("behavior: representative input")
    return checks
