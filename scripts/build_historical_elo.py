"""Reconstruct historical pre-match Elo features from normalized results."""

from __future__ import annotations

from pathlib import Path

from scripts.historical_model import (
    ELO_FORMULA_VERSION,
    ELO_TIMESERIES_FILE,
    INITIAL_ELO,
    K_FACTOR,
    MATCH_FEATURES_FILE,
    NORMALIZED_RESULTS_FILE,
    SOURCE_ID,
    read_csv,
    simple_elo_probability_from_diff,
    write_csv,
)
from scripts.prepare_historical_results import prepare_historical_results


TIMESERIES_FIELDS = [
    "match_id",
    "date",
    "match_index",
    "team_id",
    "pre_match_elo",
    "post_match_elo",
    "opponent_team_id",
    "opponent_pre_match_elo",
    "target",
    "tournament",
    "neutral",
    "result_type",
    "elo_formula_version",
    "source_id",
]

FEATURE_FIELDS = [
    "match_id",
    "date",
    "team_a",
    "team_b",
    "rating_a_pre",
    "rating_b_pre",
    "rating_diff_a_minus_b",
    "target_a",
    "target_b",
    "tournament",
    "neutral",
    "source_match_id",
    "result_type",
    "notes",
]


def build_historical_elo(repo_root: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    normalized_path = repo_root / NORMALIZED_RESULTS_FILE
    if not normalized_path.exists():
        prepare_historical_results(repo_root)

    normalized_rows = sorted(
        read_csv(normalized_path),
        key=lambda row: (row["date"], row["match_id"]),
    )
    ratings: dict[str, float] = {}
    timeseries_rows: list[dict[str, str]] = []
    feature_rows: list[dict[str, str]] = []

    for match_index, row in enumerate(normalized_rows, start=1):
        team_a = row["home_team_id"]
        team_b = row["away_team_id"]
        target_a = float(row["home_result"])
        target_b = float(row["away_result"])
        rating_a_pre = ratings.get(team_a, INITIAL_ELO)
        rating_b_pre = ratings.get(team_b, INITIAL_ELO)
        expected_a = simple_elo_probability_from_diff(rating_a_pre - rating_b_pre)
        expected_b = 1 - expected_a
        rating_a_post = rating_a_pre + K_FACTOR * (target_a - expected_a)
        rating_b_post = rating_b_pre + K_FACTOR * (target_b - expected_b)

        ratings[team_a] = rating_a_post
        ratings[team_b] = rating_b_post

        feature_rows.append(
            {
                "match_id": row["match_id"],
                "date": row["date"],
                "team_a": team_a,
                "team_b": team_b,
                "rating_a_pre": _format_rating(rating_a_pre),
                "rating_b_pre": _format_rating(rating_b_pre),
                "rating_diff_a_minus_b": _format_rating(rating_a_pre - rating_b_pre),
                "target_a": _format_target(target_a),
                "target_b": _format_target(target_b),
                "tournament": row["tournament"],
                "neutral": row["neutral"],
                "source_match_id": row["source_match_id"],
                "result_type": row["result_type"],
                "notes": row["notes"],
            }
        )

        timeseries_rows.extend(
            [
                _build_timeseries_row(
                    row=row,
                    match_index=match_index,
                    team_id=team_a,
                    opponent_team_id=team_b,
                    pre=rating_a_pre,
                    post=rating_a_post,
                    opponent_pre=rating_b_pre,
                    target=target_a,
                ),
                _build_timeseries_row(
                    row=row,
                    match_index=match_index,
                    team_id=team_b,
                    opponent_team_id=team_a,
                    pre=rating_b_pre,
                    post=rating_b_post,
                    opponent_pre=rating_a_pre,
                    target=target_b,
                ),
            ]
        )

    write_csv(repo_root / ELO_TIMESERIES_FILE, TIMESERIES_FIELDS, timeseries_rows)
    write_csv(repo_root / MATCH_FEATURES_FILE, FEATURE_FIELDS, feature_rows)
    return timeseries_rows, feature_rows


def _build_timeseries_row(
    *,
    row: dict[str, str],
    match_index: int,
    team_id: str,
    opponent_team_id: str,
    pre: float,
    post: float,
    opponent_pre: float,
    target: float,
) -> dict[str, str]:
    return {
        "match_id": row["match_id"],
        "date": row["date"],
        "match_index": str(match_index),
        "team_id": team_id,
        "pre_match_elo": _format_rating(pre),
        "post_match_elo": _format_rating(post),
        "opponent_team_id": opponent_team_id,
        "opponent_pre_match_elo": _format_rating(opponent_pre),
        "target": _format_target(target),
        "tournament": row["tournament"],
        "neutral": row["neutral"],
        "result_type": row["result_type"],
        "elo_formula_version": ELO_FORMULA_VERSION,
        "source_id": SOURCE_ID,
    }


def _format_rating(value: float) -> str:
    return f"{value:.6f}"


def _format_target(value: float) -> str:
    return f"{value:.1f}"


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    try:
        timeseries_rows, feature_rows = build_historical_elo(repo_root)
    except ValueError as error:
        print(f"Historical Elo reconstruction failed: {error}")
        return 1

    print(f"Wrote {len(timeseries_rows)} Elo time-series rows to {ELO_TIMESERIES_FILE.as_posix()}.")
    print(f"Wrote {len(feature_rows)} match feature rows to {MATCH_FEATURES_FILE.as_posix()}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
