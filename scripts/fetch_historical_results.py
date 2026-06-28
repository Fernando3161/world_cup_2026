"""Fetch and validate local historical international football result snapshots."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from scripts.historical_model import (
    RESULTS_FILE,
    SHOOTOUTS_FILE,
    SOURCE_ID,
    SOURCE_METADATA_FILE,
    SOURCE_NAME,
    SOURCE_URL,
    utc_now_iso,
)


RAW_RESULTS_URL = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"
RAW_SHOOTOUTS_URL = "https://raw.githubusercontent.com/martj42/international_results/master/shootouts.csv"
GITHUB_COMMIT_API_URL = "https://api.github.com/repos/martj42/international_results/commits/master"
PARSER_VERSION = "fetch_historical_results.py:1"


def fetch(repo_root: Path) -> int:
    raw_dir = repo_root / RESULTS_FILE.parent
    raw_dir.mkdir(parents=True, exist_ok=True)

    try:
        results_bytes = _download(RAW_RESULTS_URL)
        shootouts_bytes = _download(RAW_SHOOTOUTS_URL)
        commit_sha = _fetch_commit_sha()
    except RuntimeError as error:
        print(f"Historical result fetch failed: {error}")
        return 1

    (repo_root / RESULTS_FILE).write_bytes(results_bytes)
    (repo_root / SHOOTOUTS_FILE).write_bytes(shootouts_bytes)

    metadata: dict[str, Any] = {
        "source_id": SOURCE_ID,
        "source_name": SOURCE_NAME,
        "source_url": SOURCE_URL,
        "raw_file_urls": {
            "results.csv": RAW_RESULTS_URL,
            "shootouts.csv": RAW_SHOOTOUTS_URL,
        },
        "retrieved_at": utc_now_iso(),
        "files": ["results.csv", "shootouts.csv"],
        "commit_sha": commit_sha,
        "license_note": (
            "External open dataset. Review upstream repository license and attribution "
            "requirements before publication."
        ),
        "parser_script": PARSER_VERSION,
    }
    (repo_root / SOURCE_METADATA_FILE).write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )

    return validate_local(repo_root)


def validate_local(repo_root: Path) -> int:
    errors: list[str] = []
    for relative_path in (RESULTS_FILE, SHOOTOUTS_FILE, SOURCE_METADATA_FILE):
        path = repo_root / relative_path
        if not path.is_file():
            errors.append(f"Missing required historical source file: {relative_path.as_posix()}")
            continue
        if path.stat().st_size == 0:
            errors.append(f"Historical source file is empty: {relative_path.as_posix()}")

    if not errors:
        errors.extend(_validate_csv_header(repo_root / RESULTS_FILE, {"date", "home_team", "away_team", "home_score", "away_score", "tournament", "neutral"}))
        errors.extend(_validate_csv_header(repo_root / SHOOTOUTS_FILE, {"date", "home_team", "away_team", "winner"}))
        errors.extend(_validate_metadata(repo_root / SOURCE_METADATA_FILE))

    if errors:
        print("Historical local source validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Historical local source validation passed.")
    return 0


def _download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "world-cup-forecast-data-fetch/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status != 200:
                raise RuntimeError(f"{url} returned HTTP {response.status}.")
            return response.read()
    except urllib.error.URLError as error:
        raise RuntimeError(f"Could not fetch {url}: {error}") from error


def _fetch_commit_sha() -> str | None:
    request = urllib.request.Request(GITHUB_COMMIT_API_URL, headers={"User-Agent": "world-cup-forecast-data-fetch/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status != 200:
                return None
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError):
        return None
    return data.get("sha") if isinstance(data, dict) else None


def _validate_csv_header(path: Path, required_columns: set[str]) -> list[str]:
    if not path.exists():
        return []
    first_line = path.read_text(encoding="utf-8-sig").splitlines()[0]
    columns = {column.strip() for column in first_line.split(",")}
    missing = sorted(required_columns - columns)
    if missing:
        return [f"{path.as_posix()} is missing expected columns: {', '.join(missing)}"]
    return []


def _validate_metadata(path: Path) -> list[str]:
    if not path.exists():
        return []
    try:
        metadata = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return [f"{path.as_posix()} is not valid JSON: {error}"]

    required_fields = {"source_name", "source_url", "retrieved_at", "files", "license_note", "parser_script"}
    missing = sorted(field for field in required_fields if not metadata.get(field))
    return [f"{path.as_posix()} is missing metadata fields: {', '.join(missing)}"] if missing else []


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["fetch", "validate-local"])
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(__file__).resolve().parents[1]

    if args.command == "fetch":
        return fetch(repo_root)
    return validate_local(repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
