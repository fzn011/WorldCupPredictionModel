"""Tests for Step 13 knockout validation rules."""

from __future__ import annotations

import pandas as pd

from src.simulation.knockout_stage import validate_knockout_simulation


def _valid_knockout_matches() -> pd.DataFrame:
    rows = []
    for i in range(1, 17):
        rows.append(
            {
                "round": "round_of_32",
                "match_id": f"R32-{i:02d}",
                "winner": f"Team {i:02d}",
            }
        )
    for i in range(1, 9):
        rows.append(
            {
                "round": "round_of_16",
                "match_id": f"R16-{i:02d}",
                "winner": f"Team {i:02d}",
            }
        )
    for i in range(1, 5):
        rows.append(
            {
                "round": "quarter_final",
                "match_id": f"QF-{i:02d}",
                "winner": f"Team {i:02d}",
            }
        )
    rows.extend(
        [
            {"round": "semi_final", "match_id": "SF-01", "winner": "Team 01"},
            {"round": "semi_final", "match_id": "SF-02", "winner": "Team 02"},
            {"round": "third_place", "match_id": "TP-01", "winner": "Team 03"},
            {"round": "final", "match_id": "F-01", "winner": "Team 01"},
        ]
    )
    return pd.DataFrame(rows)


def test_validate_knockout_simulation_passes_for_valid_synthetic_result() -> None:
    matches = _valid_knockout_matches()
    passed, report = validate_knockout_simulation(
        matches,
        {
            "champion": "Team 01",
            "runner_up": "Team 02",
            "third_place": "Team 03",
            "fourth_place": "Team 04",
        },
    )
    assert passed is True
    assert report["passed"].all()


def test_validate_knockout_simulation_fails_when_champion_missing() -> None:
    matches = _valid_knockout_matches()
    passed, report = validate_knockout_simulation(
        matches,
        {
            "champion": None,
            "runner_up": "Team 02",
            "third_place": "Team 03",
            "fourth_place": "Team 04",
        },
    )
    assert passed is False
    assert not report["passed"].all()


def test_validate_knockout_simulation_fails_when_counts_are_wrong() -> None:
    matches = _valid_knockout_matches().iloc[:-1].copy()
    passed, report = validate_knockout_simulation(
        matches,
        {
            "champion": "Team 01",
            "runner_up": "Team 02",
            "third_place": "Team 03",
            "fourth_place": "Team 04",
        },
    )
    assert passed is False
    assert not report["passed"].all()
