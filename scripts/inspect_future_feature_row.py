"""Inspect a generated future-match feature row for diagnostics."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.features.future_match_features import generate_future_match_feature_row
import src.utils.constants as C

DEFAULT_FUTURE_MATCH_DATE = getattr(C, "DEFAULT_FUTURE_MATCH_DATE", "2026-06-11")
DEFAULT_FUTURE_TOURNAMENT = getattr(C, "DEFAULT_FUTURE_TOURNAMENT", "FIFA World Cup")
DEFAULT_FUTURE_CITY = getattr(C, "DEFAULT_FUTURE_CITY", "Unknown")
DEFAULT_FUTURE_COUNTRY = getattr(C, "DEFAULT_FUTURE_COUNTRY", "Unknown")
DEFAULT_FUTURE_NEUTRAL = getattr(C, "DEFAULT_FUTURE_NEUTRAL", 1)



def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect a Step 8 future feature row.")
    parser.add_argument("--team-a", required=True)
    parser.add_argument("--team-b", required=True)
    parser.add_argument("--date", default=DEFAULT_FUTURE_MATCH_DATE)
    parser.add_argument("--tournament", default=DEFAULT_FUTURE_TOURNAMENT)
    parser.add_argument("--city", default=DEFAULT_FUTURE_CITY)
    parser.add_argument("--country", default=DEFAULT_FUTURE_COUNTRY)
    parser.add_argument("--neutral", type=int, default=DEFAULT_FUTURE_NEUTRAL)
    return parser



def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)

    try:
        row = generate_future_match_feature_row(
            team_a=args.team_a,
            team_b=args.team_b,
            match_date=args.date,
            tournament=args.tournament,
            city=args.city,
            country=args.country,
            neutral=args.neutral,
        )
    except Exception as exc:
        print(f"[error] Could not generate future feature row: {exc}")
        return 1

    print("=== Future Feature Row Overview ===")
    print(f"Shape: {row.shape}")
    print(f"team_a: {row.iloc[0].get('team_a')}")
    print(f"team_b: {row.iloc[0].get('team_b')}")
    print(f"date: {row.iloc[0].get('date')}")
    print(f"tournament: {row.iloc[0].get('tournament')}")

    historical_cols = [
        "team_a_matches_played_before",
        "team_b_matches_played_before",
        "team_a_last_5_win_rate",
        "team_b_last_5_win_rate",
        "diff_last_5_win_rate",
        "team_a_goals_scored_avg_before",
        "team_b_goals_scored_avg_before",
        "diff_goal_diff_avg_before",
    ]

    ranking_cols = [
        "team_a_fifa_rank",
        "team_b_fifa_rank",
        "diff_fifa_rank",
        "team_a_elo",
        "team_b_elo",
        "diff_elo",
        "diff_strength_score",
    ]

    print("\n=== Selected historical features ===")
    for col in historical_cols:
        print(f"{col}: {row.iloc[0].get(col)}")

    print("\n=== Ranking/Elo features ===")
    for col in ranking_cols:
        print(f"{col}: {row.iloc[0].get(col)}")

    missing_expected = [col for col in (historical_cols + ranking_cols) if col not in row.columns]
    if missing_expected:
        print("\n[warning] Missing expected columns:")
        for col in missing_expected:
            print(f"- {col}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
