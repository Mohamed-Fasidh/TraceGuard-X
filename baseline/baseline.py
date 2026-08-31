import argparse, json
from pathlib import Path

def evaluate(raw):
    claim = raw.get("claimed_verdict", "").upper()
    text = raw.get("trajectory", "").lower()
    if claim in {"PASS", "SUCCESS", "SOLVED", "OK"} or "tests passed" in text:
        return {"trace_id": raw["trace_id"], "score": 85.0, "verdict": "PASS", "human_review_required": False}
    if claim in {"FAIL", "FAILED", "ERROR"}:
        return {"trace_id": raw["trace_id"], "score": 25.0, "verdict": "FAIL", "human_review_required": False}
    return {"trace_id": raw["trace_id"], "score": 50.0, "verdict": "REVIEW", "human_review_required": True}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    results = [evaluate(json.loads(x.read_text())) for x in sorted(Path(a.data).glob("*.json"))]
    Path(a.output).parent.mkdir(parents=True, exist_ok=True)
    Path(a.output).write_text(json.dumps(results, indent=2))
    print(json.dumps({"traces": len(results), "output": a.output}, indent=2))

if __name__ == "__main__":
    main()
