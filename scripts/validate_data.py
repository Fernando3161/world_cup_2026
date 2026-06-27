"""Validate MVP source data for the static forecast site."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROUND_DEFINITIONS = {
    "R32": {"display_name": "Round of 32", "display_order": 1, "match_count": 16},
    "R16": {"display_name": "Round of 16", "display_order": 2, "match_count": 8},
    "QF": {"display_name": "Quarter-final", "display_order": 3, "match_count": 4},
    "SF": {"display_name": "Semi-final", "display_order": 4, "match_count": 2},
    "F": {"display_name": "Final", "display_order": 5, "match_count": 1},
}
ROUND_ORDER = {round_id: data["display_order"] for round_id, data in ROUND_DEFINITIONS.items()}

REQUIRED_MVP_FILES = (
    Path("data/manual/bracket.json"),
    Path("data/manual/teams.csv"),
    Path("data/snapshots/ratings.csv"),
)

TEAM_REQUIRED_COLUMNS = {
    "team_id",
    "display_name",
    "short_name",
    "flag_mode",
    "flag_value",
}
RATING_REQUIRED_COLUMNS = {
    "team_id",
    "display_name",
    "rating",
    "rating_source",
    "source_id",
    "rating_snapshot_kind",
    "rating_date",
    "retrieved_at",
}


class DataValidationError(Exception):
    """Raised when source data does not satisfy the MVP data contract."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("\n".join(errors))


@dataclass(frozen=True)
class ProjectData:
    repo_root: Path
    teams: list[dict[str, str]]
    ratings: list[dict[str, str]]
    bracket: dict[str, Any]
    sources: list[dict[str, Any]]


def find_missing_files(repo_root: Path) -> list[Path]:
    """Return required MVP source files that are not present."""

    return [path for path in REQUIRED_MVP_FILES if not (repo_root / path).is_file()]


def load_project_data(repo_root: Path) -> ProjectData:
    """Load source files without validating cross-file relationships."""

    missing_files = find_missing_files(repo_root)
    if missing_files:
        errors = [f"Missing required source file: {path.as_posix()}" for path in missing_files]
        raise DataValidationError(errors)

    teams = _read_csv(repo_root / "data/manual/teams.csv")
    ratings = _read_csv(repo_root / "data/snapshots/ratings.csv")
    bracket = _read_json(repo_root / "data/manual/bracket.json")
    source_catalog_path = repo_root / "data/manual/source_catalog.json"
    sources = _read_json(source_catalog_path).get("sources", []) if source_catalog_path.exists() else []

    return ProjectData(
        repo_root=repo_root,
        teams=teams,
        ratings=ratings,
        bracket=bracket,
        sources=sources,
    )


def validate_project_data(repo_root: Path) -> ProjectData:
    """Load and validate all MVP source data."""

    project_data = load_project_data(repo_root)
    errors: list[str] = []

    errors.extend(_validate_csv_columns("teams.csv", project_data.teams, TEAM_REQUIRED_COLUMNS))
    errors.extend(_validate_csv_columns("ratings.csv", project_data.ratings, RATING_REQUIRED_COLUMNS))
    errors.extend(_validate_teams(project_data.teams))
    errors.extend(_validate_ratings(project_data.ratings))
    errors.extend(_validate_bracket(project_data.bracket, project_data.teams, project_data.ratings))

    if errors:
        raise DataValidationError(errors)

    return project_data


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return [{key: (value or "").strip() for key, value in row.items()} for row in reader]


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise DataValidationError([f"{path.as_posix()} must contain a JSON object."])
    return data


def _validate_csv_columns(
    file_name: str,
    rows: list[dict[str, str]],
    required_columns: set[str],
) -> list[str]:
    if not rows:
        return [f"{file_name} must contain at least one data row."]

    present_columns = set(rows[0].keys())
    missing_columns = sorted(required_columns - present_columns)
    if missing_columns:
        return [f"{file_name} is missing required columns: {', '.join(missing_columns)}"]
    return []


