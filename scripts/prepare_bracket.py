"""Prepare real knockout-stage source data from local HTML snapshots.

The frontend must remain fully static. This script is a build-time/local data
preparation tool: it reads committed snapshots from data/raw, normalizes the
Round-of-32 bracket and current rating rows, and writes the authoritative CSV
and JSON source files consumed by validation and frontend generation.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from scripts.generate_frontend_data import build_frontend_data, write_frontend_data
from scripts.validate_data import DataValidationError, validate_project_data


WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_knockout_stage"
FOOTBALLRATINGS_URL = "https://www.footballratings.org/"
DEFAULT_WIKIPEDIA_SNAPSHOT = Path("data/raw/wikipedia/2026_fifa_world_cup_knockout_stage.html")
DEFAULT_RATINGS_SNAPSHOT = Path("data/raw/footballratings/footballratings_snapshot.html")

TEAM_COLUMNS = [
    "team_id",
    "display_name",
    "short_name",
    "flag_mode",
    "flag_value",
    "fifa_code",
    "iso_alpha2",
    "iso_alpha3",
    "confederation",
    "notes",
]
RATING_COLUMNS = [
    "team_id",
    "display_name",
    "rating",
    "rating_source",
    "source_id",
    "rating_snapshot_kind",
    "rating_date",
    "retrieved_at",
    "source_url",
    "fifa_code",
    "iso_alpha2",
    "iso_alpha3",
    "notes",
]
ALIAS_COLUMNS = ["source_name", "team_id", "source_id", "valid_from", "valid_to", "notes"]

ROUND_DEFINITIONS = [
    {"round_id": "R32", "display_name": "Round of 32", "display_order": 1},
    {"round_id": "R16", "display_name": "Round of 16", "display_order": 2},
    {"round_id": "QF", "display_name": "Quarter-final", "display_order": 3},
    {"round_id": "SF", "display_name": "Semi-final", "display_order": 4},
    {"round_id": "F", "display_name": "Final", "display_order": 5},
]


class KnockoutPreparationError(Exception):
    """Raised when real source data cannot be normalized safely."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("\n".join(errors))


@dataclass(frozen=True)
class TeamMetadata:
    team_id: str
    display_name: str
    short_name: str
    fifa_code: str
    iso_alpha2: str
    iso_alpha3: str
    confederation: str
    flag_asset: str
    rating_aliases: tuple[str, ...] = ()
    wikipedia_aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class SourceMatch:
    source_match_id: str
    home_team_name: str
    away_team_name: str


