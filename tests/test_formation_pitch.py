"""Tests for Team of the Tournament pitch rendering helpers."""

from __future__ import annotations

import pandas as pd

from app.components.ui import (
    _pitch_lines_from_positions,
    _pitch_lines_from_slots,
    render_formation_pitch,
    render_team_formation,
)


def test_pitch_lines_from_slots_builds_four_rows() -> None:
    df = pd.DataFrame(
        {
            "formation_slot": ["FWD1", "MID1", "DEF1", "GK1"],
            "player_name": ["Forward One", "Mid One", "Def One", "Keeper One"],
            "team": ["Brazil", "France", "Spain", "Belgium"],
            "position_code": ["FW", "MF", "DF", "GK"],
        }
    )
    lines = _pitch_lines_from_slots(df, "player_name")
    assert len(lines) == 4
    assert lines[0][0]["name"] == "Forward One"
    assert lines[0][0]["meta"] == "Brazil · FW"
    assert lines[3][0]["name"] == "Keeper One"


def test_pitch_lines_from_positions_groups_by_role() -> None:
    df = pd.DataFrame(
        {
            "player_name": ["Striker", "Midfielder", "Defender", "Goalkeeper"],
            "team": ["Brazil", "France", "Spain", "Belgium"],
            "position_group": ["forward", "midfielder", "defender", "goalkeeper"],
            "position_code": ["FW", "MF", "DF", "GK"],
        }
    )
    lines = _pitch_lines_from_positions(df, "player_name")
    assert lines[0][0]["name"] == "Striker"
    assert lines[1][0]["name"] == "Midfielder"
    assert lines[2][0]["name"] == "Defender"
    assert lines[3][0]["name"] == "Goalkeeper"


def test_render_team_formation_accepts_dataframe_with_slots() -> None:
    df = pd.DataFrame(
        {
            "formation_slot": ["GK1"],
            "player_name": ["Player GK"],
            "team": ["Brazil"],
            "position_code": ["GK"],
        }
    )
    render_team_formation(df, name_col="player_name")
    render_formation_pitch(_pitch_lines_from_slots(df, "player_name"))
