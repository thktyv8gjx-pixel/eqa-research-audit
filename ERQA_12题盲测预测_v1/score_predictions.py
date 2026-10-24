"""Score immutable submitted predictions against private ERQA labels; no inference.

Run: python3 score_predictions.py
Only predicted_answer == answer is used; uncertainty never excludes a row.
"""
import csv
import hashlib
import io
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OFFICIAL = HERE.parent / "ERQA_EXPLORE_2026-10-24/private/first12/examples.jsonl"


def main():
    exceptions = []

    def read_rows(path, source):
        indexed = {}
        for line_no, line in enumerate(path.read_text().splitlines(), 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                key = row["row_index"]
                if type(key) is not int or key not in range(12):
                    raise ValueError("row_index must be an integer in 0..11")
                indexed.setdefault(key, []).append(row)
            except (ValueError, TypeError, KeyError) as error:
                exceptions.append({"source": source, "line": line_no, "error": str(error)})
        return indexed

    predictions_path = HERE / "predictions.jsonl"
    original = predictions_path.read_bytes()
    predictions = read_rows(predictions_path, "predictions")
    official = read_rows(OFFICIAL, "official")
    info = json.loads((HERE / "run_info.json").read_text())
    prediction_hash = hashlib.sha256(original).hexdigest()
    if prediction_hash != info.get("predictions_sha256"):
        exceptions.append({"source": "run_info", "error": "predictions_sha256 mismatch"})
    scores = []
    for index in range(12):
        pair = {}
        for source, values, field in [("predictions", predictions, "predicted_answer"),
                                      ("official", official, "answer")]:
            matches = values.get(index, [])
            if len(matches) != 1:
                exceptions.append({"source": source, "row_index": index,
                                   "error": f"Expected exactly one row, found {len(matches)}"})
                pair[source] = None
                continue
            pair[source] = matches[0]
            if matches[0].get(field) not in ("A", "B", "C", "D"):
                exceptions.append({"source": source, "row_index": index,
                                   "error": f"Invalid or missing {field}"})
        prediction = (pair["predictions"] or {}).get("predicted_answer")
        answer = (pair["official"] or {}).get("answer")
        valid = prediction in ("A", "B", "C", "D") and answer in ("A", "B", "C", "D")
        scores.append({"row_index": index, "predicted_answer": prediction,
                       "official_answer": answer, "correct": valid and prediction == answer,
                       "comparison_status": "COMPARED" if valid else "CORRESPONDENCE_OR_PARSE_ERROR",
                       "uncertainty_flag": (pair["predictions"] or {}).get("uncertainty_flag")})
    summary = {"run_id": info.get("run_id"), "scoring_rule": "literal predicted_answer == official answer; no normalization",
               "denominator": 12, "compared_rows": sum(s["comparison_status"] == "COMPARED" for s in scores),
               "correct": sum(s["correct"] for s in scores), "incorrect_row_indices": [s["row_index"] for s in scores if not s["correct"]],
               "uncertain_rows_included": [s["row_index"] for s in scores if s["uncertainty_flag"]],
               "exceptions": exceptions, "predictions_sha256": prediction_hash,
               "official_local_source_sha256": hashlib.sha256(OFFICIAL.read_bytes()).hexdigest(),
               "run_info_sha256": hashlib.sha256((HERE / "run_info.json").read_bytes()).hexdigest(),
               "prediction_method_as_supplied": info.get("prediction_method"),
               "new_model_calls_during_scoring": 0,
               "provenance_note": "run_info.json is preserved as submitted, including its pre-scoring NOT_SCORED state; blinding claims are supplied metadata, not independently verified here.",
               "official_source": "https://github.com/embodiedreasoning/ERQA/tree/5bba488252c5b345a43335bfb9239b6bf12bd91c",
               "official_license": "CC BY 4.0; images and full question bank are not republished."}
    summary["accuracy"] = summary["correct"] / 12
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(scores[0]))
    writer.writeheader()
    writer.writerows(scores)
    (HERE / "scores.csv").write_text(stream.getvalue())
    (HERE / "score_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    assert predictions_path.read_bytes() == original, "Prediction input was modified"
    print(stream.getvalue())
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