TEAM_METADATA: dict[str, TeamMetadata] = {
    "South Africa": TeamMetadata("rsa", "South Africa", "South Africa", "RSA", "ZA", "ZAF", "CAF", "/flags/rsa.svg"),
    "Canada": TeamMetadata("can", "Canada", "Canada", "CAN", "CA", "CAN", "CONCACAF", "/flags/can.svg"),
    "Brazil": TeamMetadata("bra", "Brazil", "Brazil", "BRA", "BR", "BRA", "CONMEBOL", "/flags/bra.svg"),
    "Japan": TeamMetadata("jpn", "Japan", "Japan", "JPN", "JP", "JPN", "AFC", "/flags/jpn.svg"),
    "Germany": TeamMetadata("ger", "Germany", "Germany", "GER", "DE", "DEU", "UEFA", "/flags/ger.svg"),
    "Paraguay": TeamMetadata("par", "Paraguay", "Paraguay", "PAR", "PY", "PRY", "CONMEBOL", "/flags/par.svg"),
    "Netherlands": TeamMetadata("ned", "Netherlands", "Netherlands", "NED", "NL", "NLD", "UEFA", "/flags/ned.svg"),
    "Morocco": TeamMetadata("mar", "Morocco", "Morocco", "MAR", "MA", "MAR", "CAF", "/flags/mar.svg"),
    "Ivory Coast": TeamMetadata(
        "civ",
        "Cote d'Ivoire",
        "CIV",
        "CIV",
        "CI",
        "CIV",
        "CAF",
        "/flags/civ.svg",
        rating_aliases=("Côte d'Ivoire", "Ivory Coast"),
        wikipedia_aliases=("Côte d'Ivoire",),
    ),
    "Norway": TeamMetadata("nor", "Norway", "Norway", "NOR", "NO", "NOR", "UEFA", "/flags/nor.svg"),
    "France": TeamMetadata("fra", "France", "France", "FRA", "FR", "FRA", "UEFA", "/flags/fra.svg"),
    "Sweden": TeamMetadata("swe", "Sweden", "Sweden", "SWE", "SE", "SWE", "UEFA", "/flags/swe.svg"),
    "Mexico": TeamMetadata("mex", "Mexico", "Mexico", "MEX", "MX", "MEX", "CONCACAF", "/flags/mex.svg"),
    "Ecuador": TeamMetadata("ecu", "Ecuador", "Ecuador", "ECU", "EC", "ECU", "CONMEBOL", "/flags/ecu.svg"),
    "England": TeamMetadata("eng", "England", "England", "ENG", "GB", "GBR", "UEFA", "/flags/eng.svg"),
    "DR Congo": TeamMetadata(
        "cod",
        "DR Congo",
        "DR Congo",
        "COD",
        "CD",
        "COD",
        "CAF",
        "/flags/cod.svg",
        rating_aliases=("Congo DR", "Democratic Republic of the Congo"),
    ),
    "Belgium": TeamMetadata("bel", "Belgium", "Belgium", "BEL", "BE", "BEL", "UEFA", "/flags/bel.svg"),
    "Senegal": TeamMetadata("sen", "Senegal", "Senegal", "SEN", "SN", "SEN", "CAF", "/flags/sen.svg"),
    "United States": TeamMetadata(
        "usa",
        "United States",
        "USA",
        "USA",
        "US",
        "USA",
        "CONCACAF",
        "/flags/usa.svg",
        rating_aliases=("USA",),
    ),
    "Bosnia and Herzegovina": TeamMetadata("bih", "Bosnia and Herzegovina", "Bosnia", "BIH", "BA", "BIH", "UEFA", "/flags/bih.svg"),
    "Spain": TeamMetadata("esp", "Spain", "Spain", "ESP", "ES", "ESP", "UEFA", "/flags/esp.svg"),
    "Austria": TeamMetadata("aut", "Austria", "Austria", "AUT", "AT", "AUT", "UEFA", "/flags/aut.svg"),
    "Portugal": TeamMetadata("por", "Portugal", "Portugal", "POR", "PT", "PRT", "UEFA", "/flags/por.svg"),
    "Croatia": TeamMetadata("cro", "Croatia", "Croatia", "CRO", "HR", "HRV", "UEFA", "/flags/cro.svg"),
    "Switzerland": TeamMetadata("sui", "Switzerland", "Switzerland", "SUI", "CH", "CHE", "UEFA", "/flags/sui.svg"),
    "Algeria": TeamMetadata("dza", "Algeria", "Algeria", "DZA", "DZ", "DZA", "CAF", "/flags/dza.svg"),
    "Australia": TeamMetadata("aus", "Australia", "Australia", "AUS", "AU", "AUS", "AFC", "/flags/aus.svg"),
    "Egypt": TeamMetadata("egy", "Egypt", "Egypt", "EGY", "EG", "EGY", "CAF", "/flags/egy.svg"),
    "Argentina": TeamMetadata("arg", "Argentina", "Argentina", "ARG", "AR", "ARG", "CONMEBOL", "/flags/arg.svg"),
    "Cape Verde": TeamMetadata("cpv", "Cape Verde", "Cape Verde", "CPV", "CV", "CPV", "CAF", "/flags/cpv.svg", rating_aliases=("Cabo Verde",)),
    "Colombia": TeamMetadata("col", "Colombia", "Colombia", "COL", "CO", "COL", "CONMEBOL", "/flags/col.svg"),
    "Ghana": TeamMetadata("gha", "Ghana", "Ghana", "GHA", "GH", "GHA", "CAF", "/flags/gha.svg"),
}


