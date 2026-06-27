from __future__ import annotations

import csv
import shutil
from pathlib import Path

import pytest

from scripts.fetch_current_elo import RatingSnapshotError, SnapshotMetadata, import_ratings_csv
from scripts.validate_data import validate_project_data


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_import_manual_current_elo_csv_writes_snapshot_with_metadata(tmp_path: Path) -> None:
    repo_root = _copy_data_tree(tmp_path)
    input_path = tmp_path / "manual_ratings.csv"
    _write_csv(
        input_path,
        [
            {"team_id": f"t{index:02d}", "rating": str(1700 + index)}
            for index in range(1, 33)
        ],
        ["team_id", "rating"],
    )

    rows = import_ratings_csv(
        repo_root,
        input_path,
        metadata=SnapshotMetadata(
            rating_source="Manual World Football Elo snapshot",
            source_id="world_football_elo",
            rating_snapshot_kind="pre_knockout",
            rating_date="2026-07-01",
            retrieved_at="2026-07-01T12:00:00Z",
            source_url="https://www.eloratings.net/",
            notes="Manual build-time import.",
        ),
    )

    assert len(rows) == 32
    written = _read_csv(repo_root / "data/snapshots/ratings.csv")
    assert written[0]["team_id"] == "t01"
    assert written[0]["display_name"] == "Placeholder Team 01"
    assert written[0]["rating"] == "1701"
    assert written[0]["rating_source"] == "Manual World Football Elo snapshot"
    assert written[0]["source_id"] == "world_football_elo"
    assert written[0]["rating_snapshot_kind"] == "pre_knockout"
    assert written[0]["rating_date"] == "2026-07-01"
    assert written[0]["retrieved_at"] == "2026-07-01T12:00:00Z"
    assert written[0]["source_url"] == "https://www.eloratings.net/"
    validate_project_data(repo_root)


def test_import_missing_bracket_rating_fails_clearly(tmp_path: Path) -> None:
    repo_root = _copy_data_tree(tmp_path)
    input_path = tmp_path / "manual_ratings.csv"
    _write_csv(
        input_path,
        [
            {"team_id": f"t{index:02d}", "rating": str(1700 + index)}
            for index in range(2, 33)
        ],
        ["team_id", "rating"],
    )

    with pytest.raises(RatingSnapshotError, match="Missing ratings.*t01"):
        import_ratings_csv(repo_root, input_path, metadata=_valid_metadata())


def test_import_requires_source_metadata_when_input_does_not_have_it(tmp_path: Path) -> None:
    repo_root = _copy_data_tree(tmp_path)
    input_path = tmp_path / "manual_ratings.csv"
    _write_csv(
        input_path,
        [
            {"team_id": f"t{index:02d}", "rating": str(1700 + index)}
            for index in range(1, 33)
        ],
        ["team_id", "rating"],
    )

    with pytest.raises(RatingSnapshotError, match="rating_source is required"):
        import_ratings_csv(repo_root, input_path)


def _copy_data_tree(tmp_path: Path) -> Path:
    repo_root = tmp_path / "repo"
    shutil.copytree(REPO_ROOT / "data", repo_root / "data")
    (repo_root / "frontend/public/data").mkdir(parents=True)
    return repo_root


def _valid_metadata() -> SnapshotMetadata:
    return SnapshotMetadata(
        rating_source="Manual World Football Elo snapshot",
        source_id="world_football_elo",
        rating_snapshot_kind="pre_knockout",
        rating_date="2026-07-01",
        retrieved_at="2026-07-01T12:00:00Z",
        source_url="https://www.eloratings.net/",
        notes="Manual build-time import.",
    )


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def _write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
