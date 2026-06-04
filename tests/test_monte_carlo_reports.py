"""Tests for Step 15 Monte Carlo report builders."""

from __future__ import annotations

import pandas as pd

from src.simulation.monte_carlo import (
    build_finalists_table,
    build_semifinalists_table,
    build_team_stage_counts,
    build_team_stage_probabilities,
)


def _synthetic_path_reports() -> list[dict]:
    sim1 = pd.DataFrame(
        {
            "team": ["A", "B", "C", "D"],
            "reached_round": ["final", "final", "semi_final", "quarter_final"],
            "final_position": ["champion", "runner_up", "third_place", "eliminated_quarter_final"],
        }
    )
    sim2 = pd.DataFrame(
        {
            "team": ["A", "B", "C", "D"],
            "reached_round": ["round_of_16", "semi_final", "final", "final"],
            "final_position": ["eliminated_round_of_16", "fourth_place", "runner_up", "champion"],
        }
    )
    return [
        {"simulation_id": 1, "path_report": sim1},
        {"simulation_id": 2, "path_report": sim2},
    ]


def test_build_team_stage_counts_with_synthetic_reports() -> None:
    counts = build_team_stage_counts(_synthetic_path_reports())
    assert not counts.empty
    assert {"team", "champion_count", "final_count"}.issubset(set(counts.columns))


def test_build_team_stage_probabilities_computes_probabilities() -> None:
    counts = build_team_stage_counts(_synthetic_path_reports())
    probs = build_team_stage_probabilities(counts, successful_simulations=2)
    assert not probs.empty
    assert ((probs["champion_probability"] >= 0) & (probs["champion_probability"] <= 1)).all()


def test_build_finalists_and_semifinalists_tables_created() -> None:
    simulation_results_df = pd.DataFrame(
        {
            "status": ["success", "success"],
            "champion": ["A", "D"],
            "runner_up": ["B", "C"],
        }
    )
    finalists = build_finalists_table(simulation_results_df)
    semifinalists = build_semifinalists_table(_synthetic_path_reports(), successful_simulations=2)

    assert not finalists.empty
    assert not semifinalists.empty
