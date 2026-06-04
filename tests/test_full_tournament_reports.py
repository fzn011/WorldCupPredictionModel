"""Tests for Step 14 full tournament reports and validation helpers."""

from __future__ import annotations

import pandas as pd

from src.simulation.full_tournament import (
    create_full_tournament_path_report,
    create_full_tournament_stage_results,
    validate_full_tournament,
)


def _minimal_group_result() -> dict:
    teams = [f"Team {i:02d}" for i in range(1, 49)]
    groups = [chr(65 + ((i - 1) % 12)) for i in range(1, 49)]
    ranks = [((i - 1) % 4) + 1 for i in range(1, 49)]
    rankings = pd.DataFrame(
        {
            "group": groups,
            "team": teams,
            "group_rank": ranks,
            "points": [9 - (r - 1) * 2 for r in ranks],
            "goal_difference": [4 - r for r in ranks],
            "goals_for": [6 - r for r in ranks],
        }
    )
    qualifiers = rankings.sort_values(["group", "group_rank"]).head(32).copy()
    qualifiers["qualification_type"] = ["automatic_top_two"] * 24 + ["best_third_place"] * 8

    return {
        "simulated_group_matches": pd.DataFrame({"match_id": [f"G-{i:03d}" for i in range(1, 73)]}),
        "group_tables": rankings,
        "group_rankings": rankings,
        "round_of_32_qualifiers": qualifiers,
        "group_validation_passed": True,
    }


def _minimal_knockout_result() -> dict:
    rows = []
    for i in range(1, 17):
        rows.append({"round": "round_of_32", "match_id": f"R32-{i:02d}", "winner": f"Team {i:02d}", "loser": f"Team {i+16:02d}"})
    for i in range(1, 9):
        rows.append({"round": "round_of_16", "match_id": f"R16-{i:02d}", "winner": f"Team {i:02d}", "loser": f"Team {i+8:02d}"})
    for i in range(1, 5):
        rows.append({"round": "quarter_final", "match_id": f"QF-{i:02d}", "winner": f"Team {i:02d}", "loser": f"Team {i+4:02d}"})
    rows.extend(
        [
            {"round": "semi_final", "match_id": "SF-01", "winner": "Team 01", "loser": "Team 02"},
            {"round": "semi_final", "match_id": "SF-02", "winner": "Team 03", "loser": "Team 04"},
            {"round": "third_place", "match_id": "TP-01", "winner": "Team 02", "loser": "Team 04"},
            {"round": "final", "match_id": "F-01", "winner": "Team 01", "loser": "Team 03"},
        ]
    )
    return {
        "knockout_simulated_matches": pd.DataFrame(rows),
        "champion": "Team 01",
        "runner_up": "Team 03",
        "third_place": "Team 02",
        "fourth_place": "Team 04",
        "knockout_validation_passed": True,
    }


def test_create_full_tournament_stage_results_returns_required_stages() -> None:
    group_result = _minimal_group_result()
    knockout_result = _minimal_knockout_result()
    stage_df = create_full_tournament_stage_results(group_result, knockout_result)
    stages = set(stage_df["stage"].tolist())
    assert {
        "group_stage",
        "round_of_32",
        "round_of_16",
        "quarter_final",
        "semi_final",
        "third_place",
        "final",
    }.issubset(stages)


def test_create_full_tournament_path_report_has_48_teams() -> None:
    group_result = _minimal_group_result()
    knockout_result = _minimal_knockout_result()
    path_df = create_full_tournament_path_report(group_result, knockout_result)
    assert len(path_df) == 48


def test_validate_full_tournament_catches_missing_champion_or_wrong_match_count() -> None:
    group_result = _minimal_group_result()
    knockout_result = _minimal_knockout_result()
    path_df = create_full_tournament_path_report(group_result, knockout_result)

    invalid_knockout = dict(knockout_result)
    invalid_knockout["champion"] = None

    invalid_match_log = pd.DataFrame({"match_id": list(range(103))})
    passed, report = validate_full_tournament(group_result, invalid_knockout, invalid_match_log, path_df)

    assert passed is False
    assert not report["passed"].all()
