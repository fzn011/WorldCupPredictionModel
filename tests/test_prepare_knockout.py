"""Tests for Step 13 knockout preparation orchestration."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.simulation.prepare_knockout import prepare_step13_knockout_simulation


def test_prepare_step13_knockout_simulation_returns_status_ok(monkeypatch) -> None:
    seeded_qualifiers = pd.DataFrame(
        {
            "team": [f"Team {i:02d}" for i in range(1, 33)],
            "group": [chr(64 + ((i - 1) % 12) + 1) for i in range(1, 33)],
            "group_rank": [1] * 32,
            "qualification_type": ["automatic_top_two"] * 24 + ["best_third_place"] * 8,
            "points": [9] * 32,
            "goal_difference": [3] * 32,
            "goals_for": [5] * 32,
            "seed": list(range(1, 33)),
            "seed_label": [f"S{i:02d}" for i in range(1, 33)],
        }
    )
    bracket_filled = pd.DataFrame(
        [
            {
                "round": "round_of_32",
                "match_id": f"R32-{i:02d}",
                "team_a": f"Team {i:02d}",
                "team_b": f"Team {33 - i:02d}",
                "source_a": f"S{i:02d}",
                "source_b": f"S{33 - i:02d}",
                "winner_to": f"R16-{(i + 1) // 2:02d}",
            }
            for i in range(1, 17)
        ]
    )
    simulated_matches = pd.DataFrame(
        [
            {
                "round": "round_of_32",
                "match_id": f"R32-{i:02d}",
                "team_a": f"Team {i:02d}",
                "team_b": f"Team {33 - i:02d}",
                "simulated_team_a_score": 1,
                "simulated_team_b_score": 0,
                "outcome_method": "regular_time",
                "winner": f"Team {i:02d}",
                "loser": f"Team {33 - i:02d}",
            }
            for i in range(1, 17)
        ]
        + [
            {
                "round": "round_of_16",
                "match_id": f"R16-{i:02d}",
                "team_a": f"Team {2 * i - 1:02d}",
                "team_b": f"Team {2 * i:02d}",
                "simulated_team_a_score": 1,
                "simulated_team_b_score": 0,
                "outcome_method": "regular_time",
                "winner": f"Team {2 * i - 1:02d}",
                "loser": f"Team {2 * i:02d}",
            }
            for i in range(1, 9)
        ]
        + [
            {
                "round": "quarter_final",
                "match_id": f"QF-{i:02d}",
                "team_a": f"Team {2 * i - 1:02d}",
                "team_b": f"Team {2 * i:02d}",
                "simulated_team_a_score": 1,
                "simulated_team_b_score": 0,
                "outcome_method": "regular_time",
                "winner": f"Team {2 * i - 1:02d}",
                "loser": f"Team {2 * i:02d}",
            }
            for i in range(1, 5)
        ]
        + [
            {
                "round": "semi_final",
                "match_id": "SF-01",
                "team_a": "Team 01",
                "team_b": "Team 02",
                "simulated_team_a_score": 1,
                "simulated_team_b_score": 0,
                "outcome_method": "regular_time",
                "winner": "Team 01",
                "loser": "Team 02",
            },
            {
                "round": "semi_final",
                "match_id": "SF-02",
                "team_a": "Team 03",
                "team_b": "Team 04",
                "simulated_team_a_score": 0,
                "simulated_team_b_score": 1,
                "outcome_method": "regular_time",
                "winner": "Team 04",
                "loser": "Team 03",
            },
            {
                "round": "third_place",
                "match_id": "TP-01",
                "team_a": "Team 02",
                "team_b": "Team 03",
                "simulated_team_a_score": 1,
                "simulated_team_b_score": 0,
                "outcome_method": "regular_time",
                "winner": "Team 02",
                "loser": "Team 03",
            },
            {
                "round": "final",
                "match_id": "F-01",
                "team_a": "Team 01",
                "team_b": "Team 04",
                "simulated_team_a_score": 2,
                "simulated_team_b_score": 1,
                "outcome_method": "regular_time",
                "winner": "Team 01",
                "loser": "Team 04",
            },
        ]
    )
    summary = {
        "status": "ok",
        "validation_passed": True,
        "champion": "Team 01",
        "runner_up": "Team 04",
        "third_place": "Team 02",
        "fourth_place": "Team 03",
        "total_knockout_matches": 32,
        "round_counts": {
            "round_of_32": 16,
            "round_of_16": 8,
            "quarter_final": 4,
            "semi_final": 2,
            "third_place": 1,
            "final": 1,
        },
    }

    monkeypatch.setattr(
        "src.simulation.prepare_knockout.simulate_knockout_stage",
        lambda **_: {
            "seeded_qualifiers": seeded_qualifiers,
            "bracket_filled": bracket_filled,
            "simulated_matches": simulated_matches,
            "champion": "Team 01",
            "runner_up": "Team 04",
            "third_place": "Team 02",
            "fourth_place": "Team 03",
            "summary": summary,
        },
    )

    out = prepare_step13_knockout_simulation(random_seed=42)
    assert out["status"] == "ok"
    assert out["validation_passed"] is True
    assert out["champion"] == "Team 01"
    assert Path(out["knockout_bracket_filled_path"]).is_file()
    assert Path(out["knockout_simulated_matches_path"]).is_file()
    assert Path(out["single_tournament_result_path"]).is_file()
    assert Path(out["validation_report_path"]).is_file()

    with Path(out["single_tournament_result_path"]).open("r", encoding="utf-8") as f:
        payload = json.load(f)
    assert payload["champion"] == "Team 01"
    assert len(payload["simulated_matches"]) == 32
