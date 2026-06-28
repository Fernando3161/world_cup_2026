from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

import pytest

from scripts.generate_frontend_data import build_frontend_data, write_frontend_data
from scripts.validate_data import DataValidationError, validate_project_data


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_valid_example_data_passes_validation() -> None:
    project_data = validate_project_data(REPO_ROOT)

    assert len(project_data.teams) == 32
    assert len(project_data.ratings) == 32
    assert len(project_data.bracket["matches"]) == 31


def test_frontend_data_generation_shape(tmp_path: Path) -> None:
    repo_root = _copy_data_tree(tmp_path)
    project_data = validate_project_data(repo_root)
    frontend_data = build_frontend_data(project_data)
    output_paths = write_frontend_data(repo_root, frontend_data)

    assert {path.relative_to(repo_root).as_posix() for path in output_paths} == {
        "frontend/public/data/tournament.json",
        "data/frontend/tournament.json",
    }

    generated = json.loads((repo_root / "frontend/public/data/tournament.json").read_text(encoding="utf-8"))
    assert generated["schema_version"] == "1"
    assert generated["models"]["default_model_id"] == "simple_elo"
    assert len(generated["teams"]) == 32
    assert len(generated["rounds"]) == 5
    assert len(generated["matches"]) == 31
    assert generated["official_results"] == []


def test_duplicate_team_id_fails(tmp_path: Path) -> None:
    repo_root = _copy_data_tree(tmp_path)
    teams_path = repo_root / "data/manual/teams.csv"
    rows = _read_csv(teams_path)
    rows[1]["team_id"] = rows[0]["team_id"]
    _write_csv(teams_path, rows)

    with pytest.raises(DataValidationError, match=f"duplicate team_id '{rows[0]['team_id']}'"):
        validate_project_data(repo_root)


def test_duplicate_match_id_fails(tmp_path: Path) -> None:
    repo_root = _copy_data_tree(tmp_path)
    bracket_path = repo_root / "data/manual/bracket.json"
    bracket = json.loads(bracket_path.read_text(encoding="utf-8"))
    bracket["matches"][1]["match_id"] = "R32-01"
    bracket_path.write_text(json.dumps(bracket, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(DataValidationError, match="duplicate match_id 'R32-01'"):
        validate_project_data(repo_root)


def test_missing_rating_fails(tmp_path: Path) -> None:
    repo_root = _copy_data_tree(tmp_path)
    ratings_path = repo_root / "data/snapshots/ratings.csv"
    removed_team_id = _read_csv(ratings_path)[0]["team_id"]
    rows = [row for row in _read_csv(ratings_path) if row["team_id"] != removed_team_id]
    _write_csv(ratings_path, rows)

    with pytest.raises(DataValidationError, match=f"Missing ratings.*{removed_team_id}"):
        validate_project_data(repo_root)


def test_asset_flag_path_must_be_local_svg(tmp_path: Path) -> None:
    repo_root = _copy_data_tree(tmp_path)
    teams_path = repo_root / "data/manual/teams.csv"
    rows = _read_csv(teams_path)
    rows[0]["flag_mode"] = "asset"
    rows[0]["flag_value"] = "https://example.com/bra.svg"
    _write_csv(teams_path, rows)

    with pytest.raises(DataValidationError, match="asset flag_value must start with '/flags/'"):
        validate_project_data(repo_root)


def test_unknown_flag_mode_fails(tmp_path: Path) -> None:
    repo_root = _copy_data_tree(tmp_path)
    teams_path = repo_root / "data/manual/teams.csv"
    rows = _read_csv(teams_path)
    rows[0]["flag_mode"] = "remote"
    _write_csv(teams_path, rows)

    with pytest.raises(DataValidationError, match="flag_mode must be one of"):
        validate_project_data(repo_root)


def test_invalid_round_id_fails(tmp_path: Path) -> None:
    repo_root = _copy_data_tree(tmp_path)
    bracket_path = repo_root / "data/manual/bracket.json"
    bracket = json.loads(bracket_path.read_text(encoding="utf-8"))
    bracket["matches"][0]["round_id"] = "BAD"
    bracket_path.write_text(json.dumps(bracket, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(DataValidationError, match="invalid round_id 'BAD'"):
        validate_project_data(repo_root)


def test_invalid_match_reference_fails(tmp_path: Path) -> None:
    repo_root = _copy_data_tree(tmp_path)
    bracket_path = repo_root / "data/manual/bracket.json"
    bracket = json.loads(bracket_path.read_text(encoding="utf-8"))
    bracket["matches"][16]["slot_a"]["source_match_id"] = "R32-99"
    bracket_path.write_text(json.dumps(bracket, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(DataValidationError, match="source_match_id 'R32-99'"):
        validate_project_data(repo_root)


def test_round_match_count_fails(tmp_path: Path) -> None:
    repo_root = _copy_data_tree(tmp_path)
    bracket_path = repo_root / "data/manual/bracket.json"
    bracket = json.loads(bracket_path.read_text(encoding="utf-8"))
    bracket["matches"] = [match for match in bracket["matches"] if match["match_id"] != "R32-16"]
    bracket_path.write_text(json.dumps(bracket, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(DataValidationError, match="Round R32 must contain 16 matches, found 15"):
        validate_project_data(repo_root)


def _copy_data_tree(tmp_path: Path) -> Path:
    repo_root = tmp_path / "repo"
    shutil.copytree(REPO_ROOT / "data", repo_root / "data")
    (repo_root / "frontend/public/data").mkdir(parents=True)
    return repo_root


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
