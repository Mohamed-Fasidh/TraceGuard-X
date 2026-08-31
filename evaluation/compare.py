import argparse
import json
from pathlib import Path


def prf(truth, predicted):
    """
    Calculate precision, recall and F1 for a binary set prediction.
    """

    tp = len(truth & predicted)
    fp = len(predicted - truth)
    fn = len(truth - predicted)

    precision = (
        tp / (tp + fp)
        if (tp + fp)
        else 0.0
    )

    recall = (
        tp / (tp + fn)
        if (tp + fn)
        else 0.0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall)
        else 0.0
    )

    return (
        tp,
        fp,
        fn,
        precision,
        recall,
        f1,
    )


def safe_accuracy(results, truth):
    """
    Calculate verdict accuracy while ensuring every evaluated
    trace exists in the ground truth.
    """

    if not results:
        return 0.0

    correct = 0

    for result in results:

        trace_id = result["trace_id"]

        if trace_id not in truth:
            raise ValueError(
                f"Result contains unknown trace_id: {trace_id}"
            )

        if (
            result.get("verdict")
            == truth[trace_id]["verdict"]
        ):
            correct += 1

    return correct / len(results)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--baseline",
        required=True,
    )

    parser.add_argument(
        "--advanced",
        required=True,
    )

    parser.add_argument(
        "--ground",
        default="data/ground_truth.json",
    )

    args = parser.parse_args()

    baseline = json.loads(
        Path(args.baseline).read_text(
            encoding="utf-8"
        )
    )

    advanced = json.loads(
        Path(args.advanced).read_text(
            encoding="utf-8"
        )
    )

    ground_truth = json.loads(
        Path(args.ground).read_text(
            encoding="utf-8"
        )
    )

    truth = {
        item["trace_id"]: item
        for item in ground_truth
    }

    # ---------------------------------------------------------
    # Benchmark integrity
    # ---------------------------------------------------------

    expected_ids = set(truth)

    baseline_ids = {
        item["trace_id"]
        for item in baseline
    }

    advanced_ids = {
        item["trace_id"]
        for item in advanced
    }

    if baseline_ids != expected_ids:
        raise ValueError(
            "Baseline result set does not exactly match "
            "the ground-truth benchmark."
        )

    if advanced_ids != expected_ids:
        raise ValueError(
            "Advanced result set does not exactly match "
            "the ground-truth benchmark."
        )

    # ---------------------------------------------------------
    # Verdict accuracy
    # ---------------------------------------------------------

    baseline_accuracy = safe_accuracy(
        baseline,
        truth,
    )

    advanced_accuracy = safe_accuracy(
        advanced,
        truth,
    )

    absolute_improvement = (
        advanced_accuracy
        - baseline_accuracy
    )

    relative_improvement = (
        absolute_improvement
        / baseline_accuracy
        * 100
        if baseline_accuracy
        else 0.0
    )

    # ---------------------------------------------------------
    # Helper
    # ---------------------------------------------------------

    def categories(result):

        return {
            finding.get("category")
            for finding in result.get(
                "findings",
                []
            )
        }

    # ---------------------------------------------------------
    # Critical failure
    # ---------------------------------------------------------

    critical_truth = {
        item["trace_id"]
        for item in ground_truth
        if item.get("critical_failure") is True
    }

    #
    # IMPORTANT:
    #
    # Only genuine candidate evidence counts as a critical
    # candidate failure.
    #
    # sandbox_timeout and verification_gap are handled separately
    # and do not count as candidate failures.

    critical_categories = {
    "runtime_error",
    "dependency_error",
    "syntax_error",
    "timeout",
}

    critical_predicted = {
        result["trace_id"]
        for result in advanced
        if categories(result)
        & critical_categories
    }

    (
        critical_tp,
        critical_fp,
        critical_fn,
        critical_precision,
        critical_recall,
        critical_f1,
    ) = prf(
        critical_truth,
        critical_predicted,
    )

    # ---------------------------------------------------------
    # Claim / evidence contradiction
    # ---------------------------------------------------------

    contradiction_truth = {
        item["trace_id"]
        for item in ground_truth
        if item.get("contradiction") is True
    }

    contradiction_predicted = {
        result["trace_id"]
        for result in advanced
        if "claim_evidence_contradiction"
        in categories(result)
    }

    (
        contradiction_tp,
        contradiction_fp,
        contradiction_fn,
        contradiction_precision,
        contradiction_recall,
        contradiction_f1,
    ) = prf(
        contradiction_truth,
        contradiction_predicted,
    )

    # ---------------------------------------------------------
    # Verification gap
    # ---------------------------------------------------------

    verification_gap_predicted = {
        result["trace_id"]
        for result in advanced
        if "verification_gap"
        in categories(result)
    }

    sandbox_failure_predicted = {
        result["trace_id"]
        for result in advanced
        if "sandbox_timeout"
        in categories(result)
    }

    # ---------------------------------------------------------
    # Confusion matrix
    # ---------------------------------------------------------

    rows = []

    for trace_id in sorted(truth):

        expected = truth[trace_id]

        advanced_result = next(
            result
            for result in advanced
            if result["trace_id"] == trace_id
        )

        predicted = advanced_result["verdict"]

        rows.append({
            "trace_id": trace_id,
            "expected": expected["verdict"],
            "predicted": predicted,
            "correct": (
                expected["verdict"]
                == predicted
            ),
            "case_type": expected.get(
                "case_type"
            ),
            "findings": [
                finding.get("category")
                for finding in advanced_result.get(
                    "findings",
                    []
                )
            ],
        })

    actual_pass_predicted_pass = sum(
        row["expected"] == "PASS"
        and row["predicted"] == "PASS"
        for row in rows
    )

    actual_pass_predicted_fail = sum(
        row["expected"] == "PASS"
        and row["predicted"] != "PASS"
        for row in rows
    )

    actual_fail_predicted_fail = sum(
        row["expected"] != "PASS"
        and row["predicted"] != "PASS"
        for row in rows
    )

    actual_fail_predicted_pass = sum(
        row["expected"] != "PASS"
        and row["predicted"] == "PASS"
        for row in rows
    )

    # ---------------------------------------------------------
    # Per-case analysis
    # ---------------------------------------------------------

    error_cases = [
        row
        for row in rows
        if not row["correct"]
    ]

    # ---------------------------------------------------------
    # Final metrics
    # ---------------------------------------------------------

    metrics = {

        "benchmark": {
            "cases": len(ground_truth),
            "baseline_cases": len(baseline),
            "advanced_cases": len(advanced),
            "same_benchmark": True,
        },

        "verdict_accuracy": {
            "baseline": round(
                baseline_accuracy,
                4,
            ),
            "advanced": round(
                advanced_accuracy,
                4,
            ),
            "absolute_improvement": round(
                absolute_improvement,
                4,
            ),
            "relative_improvement_percent": round(
                relative_improvement,
                2,
            ),
        },

        "critical_failure": {
            "tp": critical_tp,
            "fp": critical_fp,
            "fn": critical_fn,
            "precision": round(
                critical_precision,
                4,
            ),
            "recall": round(
                critical_recall,
                4,
            ),
            "f1": round(
                critical_f1,
                4,
            ),
        },

        "claim_evidence_contradiction": {
            "tp": contradiction_tp,
            "fp": contradiction_fp,
            "fn": contradiction_fn,
            "precision": round(
                contradiction_precision,
                4,
            ),
            "recall": round(
                contradiction_recall,
                4,
            ),
            "f1": round(
                contradiction_f1,
                4,
            ),
        },

        "verification": {
            "verification_gap_cases": len(
                verification_gap_predicted
            ),
            "sandbox_failure_cases": len(
                sandbox_failure_predicted
            ),
        },

        "confusion_matrix": {

            "pass": {
                "actual_pass_predicted_pass":
                    actual_pass_predicted_pass,

                "actual_pass_predicted_fail":
                    actual_pass_predicted_fail,
            },

            "fail": {
                "actual_fail_predicted_fail":
                    actual_fail_predicted_fail,

                "actual_fail_predicted_pass":
                    actual_fail_predicted_pass,
            },
        },

        "error_analysis": {
            "incorrect_cases": len(
                error_cases
            ),
            "cases": error_cases,
        },

        "rows": rows,
    }

    # ---------------------------------------------------------
    # Write result
    # ---------------------------------------------------------

    output_dir = Path("artifacts")

    output_dir.mkdir(
        exist_ok=True
    )

    output_file = (
        output_dir
        / "comparison.json"
    )

    output_file.write_text(
        json.dumps(
            metrics,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            metrics,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()