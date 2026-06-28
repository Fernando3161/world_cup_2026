"""Calibrate a compact historically informed Elo probability model."""

from __future__ import annotations

import math
from pathlib import Path
from statistics import mean

from scripts.build_historical_elo import build_historical_elo
from scripts.historical_model import (
    CALIBRATED_MODEL_FILE,
    ELO_FORMULA_VERSION,
    INITIAL_ELO,
    K_FACTOR,
    MATCH_FEATURES_FILE,
    MODEL_DISPLAY_NAME,
    MODEL_ID,
    MODEL_VERSION,
    SIMPLE_ELO_BETA,
    SOURCE_ID,
    SOURCE_NAME,
    SOURCE_METADATA_FILE,
    SOURCE_URL,
    clamp_probability,
    logistic_probability_from_diff,
    read_csv,
    read_json,
    utc_now_iso,
    write_json,
)


def calibrate_historical_model(repo_root: Path) -> dict[str, object]:
    features_path = repo_root / MATCH_FEATURES_FILE
    if not features_path.exists():
        build_historical_elo(repo_root)

    feature_rows = read_csv(features_path)
    if not feature_rows:
        raise ValueError("historical_match_features.csv contains no rows.")

    training_examples = [
        (float(row["rating_diff_a_minus_b"]), float(row["target_a"]))
        for row in feature_rows
    ]
    gamma = _fit_gamma(training_examples)
    beta = gamma / 400.0
    alpha = 0.0
    dates = [row["date"] for row in feature_rows if row.get("date")]
    source_metadata = _load_source_metadata(repo_root)

    sample_rating_differences = [-400, -200, -100, 0, 100, 200, 400]
    sample_predictions = [
        {
            "rating_diff": rating_diff,
            "simple_elo_probability": round(clamp_probability(logistic_probability_from_diff(rating_diff, 0, SIMPLE_ELO_BETA)), 6),
            "historically_informed_probability": round(clamp_probability(logistic_probability_from_diff(rating_diff, alpha, beta)), 6),
        }
        for rating_diff in sample_rating_differences
    ]

    model: dict[str, object] = {
        "model_id": MODEL_ID,
        "display_name": MODEL_DISPLAY_NAME,
        "model_version": MODEL_VERSION,
        "is_available": True,
        "probability_method": "historical_reconstructed_elo_logistic_recalibration",
        "calibration": {
            "type": "logistic",
            "alpha": alpha,
            "beta": beta,
            "input": "rating_diff_a_minus_b",
            "formula": "P(team A advances) = 1 / (1 + exp(-(alpha + beta * rating_diff)))",
        },
        "metadata": {
            "training_data_source": SOURCE_NAME,
            "training_source_id": SOURCE_ID,
            "training_source_url": SOURCE_URL,
            "training_source_commit_sha": source_metadata.get("commit_sha"),
            "training_match_count": len(feature_rows),
            "training_date_min": min(dates),
            "training_date_max": max(dates),
            "rating_feature_type": "Reconstructed historical Elo features",
            "rating_reconstruction_params": {
                "initial_rating": INITIAL_ELO,
                "k_factor": K_FACTOR,
                "expected_score_formula": "1 / (1 + 10 ^ (-rating_diff / 400))",
                "elo_formula_version": ELO_FORMULA_VERSION,
                "home_field_adjustment": 0,
                "importance_weighting": "none",
            },
            "calibration_method": (
                "One-parameter logistic recalibration fit to historical expected-score targets. "
                "Draws without shootouts are target 0.5; shootout winners are target 1."
            ),
            "generated_at": utc_now_iso(),
            "notes": (
                "Historically calibrated from international match results and locally reconstructed "
                "pre-match Elo features. It is used as a knockout advancement proxy, not as an "
                "official Elo table or betting model."
            ),
        },
        "diagnostics": {
            "log_loss": round(_log_loss(training_examples, alpha, beta), 6),
            "mean_target": round(mean(target for _, target in training_examples), 6),
            "sample_predictions": sample_predictions,
        },
    }
    write_json(repo_root / CALIBRATED_MODEL_FILE, model)
    return model


def _fit_gamma(examples: list[tuple[float, float]]) -> float:
    gamma = math.log(10)
    learning_rate = 0.08
    scaled_examples = [(rating_diff / 400.0, target) for rating_diff, target in examples]

    for _ in range(1200):
        gradient = 0.0
        for scaled_diff, target in scaled_examples:
            z = gamma * scaled_diff
            probability = 1 / (1 + math.exp(-z)) if z >= 0 else math.exp(z) / (1 + math.exp(z))
            gradient += (probability - target) * scaled_diff
        gradient /= len(scaled_examples)
        gamma -= learning_rate * gradient
        gamma = min(8.0, max(0.01, gamma))

    return gamma


def _log_loss(examples: list[tuple[float, float]], alpha: float, beta: float) -> float:
    losses: list[float] = []
    for rating_diff, target in examples:
        probability = min(1 - 1e-12, max(1e-12, logistic_probability_from_diff(rating_diff, alpha, beta)))
        losses.append(-(target * math.log(probability) + (1 - target) * math.log(1 - probability)))
    return mean(losses)


def _load_source_metadata(repo_root: Path) -> dict[str, object]:
    path = repo_root / SOURCE_METADATA_FILE
    if not path.exists():
        return {}
    return read_json(path)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    try:
        model = calibrate_historical_model(repo_root)
    except ValueError as error:
        print(f"Historical model calibration failed: {error}")
        return 1

    metadata = model["metadata"]
    assert isinstance(metadata, dict)
    print(f"Wrote calibrated historical model to {CALIBRATED_MODEL_FILE.as_posix()}.")
    print(f"Training matches: {metadata['training_match_count']}")
    print(f"Date range: {metadata['training_date_min']} to {metadata['training_date_max']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
