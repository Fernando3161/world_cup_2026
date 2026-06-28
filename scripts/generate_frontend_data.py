"""Generate static frontend tournament data from validated MVP source files."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scripts.historical_model import CALIBRATED_MODEL_FILE, MODEL_ID
from scripts.validate_data import DataValidationError, ProjectData, validate_project_data


PUBLIC_OUTPUT_PATH = Path("frontend/public/data/tournament.json")
DATA_OUTPUT_PATH = Path("data/frontend/tournament.json")


def build_frontend_data(project_data: ProjectData) -> dict[str, Any]:
    ratings_by_team_id = {rating["team_id"]: rating for rating in project_data.ratings}
    first_rating = project_data.ratings[0]
    calibrated_model = _load_calibrated_model(project_data.repo_root)
    available_models = [
        {
            "model_id": "simple_elo",
            "display_name": "Simple Elo",
            "model_version": "1.0.0",
            "probability_method": "rating_difference_logistic",
            "is_available": True,
        }
    ]
    calibrated_models: dict[str, Any] = {}
    if calibrated_model:
        available_models.append(
            {
                "model_id": calibrated_model["model_id"],
                "display_name": calibrated_model["display_name"],
                "model_version": calibrated_model["model_version"],
                "probability_method": calibrated_model["probability_method"],
                "is_available": True,
            }
        )
        calibrated_models[calibrated_model["model_id"]] = {
            "calibration": calibrated_model["calibration"],
            "metadata": calibrated_model["metadata"],
            "diagnostics": calibrated_model.get("diagnostics", {}),
        }
    else:
        available_models.append(
            {
                "model_id": MODEL_ID,
                "display_name": "Historically informed Elo",
                "model_version": "0.1.0",
                "probability_method": "historical_reconstructed_elo_logistic_recalibration",
                "is_available": False,
            }
        )

    return {
        "schema_version": "1",
        "tournament": {
            "tournament_id": "fifa-world-cup-2026",
            "display_name": "FIFA World Cup 2026",
            "stage": "knockout",
            "starts_at_round": "R32",
            "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "data_version": "wikipedia-r32-footballratings-2026-06-28",
            "data_note": (
                "Round-of-32 fixtures are parsed from a local Wikipedia knockout-stage snapshot; "
                "ratings are parsed from a local FootballRatings.org snapshot dated 2026-06-28."
            ),
        },
        "sources": project_data.sources,
        "models": {
            "default_model_id": "simple_elo",
            "available_models": available_models,
            "calibrated_models": calibrated_models,
            "rating_source": first_rating["rating_source"],
            "rating_snapshot_date": first_rating["rating_date"],
            "rating_snapshot_kind": first_rating["rating_snapshot_kind"],
        },
        "teams": [_build_frontend_team(team, ratings_by_team_id[team["team_id"]]) for team in project_data.teams],
        "rounds": project_data.bracket["rounds"],
        "matches": project_data.bracket["matches"],
        "official_results": [],
    }


def write_frontend_data(repo_root: Path, data: dict[str, Any]) -> list[Path]:
    output_paths = [repo_root / PUBLIC_OUTPUT_PATH, repo_root / DATA_OUTPUT_PATH]
    for output_path in output_paths:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return output_paths


def _build_frontend_team(team: dict[str, str], rating: dict[str, str]) -> dict[str, Any]:
    frontend_team: dict[str, Any] = {
        "team_id": team["team_id"],
        "display_name": team["display_name"],
        "short_name": team["short_name"],
        "rating": float(rating["rating"]),
        "rating_source": rating["rating_source"],
        "source_id": rating["source_id"],
        "rating_snapshot_kind": rating["rating_snapshot_kind"],
        "rating_date": rating["rating_date"],
        "retrieved_at": rating["retrieved_at"],
        "flag_mode": team["flag_mode"],
        "flag_value": team["flag_value"],
    }

    for field in ("fifa_code", "iso_alpha2", "iso_alpha3", "confederation", "notes"):
        value = team.get(field)
        if value:
            frontend_team[field] = value

    source_url = rating.get("source_url")
    if source_url:
        frontend_team["source_url"] = source_url

    return frontend_team


def _load_calibrated_model(repo_root: Path) -> dict[str, Any] | None:
    path = repo_root / CALIBRATED_MODEL_FILE
    if not path.exists():
        return None

    with path.open(encoding="utf-8") as file:
        model = json.load(file)
    if not isinstance(model, dict) or model.get("model_id") != MODEL_ID:
        return None
    if not model.get("is_available") or not isinstance(model.get("calibration"), dict):
        return None
    return model


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    try:
        project_data = validate_project_data(repo_root)
    except DataValidationError as error:
        print("Cannot generate frontend data because source data is invalid:")
        for message in error.errors:
            print(f"- {message}")
        return 1

    output_paths = write_frontend_data(repo_root, build_frontend_data(project_data))
    print("Generated frontend tournament data:")
    for output_path in output_paths:
        print(f"- {output_path.relative_to(repo_root).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