def parse_wikipedia_round_of_32(snapshot_path: Path) -> list[SourceMatch]:
    text = _read_text(snapshot_path)
    try:
        start = text.index('id="Round_of_32"')
        end = text.index('id="Round_of_16"')
    except ValueError as error:
        raise KnockoutPreparationError(
            [f"{snapshot_path.as_posix()}: could not locate Round_of_32 and Round_of_16 sections."]
        ) from error

    segment = text[start:end]
    pattern = re.compile(
        r'<div itemscope="" itemtype="http&#58;//schema.org/SportsEvent" '
        r'class="footballbox" id="(?P<fixture_id>[^"]+)".*?'
        r'<th class="fscore">(?P<score>.*?)</th>',
        flags=re.DOTALL,
    )
    matches = [
        SourceMatch(
            source_match_id=_clean_html(match.group("score")).replace("Match ", ""),
            home_team_name=_fixture_team_names(match.group("fixture_id"))[0],
            away_team_name=_fixture_team_names(match.group("fixture_id"))[1],
        )
        for match in pattern.finditer(segment)
    ]

    errors: list[str] = []
    if len(matches) != 16:
        errors.append(f"Expected 16 Round-of-32 match boxes from Wikipedia, found {len(matches)}.")
    for source_match in matches:
        if not source_match.source_match_id.isdigit():
            errors.append(f"Wikipedia match has invalid match identifier: {source_match.source_match_id!r}.")
        for team_name in (source_match.home_team_name, source_match.away_team_name):
            if _team_metadata_for_source_name(team_name) is None:
                errors.append(f"Wikipedia team could not be mapped to project metadata: {team_name}.")
    if errors:
        raise KnockoutPreparationError(errors)

    return sorted(matches, key=lambda match: int(match.source_match_id))


def parse_footballratings(snapshot_path: Path) -> dict[str, dict[str, Any]]:
    text = _read_text(snapshot_path)
    pattern = re.compile(
        r'\{\\"rank\\":(?P<rank>\d+),\\"team\\":\\"(?P<team>[^\\"]+)\\",'
        r'\\"rating\\":(?P<rating>\d+),\\"change\\":-?\d+,\\"date\\":\\"(?P<date>\d{4}-\d{2}-\d{2})\\"',
    )
    ratings: dict[str, dict[str, Any]] = {}
    for match in pattern.finditer(text):
        team_name = html.unescape(match.group("team"))
        ratings[team_name] = {
            "rank": int(match.group("rank")),
            "team": team_name,
            "rating": int(match.group("rating")),
            "date": match.group("date"),
        }

    if not ratings:
        raise KnockoutPreparationError(
            [f"{snapshot_path.as_posix()}: could not extract FootballRatings ranking rows."]
        )
    return ratings


def build_source_files(
    wikipedia_matches: list[SourceMatch],
    ratings_by_name: dict[str, dict[str, Any]],
    retrieved_at: str,
) -> tuple[list[dict[str, str]], dict[str, Any], list[dict[str, str]], list[dict[str, str]]]:
    teams_in_order = _teams_in_bracket_order(wikipedia_matches)
    teams = [_build_team_row(team, retrieved_at) for team in teams_in_order]
    bracket = _build_bracket(wikipedia_matches)
    ratings = _build_rating_rows(teams_in_order, ratings_by_name, retrieved_at)
    aliases = _build_alias_rows(teams_in_order)
    return teams, bracket, ratings, aliases


def write_source_files(
    repo_root: Path,
    teams: list[dict[str, str]],
    bracket: dict[str, Any],
    ratings: list[dict[str, str]],
    aliases: list[dict[str, str]],
) -> None:
    _write_csv(repo_root / "data/manual/teams.csv", TEAM_COLUMNS, teams)
    _write_csv(repo_root / "data/snapshots/ratings.csv", RATING_COLUMNS, ratings)
    _write_csv(repo_root / "data/manual/team_aliases.csv", ALIAS_COLUMNS, aliases)
    (repo_root / "data/manual/bracket.json").write_text(json.dumps(bracket, indent=2) + "\n", encoding="utf-8")


def fetch_source_snapshots(wikipedia_path: Path, ratings_path: Path) -> None:
    _fetch_snapshot(WIKIPEDIA_URL, wikipedia_path)
    _fetch_snapshot(FOOTBALLRATINGS_URL, ratings_path)


def _teams_in_bracket_order(wikipedia_matches: list[SourceMatch]) -> list[TeamMetadata]:
    ordered: list[TeamMetadata] = []
    seen: set[str] = set()
    for source_match in wikipedia_matches:
        for name in (source_match.home_team_name, source_match.away_team_name):
            metadata = _team_metadata_for_source_name(name)
            if metadata is None:
                raise KnockoutPreparationError([f"Unknown team from Wikipedia source: {name}."])
            if metadata.team_id in seen:
                raise KnockoutPreparationError([f"Duplicate team in Wikipedia bracket: {metadata.display_name}."])
            seen.add(metadata.team_id)
            ordered.append(metadata)

    if len(ordered) != 32:
        raise KnockoutPreparationError([f"Expected 32 unique Round-of-32 teams, found {len(ordered)}."])
    return ordered


