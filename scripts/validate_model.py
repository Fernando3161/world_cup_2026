"""Validate the generated historically informed Elo model artifact."""

from __future__ import annotations

from pathlib import Path

from scripts.calibrate_historical_model import calibrate_historical_model
from scripts.historical_model import (
    CALIBRATED_MODEL_FILE,
    MODEL_ID,
    MODEL_VALIDATION_REPORT_FILE,
    SIMPLE_ELO_BETA,
    SOURCE_ID,
    logistic_probability_from_diff,
    read_json,
    utc_now_iso,
    write_json,
)


SAMPLE_RATING_DIFFS = [-400, -200, -100, 0, 100, 200, 400]


def validate_model(repo_root: Path) -> dict[str, object]:
    model_path = repo_root / CALIBRATED_MODEL_FILE
    if not model_path.exists():
        calibrate_historical_model(repo_root)

    model = read_json(model_path)
    errors: list[str] = []

    if model.get("model_id") != MODEL_ID:
        errors.append(f"calibrated_model.json model_id must be {MODEL_ID}.")

    metadata = model.get("metadata")
    calibration = model.get("calibration")
    if not isinstance(metadata, dict):
        errors.append("calibrated_model.json metadata must be an object.")
        metadata = {}
    if not isinstance(calibration, dict):
        errors.append("calibrated_model.json calibration must be an object.")
        calibration = {}

    training_match_count = int(metadata.get("training_match_count", 0) or 0)
    if training_match_count < 1000:
        errors.append(f"training_match_count must be nonzero and reasonable, got {training_match_count}.")
    if metadata.get("training_source_id") != SOURCE_ID:
        errors.append("historical calibration must use the committed historical result source metadata.")
    if "placeholder" in str(metadata).lower() or "demo" in str(metadata).lower():
        errors.append("calibration metadata must not indicate placeholder/demo training data.")

    alpha = float(calibration.get("alpha", 0))
    beta = float(calibration.get("beta", 0))
    if beta <= 0:
        errors.append("calibrated beta must be positive so probabilities increase with rating difference.")

    sample_predictions = []
    last_probability = -1.0
    for rating_diff in SAMPLE_RATING_DIFFS:
        historical_probability = logistic_probability_from_diff(rating_diff, alpha, beta)
        simple_probability = logistic_probability_from_diff(rating_diff, 0, SIMPLE_ELO_BETA)
        sample_predictions.append(
            {
                "rating_diff": rating_diff,
                "simple_elo_probability": round(simple_probability, 6),
                "historically_informed_probability": round(historical_probability, 6),
            }
        )

        if historical_probability < 0 or historical_probability > 1:
            errors.append(f"Probability at rating_diff {rating_diff} is outside [0, 1].")
        if historical_probability < last_probability:
            errors.append("Calibrated probability curve must be monotonic increasing.")
        last_probability = historical_probability

    equal_rating_probability = logistic_probability_from_diff(0, alpha, beta)
    if abs(equal_rating_probability - 0.5) > 0.03:
        errors.append(f"Probability at rating_diff 0 must be close to 0.5, got {equal_rating_probability:.4f}.")

    report: dict[str, object] = {
        "validated_at": utc_now_iso(),
        "model_id": model.get("model_id"),
        "model_version": model.get("model_version"),
        "training_match_count": training_match_count,
        "probability_at_zero": round(equal_rating_probability, 6),
        "is_monotonic_on_samples": not errors,
        "sample_predictions": sample_predictions,
        "errors": errors,
    }
    write_json(repo_root / MODEL_VALIDATION_REPORT_FILE, report)

    if errors:
        raise ValueError("\n".join(errors))
    return report


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    try:
        report = validate_model(repo_root)
    except ValueError as error:
        print("Model validation failed:")
        for message in str(error).splitlines():
            print(f"- {message}")
        return 1

    print(f"Model validation passed. Report written to {MODEL_VALIDATION_REPORT_FILE.as_posix()}.")
    print(f"Training matches: {report['training_match_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
