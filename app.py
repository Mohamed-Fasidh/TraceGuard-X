import json
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="TraceGuard X", layout="wide")

st.title("TraceGuard X")
st.caption("Don't trust the trace. Verify the work.")

result_file = Path("artifacts/advanced_results.json")
comparison_file = Path("artifacts/comparison.json")

if comparison_file.exists():
    comparison = json.loads(
        comparison_file.read_text(encoding="utf-8")
    )

    benchmark = comparison["benchmark"]
    accuracy = comparison["verdict_accuracy"]
    critical = comparison["critical_failure"]

    st.subheader("Benchmark")

    cols = st.columns(5)

    cols[0].metric(
        "Cases",
        benchmark["cases"],
    )

    cols[1].metric(
        "Baseline accuracy",
        f"{accuracy['baseline'] * 100:.1f}%",
    )

    cols[2].metric(
        "Advanced accuracy",
        f"{accuracy['advanced'] * 100:.1f}%",
    )

    cols[3].metric(
        "Absolute improvement",
        f"{accuracy['absolute_improvement'] * 100:.1f}pp",
    )

    cols[4].metric(
        "Critical F1",
        f"{critical['f1'] * 100:.1f}%",
    )

if not result_file.exists():
    st.info("Run the advanced evaluator to populate the evidence dashboard.")
    st.stop()

results = json.loads(result_file.read_text())
selected = st.selectbox("Evaluation run", [r["trace_id"] for r in results])
r = next(x for x in results if x["trace_id"] == selected)

cols = st.columns(4)
cols[0].metric("Verdict", r["verdict"])
cols[1].metric("Score", f"{r['score']:.1f}/100")
cols[2].metric("Evidence coverage", f"{r['evidence_coverage']*100:.0f}%")
cols[3].metric("Confidence", f"{r['confidence']*100:.0f}%")

st.subheader("Verification Plan")
for item in r["verification_plan"]:
    st.write("•", item)

st.subheader("Adversarial Verification")
st.write(f"Budget used: {r['adversarial_budget']}")
for case in r["adversarial_cases"]:
    st.write(f"**{case['id']}** — {case['rationale']} — `{case['input']}`")

st.subheader("Claim vs Evidence")
st.json({
    "findings": r["findings"],
    "execution": r["execution"],
    "property_pass_rate": r["property_pass_rate"],
})

st.subheader("Evidence Graph")
st.json(r["evidence_graph"])

st.subheader("Human Review")
if r["human_review_required"]:
    st.error("REVIEW REQUIRED — evidence is incomplete or a contradiction/failure was detected.")
else:
    st.success("No human review trigger detected.")
