import csv
import json
from pathlib import Path

from scripts.build_historical_elo import build_historical_elo
from scripts.calibrate_historical_model import calibrate_historical_model
from scripts.fetch_historical_results import validate_local
from scripts.historical_model import (
    CALIBRATED_MODEL_FILE,
    MATCH_FEATURES_FILE,
    MODEL_VALIDATION_REPORT_FILE,
    NORMALIZED_RESULTS_FILE,
    RESULTS_FILE,
    SHOOTOUTS_FILE,
)
from scripts.prepare_historical_results import prepare_historical_results
from scripts.validate_model import validate_model


def test_raw_historical_results_are_present():
    assert Path(RESULTS_FILE).is_file()
    assert Path(SHOOTOUTS_FILE).is_file()
    assert validate_local(Path(".")) == 0


def test_normalization_handles_shootout_outcomes(tmp_path):
    write_raw_results(
        tmp_path,
        [
            {
                "date": "2000-01-01",
                "home_team": "Alpha",
                "away_team": "Beta",
                "home_score": "1",
                "away_score": "1",
                "tournament": "Test Cup",
                "city": "Test City",
                "country": "Test Country",
                "neutral": "TRUE",
            }
        ],
        [
            {
                "date": "2000-01-01",
                "home_team": "Alpha",
                "away_team": "Beta",
                "winner": "Beta",
            }
        ],
    )

    rows = prepare_historical_results(tmp_path)

    assert len(rows) == 1
    assert rows[0]["result_type"] == "shootout_away"
    assert rows[0]["winner_team"] == "beta"
    assert rows[0]["home_result"] == "0.0"
    assert rows[0]["away_result"] == "1.0"


def test_historical_elo_uses_pre_match_ratings_before_updates(tmp_path):
    write_raw_results(
        tmp_path,
        [
            build_result("2000-01-01", "Alpha", "Beta", "1", "0"),
            build_result("2000-01-02", "Alpha", "Beta", "0", "1"),
        ],
        [],
    )

    _, feature_rows = build_historical_elo(tmp_path)

    assert feature_rows[0]["rating_a_pre"] == "1500.000000"
    assert feature_rows[0]["rating_b_pre"] == "1500.000000"
    assert float(feature_rows[1]["rating_a_pre"]) > 1500
    assert float(feature_rows[1]["rating_b_pre"]) < 1500
    assert "rating_diff_a_minus_b" in feature_rows[0]
    assert "target_a" in feature_rows[0]


def test_calibration_and_validation_report_are_generated():
    model = calibrate_historical_model(Path("."))
    report = validate_model(Path("."))

    assert Path(CALIBRATED_MODEL_FILE).is_file()
    assert Path(MODEL_VALIDATION_REPORT_FILE).is_file()
    assert model["model_id"] == "historically_informed_elo"
    assert model["metadata"]["training_match_count"] > 1000
    assert report["probability_at_zero"] == 0.5
    assert not report["errors"]


def test_generated_tournament_json_includes_historical_model_metadata():
    tournament_data = json.loads(Path("frontend/public/data/tournament.json").read_text(encoding="utf-8"))

    historical_model = tournament_data["models"]["calibrated_models"]["historically_informed_elo"]
    assert historical_model["metadata"]["training_match_count"] > 1000
    assert historical_model["metadata"]["rating_feature_type"] == "Reconstructed historical Elo features"


def write_raw_results(
    repo_root: Path,
    results: list[dict[str, str]],
    shootouts: list[dict[str, str]],
) -> None:
    results_path = repo_root / RESULTS_FILE
    shootouts_path = repo_root / SHOOTOUTS_FILE
    results_path.parent.mkdir(parents=True, exist_ok=True)
    write_rows(results_path, ["date", "home_team", "away_team", "home_score", "away_score", "tournament", "city", "country", "neutral"], results)
    write_rows(shootouts_path, ["date", "home_team", "away_team", "winner"], shootouts)


def build_result(date: str, home_team: str, away_team: str, home_score: str, away_score: str):
    return {
        "date": date,
        "home_team": home_team,
        "away_team": away_team,
        "home_score": home_score,
        "away_score": away_score,
        "tournament": "Friendly",
        "city": "Test City",
        "country": "Test Country",
        "neutral": "FALSE",
    }


def write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
