"""Build-time current Elo snapshot acquisition.

This script creates the local ratings snapshot consumed by validation and the
frontend data generator. It supports two build-time paths:

- import-csv: normalize a manually prepared local CSV.
- fetch-csv: download a CSV from a URL, then normalize it.

The frontend must never call this script or fetch live rating data at runtime.
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

from scripts.validate_data import DataValidationError, validate_project_data


DEFAULT_OUTPUT_PATH = Path("data/snapshots/ratings.csv")
DEFAULT_RAW_DOWNLOAD_PATH = Path("data/raw/elo/current_ratings.csv")
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


class RatingSnapshotError(Exception):
    """Raised when a rating snapshot cannot be imported safely."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("\n".join(errors))


@dataclass(frozen=True)
class SnapshotMetadata:
    rating_source: str | None
    source_id: str | None
    rating_snapshot_kind: str | None
    rating_date: str | None
    retrieved_at: str
    source_url: str | None
    notes: str | None


def import_ratings_csv(
    repo_root: Path,
    input_path: Path,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    metadata: SnapshotMetadata | None = None,
) -> list[dict[str, str]]:
    """Normalize a manually prepared ratings CSV and write ratings.csv."""

    metadata = metadata or SnapshotMetadata(
        rating_source=None,
        source_id=None,
        rating_snapshot_kind=None,
        rating_date=None,
        retrieved_at=_utc_now(),
        source_url=None,
        notes=None,
    )

    teams = _read_csv(repo_root / "data/manual/teams.csv")
    bracket_team_ids = _read_bracket_team_ids(repo_root / "data/manual/bracket.json")
    input_rows = _read_csv(input_path)
    normalized_rows = normalize_rating_rows(input_rows, teams, bracket_team_ids, metadata)

    destination = repo_root / output_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    previous_content = destination.read_bytes() if destination.exists() else None
    _write_csv(destination, normalized_rows)

    try:
        validate_project_data(repo_root)
    except DataValidationError as error:
        if previous_content is None:
            destination.unlink(missing_ok=True)
        else:
            destination.write_bytes(previous_content)
        raise RatingSnapshotError(
            ["Imported ratings did not pass project validation.", *error.errors]
        ) from error

    return normalized_rows


def normalize_rating_rows(
    input_rows: list[dict[str, str]],
    teams: list[dict[str, str]],
    bracket_team_ids: set[str],
    metadata: SnapshotMetadata,
) -> list[dict[str, str]]:
    """Normalize source rows to the project rating snapshot contract."""

    errors: list[str] = []
    teams_by_id = {team.get("team_id", ""): team for team in teams if team.get("team_id")}
    rows_by_team_id: dict[str, dict[str, str]] = {}

    if not input_rows:
        raise RatingSnapshotError(["Input ratings CSV must contain at least one data row."])

    present_columns = set(input_rows[0].keys())
    if "team_id" not in present_columns:
        errors.append("Input ratings CSV is missing required column: team_id.")
    if "rating" not in present_columns:
        errors.append("Input ratings CSV is missing required column: rating.")
    if errors:
        raise RatingSnapshotError(errors)

    for row_number, row in enumerate(input_rows, start=2):
        team_id = row.get("team_id", "").strip()
        if not team_id:
            errors.append(f"Input ratings row {row_number}: team_id is required.")
            continue
        if team_id in rows_by_team_id:
            errors.append(f"Input ratings row {row_number}: duplicate team_id '{team_id}'.")
            continue
        if team_id not in teams_by_id:
            continue

        rating = row.get("rating", "").strip()
        if not rating:
            errors.append(f"Input ratings row {row_number}: rating is required for team_id '{team_id}'.")
        else:
            try:
                float(rating)
            except ValueError:
                errors.append(
                    f"Input ratings row {row_number}: rating must be numeric for team_id '{team_id}', got '{rating}'."
                )
        rows_by_team_id[team_id] = row

    missing_team_ids = sorted(bracket_team_ids - set(rows_by_team_id))
    if missing_team_ids:
        errors.append(f"Missing ratings for bracket team_id values: {', '.join(missing_team_ids)}.")

    normalized_rows: list[dict[str, str]] = []
    for team in teams:
        team_id = team["team_id"]
        if team_id not in bracket_team_ids:
            continue
        source_row = rows_by_team_id.get(team_id)
        if source_row is None:
            continue
        normalized_rows.append(_normalize_row(source_row, team, metadata, errors))

    if errors:
        raise RatingSnapshotError(errors)

    return normalized_rows


