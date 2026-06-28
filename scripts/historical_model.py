"""Shared helpers for the offline historical Elo calibration pipeline."""

from __future__ import annotations

import csv
import json
import math
import re
import unicodedata
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable


SOURCE_ID = "martj42_international_results"
SOURCE_NAME = "Mart Jurisoo international_results"
SOURCE_URL = "https://github.com/martj42/international_results"
RAW_DIR = Path("data/raw/international_results")
RESULTS_FILE = RAW_DIR / "results.csv"
SHOOTOUTS_FILE = RAW_DIR / "shootouts.csv"
SOURCE_METADATA_FILE = RAW_DIR / "source_metadata.json"
NORMALIZED_RESULTS_FILE = Path("data/processed/historical_results_normalized.csv")
EXCLUDED_RESULTS_FILE = Path("data/processed/historical_results_excluded.csv")
ELO_TIMESERIES_FILE = Path("data/processed/historical_elo_timeseries.csv")
MATCH_FEATURES_FILE = Path("data/processed/historical_match_features.csv")
CALIBRATED_MODEL_FILE = Path("data/processed/calibrated_model.json")
MODEL_VALIDATION_REPORT_FILE = Path("data/processed/model_validation_report.json")
TEAM_ALIASES_FILE = Path("data/manual/team_aliases.csv")

MODEL_ID = "historically_informed_elo"
MODEL_DISPLAY_NAME = "Historically informed Elo"
MODEL_VERSION = "0.1.0"
ELO_FORMULA_VERSION = "reconstructed-simple-elo-v1"
INITIAL_ELO = 1500.0
K_FACTOR = 20.0
SIMPLE_ELO_SCALE = 400.0
SIMPLE_ELO_BETA = math.log(10) / SIMPLE_ELO_SCALE


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return [{key: (value or "").strip() for key, value in row.items()} for row in reader]


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"{path.as_posix()} must contain a JSON object.")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def normalize_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", ascii_value.lower()).strip()


def slugify_team_name(value: str) -> str:
    normalized = normalize_name(value)
    slug = re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")
    return slug or "unknown_team"


def load_alias_map(repo_root: Path) -> dict[str, str]:
    alias_path = repo_root / TEAM_ALIASES_FILE
    if not alias_path.exists():
        return {}

    aliases: dict[str, str] = {}
    for row in read_csv(alias_path):
        source_name = row.get("source_name", "")
        team_id = row.get("team_id", "")
        if source_name and team_id:
            aliases[normalize_name(source_name)] = team_id
    return aliases


def team_id_for_source_name(source_name: str, aliases: dict[str, str]) -> str:
    return aliases.get(normalize_name(source_name), slugify_team_name(source_name))


def simple_elo_probability_from_diff(rating_diff: float) -> float:
    return 1 / (1 + 10 ** (-rating_diff / SIMPLE_ELO_SCALE))


def logistic_probability_from_diff(rating_diff: float, alpha: float, beta: float) -> float:
    z = alpha + beta * rating_diff
    if z >= 0:
        return 1 / (1 + math.exp(-z))
    exp_z = math.exp(z)
    return exp_z / (1 + exp_z)


def clamp_probability(value: float) -> float:
    return min(1.0, max(0.0, value))