def _build_team_row(team: TeamMetadata, retrieved_at: str) -> dict[str, str]:
    return {
        "team_id": team.team_id,
        "display_name": team.display_name,
        "short_name": team.short_name,
        "flag_mode": "asset",
        "flag_value": team.flag_asset,
        "fifa_code": team.fifa_code,
        "iso_alpha2": team.iso_alpha2,
        "iso_alpha3": team.iso_alpha3,
        "confederation": team.confederation,
        "notes": f"Round-of-32 team from Wikipedia knockout-stage snapshot retrieved {retrieved_at}.",
    }


def _build_rating_rows(
    teams: list[TeamMetadata],
    ratings_by_name: dict[str, dict[str, Any]],
    retrieved_at: str,
) -> list[dict[str, str]]:
    errors: list[str] = []
    rows: list[dict[str, str]] = []
    for team in teams:
        rating = _rating_for_team(team, ratings_by_name)
        if rating is None:
            aliases = ", ".join(_rating_lookup_names(team))
            errors.append(f"Missing FootballRatings row for team_id '{team.team_id}' using aliases: {aliases}.")
            continue
        rows.append(
            {
                "team_id": team.team_id,
                "display_name": rating["team"],
                "rating": str(rating["rating"]),
                "rating_source": "Football Elo Ratings mirror",
                "source_id": "footballratings_mirror",
                "rating_snapshot_kind": "pre_knockout",
                "rating_date": rating["date"],
                "retrieved_at": retrieved_at,
                "source_url": FOOTBALLRATINGS_URL,
                "fifa_code": team.fifa_code,
                "iso_alpha2": team.iso_alpha2,
                "iso_alpha3": team.iso_alpha3,
                "notes": "Build-time local snapshot parsed from FootballRatings.org; site states data is updated nightly from eloratings.net.",
            }
        )
    if errors:
        raise KnockoutPreparationError(errors)
    return rows


