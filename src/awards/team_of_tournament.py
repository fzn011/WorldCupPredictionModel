"""Predicted Team of the Tournament selection utilities."""

from __future__ import annotations

import pandas as pd

from src.awards.player_awards import calculate_golden_ball_predictions

FORMATION_REQUIREMENTS: list[tuple[str, int, str]] = [
    ("goalkeeper", 1, "GK"),
    ("defender", 4, "DEF"),
    ("midfielder", 3, "MID"),
    ("forward", 3, "FWD"),
]


def select_team_of_tournament(players_df: pd.DataFrame) -> pd.DataFrame:
    """Select an unofficial analytics 4-3-3 Team of the Tournament."""
    out = players_df.copy()
    if "final_golden_ball_score" not in out.columns or "golden_ball_probability" not in out.columns:
        out = calculate_golden_ball_predictions(out)

    picks: list[pd.DataFrame] = []
    for position, count, slot_prefix in FORMATION_REQUIREMENTS:
        position_df = out[out["position"].astype(str).str.lower() == position].copy()
        position_df = position_df.sort_values(["final_golden_ball_score", "golden_ball_probability", "player"], ascending=[False, False, True]).head(count).copy()
        position_df["formation_slot"] = [f"{slot_prefix}{i}" for i in range(1, len(position_df) + 1)]
        picks.append(position_df)

    team_df = pd.concat(picks, ignore_index=True) if picks else pd.DataFrame()
    if not team_df.empty:
        keep_cols = [
            col
            for col in [
                "player",
                "team",
                "position",
                "formation_slot",
                "final_golden_ball_score",
                "golden_ball_probability",
            ]
            if col in team_df.columns
        ]
        team_df = team_df[keep_cols].copy()
        team_df["award"] = "Predicted Team of the Tournament"
    return team_df
