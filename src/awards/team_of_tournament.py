"""Predicted Team of the Tournament selection utilities (Step 18)."""

from __future__ import annotations

import pandas as pd

from src.awards.award_data import resolve_player_sort_column
from src.awards.player_awards import calculate_golden_ball_predictions

FORMATION_REQUIREMENTS: list[tuple[str, int, str]] = [
    ("goalkeeper", 1, "GK"),
    ("defender", 4, "DEF"),
    ("midfielder", 3, "MID"),
    ("forward", 3, "FWD"),
]


def _position_group(row: pd.Series) -> str:
    group = str(row.get("position_group", "")).strip().lower()
    if group:
        return group
    code = str(row.get("position_code", "")).strip().upper()
    mapping = {"GK": "goalkeeper", "DF": "defender", "MF": "midfielder", "FW": "forward"}
    if code in mapping:
        return mapping[code]
    return str(row.get("position", "midfielder")).strip().lower()


def select_team_of_the_tournament(golden_ball_df: pd.DataFrame) -> pd.DataFrame:
    """Select unofficial analytics 4-3-3 Team of the Tournament."""
    out = golden_ball_df.copy()
    if "final_golden_ball_score" not in out.columns:
        out = calculate_golden_ball_predictions(out)
    out["position_group"] = out.apply(_position_group, axis=1)

    picks: list[pd.DataFrame] = []
    for position, count, slot_prefix in FORMATION_REQUIREMENTS:
        position_df = out[out["position_group"] == position].copy()
        if len(position_df) < count:
            raise ValueError(
                f"Insufficient {position} players for Team of the Tournament "
                f"(need {count}, found {len(position_df)})"
            )
        sort_cols = ["final_golden_ball_score", "golden_ball_probability"]
        name_col = resolve_player_sort_column(position_df)
        sort_cols.append(name_col)
        position_df = position_df.sort_values(sort_cols, ascending=[False, False, True]).head(count).copy()
        position_df["formation_slot"] = [f"{slot_prefix}{i}" for i in range(1, count + 1)]
        picks.append(position_df)

    team_df = pd.concat(picks, ignore_index=True)
    keep_cols = [
        c
        for c in [
            "formation_slot",
            "player_id",
            "player_name",
            "player",
            "team",
            "position_group",
            "position",
            "position_code",
            "club",
            "final_golden_ball_score",
            "golden_ball_probability",
        ]
        if c in team_df.columns
    ]
    team_df = team_df[keep_cols].copy()
    team_df["position"] = team_df.get("position_group", team_df.get("position", ""))
    team_df["award"] = "Predicted Team of the Tournament"
    return team_df


def select_team_of_tournament(players_df: pd.DataFrame) -> pd.DataFrame:
    """Backward-compatible alias."""
    ball_df = players_df if "final_golden_ball_score" in players_df.columns else calculate_golden_ball_predictions(players_df)
    return select_team_of_the_tournament(ball_df)
