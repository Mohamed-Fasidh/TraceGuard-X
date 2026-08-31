
import json
from pathlib import Path
from src.traceguard.tools.mutation import mutation_kill_rate
from src.traceguard.tools.benchmark_executor import run_synthetic

def verifier(code):
    r = run_synthetic(code, [
        {"input":"hello","expected":"hello"},
        {"input":"","expected":""},
        {"input":"x","expected":"x"},
        {"input":"café","expected":"café"},
    ])
    return {
        "verdict": "PASS"
        if r["exit_code"] == 0 and r["tests_passed"] == r["tests_total"]
        else "FAIL"
    }

def main():
    rows=[]
    for path in sorted(Path("data/traces").glob("*.json")):
        raw=json.loads(path.read_text())
        if raw["case_type"] == "correct":
            rows.append({
                "trace_id": raw["trace_id"],
                **mutation_kill_rate(raw["code"], verifier)
            })

    total=sum(x["total"] for x in rows)
    killed=sum(x["killed"] for x in rows)
    report={
        "benchmark_cases": len(rows),
        "mutations_total": total,
        "mutations_killed": killed,
        "mutation_detection_rate": round(killed/total,4) if total else 0,
        "rows": rows,
    }
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/mutation_report.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    main()
