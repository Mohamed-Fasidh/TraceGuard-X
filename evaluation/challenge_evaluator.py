import json
from pathlib import Path

def main():
    results = json.loads(Path("artifacts/advanced_results.json").read_text())
    questions = []
    for r in results:
        if r["human_review_required"]:
            questions.append({
                "trace_id": r["trace_id"],
                "question": "What evidence could invalidate the current verdict?",
                "answer": "Review the requirement oracle, sandbox output, and contradiction findings.",
                "status": "HUMAN_REVIEW"
            })
        else:
            questions.append({
                "trace_id": r["trace_id"],
                "question": "What evidence could invalidate the current verdict?",
                "answer": "No known counter-evidence in the deterministic verification set.",
                "status": "NO_COUNTER_EVIDENCE_FOUND"
            })

    Path("artifacts/evaluator_challenge.json").write_text(json.dumps(questions, indent=2))
    print(json.dumps({"cases": len(questions), "output": "artifacts/evaluator_challenge.json"}, indent=2))

if __name__ == "__main__":
    main()
