
import json
from pathlib import Path
from src.traceguard.tools.benchmark_executor import run_synthetic

def main():
    ground = json.loads(Path("data/ground_truth.json").read_text())
    rows = []
    for g in ground:
        raw = json.loads(Path(f"data/traces/trace_{g['trace_id']}.json").read_text())
        r = run_synthetic(raw["code"], raw.get("test_cases", []))
        observed = "PASS" if r["exit_code"] == 0 and r["tests_passed"] == r["tests_total"] else "FAIL"
        rows.append({
            "trace_id": g["trace_id"],
            "expected": g["verdict"],
            "observed": observed,
            "match": observed == g["verdict"],
            "error": r["error"],
        })
    accuracy = sum(x["match"] for x in rows) / len(rows)
    output={"cases":len(rows),"synthetic_executor_accuracy":round(accuracy,4),"rows":rows}
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/benchmark_validation.json").write_text(json.dumps(output,indent=2))
    print(json.dumps(output,indent=2))

if __name__=="__main__":
    main()
