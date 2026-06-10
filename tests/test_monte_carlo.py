"""Tests for Step 15 Monte Carlo simulation core utilities."""

from __future__ import annotations

import pandas as pd

from src.simulation import monte_carlo as mc


class _FakePredictor:
    def __init__(self) -> None:
        self.requests = 0

    def predict(self, **kwargs):
        self.requests += 1
        return {
            "model_type": "fake",
            "predicted_label": "team_a_win",
            "probabilities": {
                "team_a_loss": 0.25,
                "draw": 0.25,
                "team_a_win": 0.50,
            },
        }

    def cache_info(self) -> dict:
        return {
            "total_requests": self.requests,
            "cache_hits": 0,
            "cache_misses": self.requests,
            "cache_size": self.requests,
        }


def test_run_single_tournament_for_monte_carlo_returns_expected_keys(monkeypatch) -> None:
    def _fake_run_full_tournament_single(random_seed: int, predictor=None) -> dict:
        return {
            "summary": {
                "validation_passed": True,
                "champion": "A",
                "runner_up": "B",
                "third_place": "C",
                "fourth_place": "D",
            },
            "path_report": pd.DataFrame({"team": ["A"], "reached_round": ["final"], "final_position": ["champion"]}),
            "stage_results": pd.DataFrame({"stage": ["final"], "matches": [1]}),
        }

    monkeypatch.setattr(mc, "run_full_tournament_single", _fake_run_full_tournament_single)
    result = mc.run_single_tournament_for_monte_carlo(simulation_id=1, random_seed=42)

    assert {
        "simulation_id",
        "random_seed",
        "status",
        "validation_passed",
        "champion",
        "runner_up",
        "third_place",
        "fourth_place",
        "summary",
        "path_report",
        "stage_results",
        "error_message",
    }.issubset(set(result.keys()))
    assert result["status"] == "success"


def test_build_simulation_results_table_has_one_row_per_simulation() -> None:
    rows = [
        {
            "simulation_id": 1,
            "random_seed": 43,
            "status": "success",
            "validation_passed": True,
            "champion": "A",
            "runner_up": "B",
            "third_place": "C",
            "fourth_place": "D",
            "error_message": None,
        },
        {
            "simulation_id": 2,
            "random_seed": 44,
            "status": "failed",
            "validation_passed": False,
            "champion": None,
            "runner_up": None,
            "third_place": None,
            "fourth_place": None,
            "error_message": "boom",
        },
    ]
    df = mc.build_simulation_results_table(rows)
    assert len(df) == 2


def test_build_champion_probabilities_are_between_0_and_1() -> None:
    df = pd.DataFrame(
        {
            "status": ["success", "success", "success"],
            "champion": ["A", "B", "A"],
        }
    )
    champ_df = mc.build_champion_probabilities(df)
    assert not champ_df.empty
    assert ((champ_df["champion_probability"] >= 0) & (champ_df["champion_probability"] <= 1)).all()


def test_validate_monte_carlo_outputs_passes_valid_synthetic_data() -> None:
    simulation_results_df = pd.DataFrame(
        {
            "status": ["success", "success"],
            "champion": ["A", "B"],
        }
    )
    team_stage_probabilities_df = pd.DataFrame(
        {
            "team": ["A", "B"],
            "champion_probability": [0.5, 0.5],
        }
    )
    champion_probabilities_df = pd.DataFrame(
        {
            "team": ["A", "B"],
            "champion_count": [1, 1],
            "champion_probability": [0.5, 0.5],
        }
    )

    passed, report = mc.validate_monte_carlo_outputs(
        simulation_results_df=simulation_results_df,
        team_stage_probabilities_df=team_stage_probabilities_df,
        champion_probabilities_df=champion_probabilities_df,
        num_simulations=2,
    )

    assert passed is True
    assert not report.empty


def test_create_monte_carlo_summary_returns_expected_keys() -> None:
    simulation_results_df = pd.DataFrame(
        {
            "status": ["success", "failed"],
            "champion": ["A", None],
        }
    )
    champion_probabilities_df = pd.DataFrame(
        {
            "team": ["A"],
            "champion_count": [1],
            "champion_probability": [1.0],
        }
    )
    team_stage_probabilities_df = pd.DataFrame(
        {
            "team": ["A"],
            "final_probability": [1.0],
            "champion_probability": [1.0],
        }
    )

    summary = mc.create_monte_carlo_summary(
        simulation_results_df=simulation_results_df,
        champion_probabilities_df=champion_probabilities_df,
        team_stage_probabilities_df=team_stage_probabilities_df,
        validation_passed=True,
        num_simulations=2,
        base_seed=42,
    )

    assert {
        "status",
        "num_simulations",
        "successful_simulations",
        "failed_simulations",
        "base_seed",
        "validation_passed",
        "top_champion",
        "top_champion_probability",
        "top_finalist",
        "cache_info",
        "notes",
    }.issubset(set(summary.keys()))


def test_run_monte_carlo_simulations_uses_predictor_and_exposes_cache(monkeypatch) -> None:
    def _fake_run_full_tournament_single(random_seed: int, predictor=None) -> dict:
        team_a = f"Team{random_seed}A"
        team_b = f"Team{random_seed}B"
        if predictor is not None:
            predictor.predict(team_a=team_a, team_b=team_b, match_date="2026-06-11")
        return {
            "summary": {
                "validation_passed": True,
                "champion": team_a,
                "runner_up": team_b,
                "third_place": "T3",
                "fourth_place": "T4",
            },
            "path_report": pd.DataFrame(
                {
                    "team": [team_a, team_b],
                    "reached_round": ["final", "final"],
                    "final_position": ["champion", "runner_up"],
                }
            ),
            "stage_results": pd.DataFrame({"stage": ["final"], "matches": [1]}),
        }

    monkeypatch.setattr(mc, "run_full_tournament_single", _fake_run_full_tournament_single)
    fake_predictor = _FakePredictor()

    result = mc.run_monte_carlo_simulations(num_simulations=3, base_seed=42, predictor=fake_predictor)

    assert len(result["simulation_results"]) == 3
    assert result["cache_info"]["total_requests"] == 3