def fetch_csv(url: str, destination: Path) -> Path:
    """Download a CSV source file for build-time import."""

    request = Request(url, headers={"User-Agent": "world-cup-forecast-build/0.1"})
    try:
        with urlopen(request, timeout=30) as response:
            content_type = response.headers.get("content-type", "")
            payload = response.read()
    except URLError as error:
        raise RatingSnapshotError([f"Could not fetch ratings CSV from {url}: {error}."]) from error

    if b"," not in payload[:4096]:
        raise RatingSnapshotError(
            [
                f"Fetched rating source from {url} does not look like CSV.",
                "Use import-csv with a manually prepared CSV if the source is HTML or otherwise unavailable.",
            ]
        )
    if content_type and "html" in content_type.lower():
        raise RatingSnapshotError(
            [
                f"Fetched rating source from {url} returned HTML content.",
                "Use import-csv with a manually prepared CSV for sources that do not expose a CSV file.",
            ]
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    return destination


def _normalize_row(
    source_row: dict[str, str],
    team: dict[str, str],
    metadata: SnapshotMetadata,
    errors: list[str],
) -> dict[str, str]:
    team_id = team["team_id"]

    rating_source = _value(source_row, "rating_source", metadata.rating_source)
    source_id = _value(source_row, "source_id", metadata.source_id)
    rating_snapshot_kind = _value(source_row, "rating_snapshot_kind", metadata.rating_snapshot_kind)
    rating_date = _value(source_row, "rating_date", metadata.rating_date)
    retrieved_at = _value(source_row, "retrieved_at", metadata.retrieved_at)
    source_url = _value(source_row, "source_url", metadata.source_url)
    notes = _value(source_row, "notes", metadata.notes)

    for field_name, value in (
        ("rating_source", rating_source),
        ("source_id", source_id),
        ("rating_snapshot_kind", rating_snapshot_kind),
        ("rating_date", rating_date),
        ("retrieved_at", retrieved_at),
    ):
        if not value:
            errors.append(f"Input ratings row for team_id '{team_id}': {field_name} is required.")

    return {
        "team_id": team_id,
        "display_name": _value(source_row, "display_name", team["display_name"]),
        "rating": source_row.get("rating", "").strip(),
        "rating_source": rating_source,
        "source_id": source_id,
        "rating_snapshot_kind": rating_snapshot_kind,
        "rating_date": rating_date,
        "retrieved_at": retrieved_at,
        "source_url": source_url,
        "fifa_code": _value(source_row, "fifa_code", team.get("fifa_code", "")),
        "iso_alpha2": _value(source_row, "iso_alpha2", team.get("iso_alpha2", "")),
        "iso_alpha3": _value(source_row, "iso_alpha3", team.get("iso_alpha3", "")),
        "notes": notes,
    }


def _value(row: dict[str, str], column: str, fallback: str | None) -> str:
    value = row.get(column, "").strip()
    if value:
        return value
    return fallback or ""


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise RatingSnapshotError([f"Missing ratings input file: {path.as_posix()}"])

    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise RatingSnapshotError([f"{path.as_posix()} must contain a CSV header row."])
        return [{key: (value or "").strip() for key, value in row.items()} for row in reader]


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=RATING_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _read_bracket_team_ids(path: Path) -> set[str]:
    import json

    if not path.is_file():
        raise RatingSnapshotError([f"Missing bracket file: {path.as_posix()}"])

    bracket = json.loads(path.read_text(encoding="utf-8"))
    team_ids: set[str] = set()
    for match in bracket.get("matches", []):
        if not isinstance(match, dict) or match.get("round_id") != "R32":
            continue
        for slot_name in ("slot_a", "slot_b"):
            slot = match.get(slot_name)
            if isinstance(slot, dict) and slot.get("slot_type") == "team" and slot.get("team_id"):
                team_ids.add(slot["team_id"])
    return team_ids


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create data/snapshots/ratings.csv from build-time current Elo data.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    import_parser = subparsers.add_parser("import-csv", help="Import a manually prepared local ratings CSV.")
    _add_common_options(import_parser)
    import_parser.add_argument("--input", required=True, type=Path, help="Manual ratings CSV to import.")

    fetch_parser = subparsers.add_parser("fetch-csv", help="Fetch a ratings CSV URL, then import it.")
    _add_common_options(fetch_parser)
    fetch_parser.add_argument("--url", required=True, help="Build-time CSV URL to download.")
    fetch_parser.add_argument(
        "--raw-output",
        default=DEFAULT_RAW_DOWNLOAD_PATH,
        type=Path,
        help="Local raw CSV download path.",
    )

    return parser


def _add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output", default=DEFAULT_OUTPUT_PATH, type=Path, help="Ratings snapshot output path.")
    parser.add_argument("--rating-source", help="Human-readable rating source name.")
    parser.add_argument("--source-id", help="Stable source ID from data/manual/source_catalog.json.")
    parser.add_argument(
        "--snapshot-kind",
        default="pre_knockout",
        help="Snapshot kind, for example pre_knockout, pre_tournament, manual, or test_fixture.",
    )
    parser.add_argument("--rating-date", help="Date the ratings represent, in YYYY-MM-DD form.")
    parser.add_argument("--retrieved-at", default=_utc_now(), help="Project retrieval timestamp.")
    parser.add_argument("--source-url", help="Source URL or source identifier.")
    parser.add_argument("--notes", help="Notes to apply to imported rating rows.")


def _metadata_from_args(args: argparse.Namespace) -> SnapshotMetadata:
    source_url = args.source_url
    if args.command == "fetch-csv" and not source_url:
        source_url = args.url

    return SnapshotMetadata(
        rating_source=args.rating_source,
        source_id=args.source_id,
        rating_snapshot_kind=args.snapshot_kind,
        rating_date=args.rating_date,
        retrieved_at=args.retrieved_at,
        source_url=source_url,
        notes=args.notes,
    )


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    repo_root = Path(__file__).resolve().parents[1]

    try:
        if args.command == "fetch-csv":
            input_path = fetch_csv(args.url, repo_root / args.raw_output)
        else:
            input_path = args.input

        rows = import_ratings_csv(
            repo_root=repo_root,
            input_path=input_path if input_path.is_absolute() else repo_root / input_path,
            output_path=args.output,
            metadata=_metadata_from_args(args),
        )
    except RatingSnapshotError as error:
        print("Current Elo snapshot acquisition failed:")
        for message in error.errors:
            print(f"- {message}")
        return 1

    print(f"Wrote {len(rows)} rating rows to {args.output.as_posix()}.")
    print("Data validation passed for the imported rating snapshot.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