def _build_alias_rows(teams: list[TeamMetadata]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for team in teams:
        source_names = sorted({team.display_name, *team.wikipedia_aliases, *team.rating_aliases})
        for source_name in source_names:
            rows.append(
                {
                    "source_name": source_name,
                    "team_id": team.team_id,
                    "source_id": "wikipedia_2026_knockout_stage;footballratings_mirror",
                    "valid_from": "",
                    "valid_to": "",
                    "notes": "Manual alias for Stage 6.2 knockout fixture and rating source normalization.",
                }
            )
    return rows


def _build_bracket(wikipedia_matches: list[SourceMatch]) -> dict[str, Any]:
    matches: list[dict[str, Any]] = []
    for index, source_match in enumerate(wikipedia_matches, start=1):
        home_team = _team_metadata_for_source_name(source_match.home_team_name)
        away_team = _team_metadata_for_source_name(source_match.away_team_name)
        if home_team is None or away_team is None:
            raise KnockoutPreparationError([f"Cannot build bracket for source match {source_match.source_match_id}."])
        downstream_index = (index + 1) // 2
        matches.append(
            {
                "match_id": f"R32-{index:02d}",
                "source_match_id": f"Match {source_match.source_match_id}",
                "round_id": "R32",
                "slot_a": {"slot_type": "team", "team_id": home_team.team_id},
                "slot_b": {"slot_type": "team", "team_id": away_team.team_id},
                "feeds_to_match_id": f"R16-{downstream_index:02d}",
                "feeds_to_slot": "A" if index % 2 == 1 else "B",
                "display_order": index,
            }
        )

    for round_id, count, target_prefix in (
        ("R16", 8, "QF"),
        ("QF", 4, "SF"),
        ("SF", 2, "F"),
    ):
        source_prefix = {"R16": "R32", "QF": "R16", "SF": "QF"}[round_id]
        for index in range(1, count + 1):
            target_index = (index + 1) // 2
            matches.append(
                {
                    "match_id": f"{round_id}-{index:02d}",
                    "round_id": round_id,
                    "slot_a": {"slot_type": "winner_of", "source_match_id": f"{source_prefix}-{(index * 2) - 1:02d}"},
                    "slot_b": {"slot_type": "winner_of", "source_match_id": f"{source_prefix}-{index * 2:02d}"},
                    "feeds_to_match_id": f"{target_prefix}-{target_index:02d}",
                    "feeds_to_slot": "A" if index % 2 == 1 else "B",
                    "display_order": index,
                }
            )

    matches.append(
        {
            "match_id": "F-01",
            "round_id": "F",
            "slot_a": {"slot_type": "winner_of", "source_match_id": "SF-01"},
            "slot_b": {"slot_type": "winner_of", "source_match_id": "SF-02"},
            "feeds_to_match_id": None,
            "feeds_to_slot": None,
            "display_order": 1,
        }
    )
    return {"schema_version": "1", "rounds": ROUND_DEFINITIONS, "matches": matches}


def _rating_for_team(team: TeamMetadata, ratings_by_name: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    for name in _rating_lookup_names(team):
        if name in ratings_by_name:
            return ratings_by_name[name]
    return None


def _rating_lookup_names(team: TeamMetadata) -> tuple[str, ...]:
    return (team.display_name, *team.rating_aliases)


def _team_metadata_for_source_name(source_name: str) -> TeamMetadata | None:
    if source_name in TEAM_METADATA:
        return TEAM_METADATA[source_name]
    for metadata in TEAM_METADATA.values():
        if source_name in metadata.wikipedia_aliases:
            return metadata
    return None


def _clean_html(value: str) -> str:
    cleaned = re.sub(r"<[^>]+>", "", value)
    return html.unescape(cleaned).replace("\xa0", " ").strip()


def _fixture_team_names(fixture_id: str) -> tuple[str, str]:
    normalized = html.unescape(fixture_id).replace("&#95;", "_")
    if "_v_" not in normalized:
        raise KnockoutPreparationError([f"Wikipedia footballbox id is not a fixture pair: {fixture_id}."])
    home, away = normalized.split("_v_", 1)
    return home.replace("_", " ").strip(), away.replace("_", " ").strip()


def _read_text(path: Path) -> str:
    if not path.is_file():
        raise KnockoutPreparationError([f"Missing source snapshot: {path.as_posix()}"])
    return path.read_text(encoding="utf-8")


def _fetch_snapshot(url: str, destination: Path) -> None:
    request = Request(url, headers={"User-Agent": "world-cup-forecast-build/0.1"})
    try:
        with urlopen(request, timeout=30) as response:
            payload = response.read()
            content_type = response.headers.get("content-type", "")
    except URLError as error:
        raise KnockoutPreparationError([f"Could not fetch source snapshot from {url}: {error}."]) from error

    if content_type and "html" not in content_type.lower():
        raise KnockoutPreparationError([f"Source snapshot from {url} did not return HTML content: {content_type}."])
    if b"<html" not in payload[:2048].lower():
        raise KnockoutPreparationError([f"Source snapshot from {url} does not look like HTML."])

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare real knockout bracket and ratings source files.")
    parser.add_argument("--wikipedia-snapshot", type=Path, default=DEFAULT_WIKIPEDIA_SNAPSHOT)
    parser.add_argument("--ratings-snapshot", type=Path, default=DEFAULT_RATINGS_SNAPSHOT)
    parser.add_argument(
        "--fetch-snapshots",
        action="store_true",
        help="Fetch Wikipedia and FootballRatings HTML snapshots before parsing them.",
    )
    parser.add_argument(
        "--retrieved-at",
        default=datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        help="Retrieval timestamp to write into generated rating source rows.",
    )
    parser.add_argument(
        "--skip-frontend-generation",
        action="store_true",
        help="Write source files only; do not regenerate frontend/public/data/tournament.json.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    repo_root = Path(__file__).resolve().parents[1]

    try:
        if args.fetch_snapshots:
            fetch_source_snapshots(repo_root / args.wikipedia_snapshot, repo_root / args.ratings_snapshot)
        wikipedia_matches = parse_wikipedia_round_of_32(repo_root / args.wikipedia_snapshot)
        ratings_by_name = parse_footballratings(repo_root / args.ratings_snapshot)
        teams, bracket, ratings, aliases = build_source_files(
            wikipedia_matches=wikipedia_matches,
            ratings_by_name=ratings_by_name,
            retrieved_at=args.retrieved_at,
        )
        write_source_files(repo_root, teams, bracket, ratings, aliases)
        project_data = validate_project_data(repo_root)
        if not args.skip_frontend_generation:
            write_frontend_data(repo_root, build_frontend_data(project_data))
    except (KnockoutPreparationError, DataValidationError) as error:
        errors = error.errors if hasattr(error, "errors") else [str(error)]
        print("Knockout source preparation failed:")
        for message in errors:
            print(f"- {message}")
        return 1

    print(f"Wrote {len(teams)} teams, {len(bracket['matches'])} matches, and {len(ratings)} ratings.")
    print("Source data validation passed.")
    if not args.skip_frontend_generation:
        print("Regenerated frontend tournament data.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
