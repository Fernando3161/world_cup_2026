from __future__ import annotations

from pathlib import Path

import pytest

from scripts.prepare_bracket import (
    KnockoutPreparationError,
    build_source_files,
    parse_footballratings,
    parse_wikipedia_round_of_32,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
WIKIPEDIA_SNAPSHOT = REPO_ROOT / "data/raw/wikipedia/2026_fifa_world_cup_knockout_stage.html"
RATINGS_SNAPSHOT = REPO_ROOT / "data/raw/footballratings/footballratings_snapshot.html"


def test_parse_wikipedia_round_of_32_snapshot() -> None:
    matches = parse_wikipedia_round_of_32(WIKIPEDIA_SNAPSHOT)

    assert len(matches) == 16
    assert matches[0].source_match_id == "73"
    assert matches[0].home_team_name == "South Africa"
    assert matches[0].away_team_name == "Canada"
    assert matches[7].home_team_name == "England"
    assert matches[7].away_team_name == "DR Congo"
    assert matches[-1].source_match_id == "88"
    assert matches[-1].home_team_name == "Australia"
    assert matches[-1].away_team_name == "Egypt"


def test_parse_footballratings_snapshot() -> None:
    ratings = parse_footballratings(RATINGS_SNAPSHOT)

    assert ratings["Spain"]["rating"] == 2144
    assert ratings["Argentina"]["date"] == "2026-06-28"
    assert ratings["DR Congo"]["rating"] == 1712


def test_build_source_files_fails_when_required_rating_is_missing() -> None:
    matches = parse_wikipedia_round_of_32(WIKIPEDIA_SNAPSHOT)
    ratings = parse_footballratings(RATINGS_SNAPSHOT)
    ratings.pop("DR Congo")

    with pytest.raises(KnockoutPreparationError, match="Missing FootballRatings row.*cod"):
        build_source_files(matches, ratings, retrieved_at="2026-06-28T12:00:00Z")
