"""Tests for Step 18 team of the tournament selection."""

from __future__ import annotations

import pandas as pd
import pytest

from src.awards.team_of_tournament import select_team_of_the_tournament


def _players() -> pd.DataFrame:
    rows = []
    for i in range(4):
        rows.append({"player_id": f"d{i}", "player_name": f"D{i}", "team": "X", "position_code": "DF", "position_group": "defender", "final_golden_ball_score": 10 - i, "golden_ball_probability": 0.1})
    for i in range(3):
        rows.append({"player_id": f"m{i}", "player_name": f"M{i}", "team": "X", "position_code": "MF", "position_group": "midfielder", "final_golden_ball_score": 9 - i, "golden_ball_probability": 0.1})
    for i in range(3):
        rows.append({"player_id": f"f{i}", "player_name": f"F{i}", "team": "X", "position_code": "FW", "position_group": "forward", "final_golden_ball_score": 8 - i, "golden_ball_probability": 0.1})
    rows.append({"player_id": "g1", "player_name": "G1", "team": "X", "position_code": "GK", "position_group": "goalkeeper", "final_golden_ball_score": 7, "golden_ball_probability": 0.1})
    return pd.DataFrame(rows)


def test_select_team_of_the_tournament_returns_11_players():
    xi = select_team_of_the_tournament(_players())
    assert len(xi) == 11


def test_select_team_of_the_tournament_formation():
    xi = select_team_of_the_tournament(_players())
    counts = xi["position_group"].value_counts()
    assert counts["goalkeeper"] == 1
    assert counts["defender"] == 4
    assert counts["midfielder"] == 3
    assert counts["forward"] == 3


def test_select_team_of_the_tournament_raises_when_insufficient():
    with pytest.raises(ValueError):
        select_team_of_the_tournament(_players().head(5))
