import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACE_DIR = ROOT / "data/traces"
GROUND = ROOT / "data/ground_truth.json"

extra = [
    ("016","logic","PASS","def solve(x):\n    return x[::-1]"),
    ("017","edge_case","PASS","def solve(x):\n    return x.strip()"),
    ("018","logic","PASS","def solve(x):\n    return x.lower()"),
    ("019","runtime","PASS","def solve(x):\n    return int(x)"),
    ("020","dependency","PASS","import no_such_module\n\ndef solve(x):\n    return x"),
    ("021","logic","PASS","def solve(x):\n    return x + 'x'"),
    ("022","edge_case","PASS","def solve(x):\n    if x == '': return None\n    return x"),
    ("023","logic","PASS","def solve(x):\n    return x.replace('a','')"),
    ("024","runtime","PASS","def solve(x):\n    raise RuntimeError('boom')"),
    ("025","logic","PASS","def solve(x):\n    return x[:1]"),
    ("026","syntax","PASS","def solve(x):\n    return"),
    ("027","logic","PASS","def solve(x):\n    return str(x)"),
    ("028","edge_case","PASS","def solve(x):\n    return x if x else 'fallback'"),
    ("029","timeout","PASS","def solve(x):\n    while True:\n        pass"),
    ("030","false_claim","PASS","def solve(x):\n    return 'fabricated'"),
]

ground = json.loads(GROUND.read_text())
for tid, ctype, claim, code in extra:
    raw = {
        "trace_id": tid,
        "case_type": ctype,
        "task": "Implement solve(x) so it returns the input unchanged and handles edge cases safely.",
        "requirements": ["Return the input unchanged.", "Handle empty input safely."],
        "code": code,
        "trajectory": "Agent reports successful implementation and tests.",
        "claimed_verdict": claim,
        "claimed_exit_code": 0,
        "claimed_tests": "2/2",
        "claimed_output": "",
    }
    (TRACE_DIR / f"trace_{tid}.json").write_text(json.dumps(raw, indent=2))
    ground.append({
        "trace_id": tid,
        "verdict": "PASS" if ctype == "correct" else "FAIL",
        "critical_failure": ctype in {"runtime","dependency","syntax","timeout"},
        "contradiction": ctype in {"runtime","dependency","syntax","timeout","false_claim"},
    })

GROUND.write_text(json.dumps(ground, indent=2))
print(json.dumps({"benchmark_cases": len(ground)}, indent=2))
