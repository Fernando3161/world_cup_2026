"""Normalize local historical international results for Elo reconstruction."""

from __future__ import annotations

from pathlib import Path

from scripts.historical_model import (
    EXCLUDED_RESULTS_FILE,
    NORMALIZED_RESULTS_FILE,
    RESULTS_FILE,
    SHOOTOUTS_FILE,
    SOURCE_ID,
    load_alias_map,
    normalize_name,
    read_csv,
    team_id_for_source_name,
    write_csv,
)


NORMALIZED_FIELDS = [
    "match_id",
    "date",
    "home_team",
    "away_team",
    "home_team_id",
    "away_team_id",
    "neutral",
    "tournament",
    "city",
    "country",
    "home_score",
    "away_score",
    "result_type",
    "winner_team",
    "loser_team",
    "shootout_winner",
    "home_result",
    "away_result",
    "source_match_id",
    "source_id",
    "notes",
]
EXCLUDED_FIELDS = [
    "source_match_id",
    "date",
    "home_team",
    "away_team",
    "home_score",
    "away_score",
    "reason",
]


def prepare_historical_results(repo_root: Path) -> list[dict[str, str]]:
    results_path = repo_root / RESULTS_FILE
    shootouts_path = repo_root / SHOOTOUTS_FILE
    if not results_path.exists() or not shootouts_path.exists():
        missing = [
            relative_path.as_posix()
            for relative_path in (RESULTS_FILE, SHOOTOUTS_FILE)
            if not (repo_root / relative_path).exists()
        ]
        raise ValueError(f"Missing historical raw files: {', '.join(missing)}")

    aliases = load_alias_map(repo_root)
    shootout_winners = _load_shootout_winners(shootouts_path)
    rows: list[dict[str, str]] = []
    excluded_rows: list[dict[str, str]] = []

    for index, raw in enumerate(read_csv(results_path), start=1):
        home_team = raw.get("home_team", "")
        away_team = raw.get("away_team", "")
        home_score = _parse_score(raw.get("home_score", ""))
        away_score = _parse_score(raw.get("away_score", ""))
        if home_score is None or away_score is None:
            excluded_rows.append(
                {
                    "source_match_id": f"results.csv:{index}",
                    "date": raw.get("date", ""),
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_score": raw.get("home_score", ""),
                    "away_score": raw.get("away_score", ""),
                    "reason": "Missing or non-integer score; excluded from historical calibration.",
                }
            )
            continue
        home_team_id = team_id_for_source_name(home_team, aliases)
        away_team_id = team_id_for_source_name(away_team, aliases)
        shootout_winner_name = shootout_winners.get(_shootout_key(raw.get("date", ""), home_team, away_team))
        shootout_winner_id = team_id_for_source_name(shootout_winner_name, aliases) if shootout_winner_name else ""

        result_type, winner_team, loser_team, home_result, away_result, notes = _derive_result(
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            home_score=home_score,
            away_score=away_score,
            shootout_winner_id=shootout_winner_id,
        )

        rows.append(
            {
                "match_id": f"hist-{index:06d}",
                "date": raw.get("date", ""),
                "home_team": home_team,
                "away_team": away_team,
                "home_team_id": home_team_id,
                "away_team_id": away_team_id,
                "neutral": raw.get("neutral", ""),
                "tournament": raw.get("tournament", ""),
                "city": raw.get("city", ""),
                "country": raw.get("country", ""),
                "home_score": str(home_score),
                "away_score": str(away_score),
                "result_type": result_type,
                "winner_team": winner_team,
                "loser_team": loser_team,
                "shootout_winner": shootout_winner_id,
                "home_result": _format_target(home_result),
                "away_result": _format_target(away_result),
                "source_match_id": f"results.csv:{index}",
                "source_id": SOURCE_ID,
                "notes": notes,
            }
        )

    write_csv(repo_root / NORMALIZED_RESULTS_FILE, NORMALIZED_FIELDS, rows)
    write_csv(repo_root / EXCLUDED_RESULTS_FILE, EXCLUDED_FIELDS, excluded_rows)
    return rows


def _load_shootout_winners(path: Path) -> dict[tuple[str, str, str], str]:
    winners: dict[tuple[str, str, str], str] = {}
    for row in read_csv(path):
        key = _shootout_key(row.get("date", ""), row.get("home_team", ""), row.get("away_team", ""))
        winner = row.get("winner", "")
        if key and winner:
            winners[key] = winner
    return winners


def _shootout_key(date: str, home_team: str, away_team: str) -> tuple[str, str, str]:
    return (date, normalize_name(home_team), normalize_name(away_team))


def _parse_score(value: str) -> int | None:
    try:
        return int(value)
    except ValueError:
        return None


def _derive_result(
    *,
    home_team_id: str,
    away_team_id: str,
    home_score: int,
    away_score: int,
    shootout_winner_id: str,
) -> tuple[str, str, str, float, float, str]:
    if home_score > away_score:
        return ("home_win", home_team_id, away_team_id, 1.0, 0.0, "Decisive result.")
    if away_score > home_score:
        return ("away_win", away_team_id, home_team_id, 0.0, 1.0, "Decisive result.")

    if shootout_winner_id:
        if shootout_winner_id == home_team_id:
            return ("shootout_home", home_team_id, away_team_id, 1.0, 0.0, "Draw decided by shootout.")
        if shootout_winner_id == away_team_id:
            return ("shootout_away", away_team_id, home_team_id, 0.0, 1.0, "Draw decided by shootout.")
        raise ValueError(
            f"Shootout winner '{shootout_winner_id}' is not one of '{home_team_id}' or '{away_team_id}'."
        )

    return ("draw", "", "", 0.5, 0.5, "Draw without shootout; used as expected-score target.")


def _format_target(value: float) -> str:
    return f"{value:.1f}"


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    try:
        rows = prepare_historical_results(repo_root)
    except ValueError as error:
        print(f"Historical result normalization failed: {error}")
        return 1

    print(f"Wrote {len(rows)} normalized historical matches to {NORMALIZED_RESULTS_FILE.as_posix()}.")
    print(f"Wrote explicit exclusions to {EXCLUDED_RESULTS_FILE.as_posix()}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
