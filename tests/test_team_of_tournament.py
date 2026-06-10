"""Tests for Step 17 Team of the Tournament selection."""

from __future__ import annotations

import pandas as pd

from src.awards.team_of_tournament import select_team_of_tournament


def _players_df() -> pd.DataFrame:
    rows = []
    for idx in range(1, 3):
        rows.append({"player": f"GK {idx}", "team": "France", "position": "goalkeeper", "final_golden_ball_score": 90 - idx, "golden_ball_probability": 0.05})
    for idx in range(1, 6):
        rows.append({"player": f"DEF {idx}", "team": "England", "position": "defender", "final_golden_ball_score": 80 - idx, "golden_ball_probability": 0.04})
    for idx in range(1, 5):
        rows.append({"player": f"MID {idx}", "team": "Spain", "position": "midfielder", "final_golden_ball_score": 85 - idx, "golden_ball_probability": 0.05})
    for idx in range(1, 5):
        rows.append({"player": f"FWD {idx}", "team": "Brazil", "position": "forward", "final_golden_ball_score": 88 - idx, "golden_ball_probability": 0.06})
    return pd.DataFrame(rows)


def test_select_team_of_tournament_returns_11_players() -> None:
    out = select_team_of_tournament(_players_df())
    assert len(out) == 11


def test_formation_has_expected_position_counts() -> None:
    out = select_team_of_tournament(_players_df())
    counts = out["position"].value_counts().to_dict()
    assert counts.get("goalkeeper", 0) == 1
    assert counts.get("defender", 0) == 4
    assert counts.get("midfielder", 0) == 3
    assert counts.get("forward", 0) == 3