def _validate_teams(teams: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    seen_team_ids: set[str] = set()

    for row_number, team in enumerate(teams, start=2):
        team_id = team.get("team_id", "")
        if not team_id:
            errors.append(f"teams.csv row {row_number}: team_id is required.")
            continue
        if team_id in seen_team_ids:
            errors.append(f"teams.csv row {row_number}: duplicate team_id '{team_id}'.")
        seen_team_ids.add(team_id)

        for field in ("display_name", "short_name", "flag_mode", "flag_value"):
            if not team.get(field):
                errors.append(f"teams.csv row {row_number}: {field} is required for team_id '{team_id}'.")

    return errors


def _validate_ratings(ratings: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    seen_team_ids: set[str] = set()

    for row_number, rating in enumerate(ratings, start=2):
        team_id = rating.get("team_id", "")
        if not team_id:
            errors.append(f"ratings.csv row {row_number}: team_id is required.")
            continue
        if team_id in seen_team_ids:
            errors.append(f"ratings.csv row {row_number}: duplicate rating for team_id '{team_id}'.")
        seen_team_ids.add(team_id)

        for field in ("display_name", "rating_source", "source_id", "rating_snapshot_kind", "rating_date", "retrieved_at"):
            if not rating.get(field):
                errors.append(f"ratings.csv row {row_number}: {field} is required for team_id '{team_id}'.")

        rating_value = rating.get("rating", "")
        if not rating_value:
            errors.append(f"ratings.csv row {row_number}: rating is required for team_id '{team_id}'.")
            continue
        try:
            float(rating_value)
        except ValueError:
            errors.append(
                f"ratings.csv row {row_number}: rating must be numeric for team_id '{team_id}', got '{rating_value}'."
            )

    return errors


def _validate_bracket(
    bracket: dict[str, Any],
    teams: list[dict[str, str]],
    ratings: list[dict[str, str]],
) -> list[str]:
    errors: list[str] = []
    matches = bracket.get("matches")
    rounds = bracket.get("rounds")

    if not isinstance(rounds, list):
        errors.append("bracket.json: rounds must be a list.")
        rounds = []
    if not isinstance(matches, list):
        errors.append("bracket.json: matches must be a list.")
        matches = []

    errors.extend(_validate_rounds(rounds))

    team_ids = {team["team_id"] for team in teams if team.get("team_id")}
    rated_team_ids = {rating["team_id"] for rating in ratings if rating.get("team_id")}

    seen_match_ids: set[str] = set()
    match_by_id: dict[str, dict[str, Any]] = {}
    matches_by_round = {round_id: 0 for round_id in ROUND_DEFINITIONS}

    for index, match in enumerate(matches):
        label = f"bracket.json match index {index}"
        if not isinstance(match, dict):
            errors.append(f"{label}: match must be an object.")
            continue

        match_id = match.get("match_id")
        round_id = match.get("round_id")
        if not match_id:
            errors.append(f"{label}: match_id is required.")
        elif match_id in seen_match_ids:
            errors.append(f"{label}: duplicate match_id '{match_id}'.")
        else:
            seen_match_ids.add(match_id)
            match_by_id[match_id] = match

        if round_id not in ROUND_DEFINITIONS:
            errors.append(f"{match_id or label}: invalid round_id '{round_id}'.")
        else:
            matches_by_round[round_id] += 1

        if not isinstance(match.get("display_order"), int):
            errors.append(f"{match_id or label}: display_order must be an integer.")

        for slot_name in ("slot_a", "slot_b"):
            errors.extend(_validate_slot(match_id or label, slot_name, match.get(slot_name), round_id, team_ids))

    for round_id, expected in ROUND_DEFINITIONS.items():
        actual = matches_by_round[round_id]
        if actual != expected["match_count"]:
            errors.append(f"Round {round_id} must contain {expected['match_count']} matches, found {actual}.")

    for match in matches:
        if not isinstance(match, dict):
            continue
        match_id = match.get("match_id", "<missing match_id>")
        round_id = match.get("round_id")
        current_order = ROUND_ORDER.get(round_id)

        feeds_to_match_id = match.get("feeds_to_match_id")
        feeds_to_slot = match.get("feeds_to_slot")
        if round_id == "F":
            if feeds_to_match_id is not None or feeds_to_slot is not None:
                errors.append(f"{match_id}: final match must not feed to another match.")
        else:
            if feeds_to_match_id not in match_by_id:
                errors.append(f"{match_id}: feeds_to_match_id '{feeds_to_match_id}' does not reference a valid match.")
            elif current_order is not None:
                target_round_id = match_by_id[feeds_to_match_id].get("round_id")
                if ROUND_ORDER.get(target_round_id, 0) <= current_order:
                    errors.append(f"{match_id}: feeds_to_match_id '{feeds_to_match_id}' must point to a later round.")
            if feeds_to_slot not in {"A", "B"}:
                errors.append(f"{match_id}: feeds_to_slot must be 'A' or 'B' for non-final matches.")

        for slot_name in ("slot_a", "slot_b"):
            slot = match.get(slot_name)
            if not isinstance(slot, dict):
                continue
            if slot.get("slot_type") == "winner_of":
                source_match_id = slot.get("source_match_id")
                if source_match_id not in match_by_id:
                    errors.append(f"{match_id} {slot_name}: source_match_id '{source_match_id}' does not reference a valid match.")
                elif current_order is not None:
                    source_round_id = match_by_id[source_match_id].get("round_id")
                    if ROUND_ORDER.get(source_round_id, 99) >= current_order:
                        errors.append(f"{match_id} {slot_name}: source_match_id '{source_match_id}' must point to an earlier round.")

    bracket_team_ids = _collect_bracket_team_ids(matches)
    missing_teams = sorted(bracket_team_ids - team_ids)
    if missing_teams:
        errors.append(f"Bracket references unknown team_id values: {', '.join(missing_teams)}.")

    missing_ratings = sorted(bracket_team_ids - rated_team_ids)
    if missing_ratings:
        errors.append(f"Missing ratings for bracket team_id values: {', '.join(missing_ratings)}.")

    if len(bracket_team_ids) != 32:
        errors.append(f"Bracket must reference exactly 32 first-round teams, found {len(bracket_team_ids)}.")

    return errors


def _validate_rounds(rounds: list[Any]) -> list[str]:
    errors: list[str] = []
    seen_round_ids: set[str] = set()

    for index, round_data in enumerate(rounds):
        if not isinstance(round_data, dict):
            errors.append(f"bracket.json round index {index}: round must be an object.")
            continue

        round_id = round_data.get("round_id")
        if round_id not in ROUND_DEFINITIONS:
            errors.append(f"bracket.json round index {index}: invalid round_id '{round_id}'.")
            continue
        if round_id in seen_round_ids:
            errors.append(f"bracket.json round index {index}: duplicate round_id '{round_id}'.")
        seen_round_ids.add(round_id)

        expected = ROUND_DEFINITIONS[round_id]
        if round_data.get("display_order") != expected["display_order"]:
            errors.append(f"Round {round_id}: display_order must be {expected['display_order']}.")

    missing_rounds = sorted(set(ROUND_DEFINITIONS) - seen_round_ids, key=ROUND_ORDER.get)
    if missing_rounds:
        errors.append(f"bracket.json is missing round definitions: {', '.join(missing_rounds)}.")

    return errors


def _validate_slot(
    match_label: str,
    slot_name: str,
    slot: Any,
    round_id: str | None,
    team_ids: set[str],
) -> list[str]:
    errors: list[str] = []
    if not isinstance(slot, dict):
        return [f"{match_label}: {slot_name} must be an object."]

    slot_type = slot.get("slot_type")
    if slot_type not in {"team", "winner_of", "empty"}:
        errors.append(f"{match_label} {slot_name}: invalid slot_type '{slot_type}'.")
        return errors

    if round_id == "R32" and slot_type != "team":
        errors.append(f"{match_label} {slot_name}: Round-of-32 slots must use slot_type 'team'.")

    if slot_type == "team":
        team_id = slot.get("team_id")
        if not team_id:
            errors.append(f"{match_label} {slot_name}: team_id is required when slot_type is 'team'.")
        elif team_id not in team_ids:
            errors.append(f"{match_label} {slot_name}: unknown team_id '{team_id}'.")
    elif slot_type == "winner_of":
        if not slot.get("source_match_id"):
            errors.append(f"{match_label} {slot_name}: source_match_id is required when slot_type is 'winner_of'.")

    return errors


def _collect_bracket_team_ids(matches: list[Any]) -> set[str]:
    team_ids: set[str] = set()
    for match in matches:
        if not isinstance(match, dict) or match.get("round_id") != "R32":
            continue
        for slot_name in ("slot_a", "slot_b"):
            slot = match.get(slot_name)
            if isinstance(slot, dict) and slot.get("slot_type") == "team" and slot.get("team_id"):
                team_ids.add(slot["team_id"])
    return team_ids


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    try:
        validate_project_data(repo_root)
    except DataValidationError as error:
        print("Data validation failed:")
        for message in error.errors:
            print(f"- {message}")
        return 1

    print("Data validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
