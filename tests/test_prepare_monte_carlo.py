"""Tests for Step 15 Monte Carlo preparation orchestrator."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

from src.simulation.prepare_monte_carlo import prepare_step15_monte_carlo_simulation


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


@lru_cache(maxsize=1)
def _prepare_once() -> dict:
    return prepare_step15_monte_carlo_simulation(
        num_simulations=2,
        base_seed=42,
        predictor=_FakePredictor(),
    )


def test_prepare_step15_monte_carlo_returns_status_ok() -> None:
    summary = _prepare_once()
    assert summary["status"] == "ok"


def test_prepare_step15_monte_carlo_output_files_exist() -> None:
    summary = _prepare_once()
    assert Path(summary["simulation_results_path"]).is_file()
    assert Path(summary["team_stage_probabilities_path"]).is_file()
    assert Path(summary["champion_probabilities_path"]).is_file()
    assert Path(summary["finalists_path"]).is_file()
    assert Path(summary["semifinalists_path"]).is_file()
    assert Path(summary["summary_path"]).is_file()
    assert Path(summary["validation_report_path"]).is_file()


def test_prepare_step15_monte_carlo_validation_report_exists() -> None:
    summary = _prepare_once()
    report_df = pd.read_csv(summary["validation_report_path"])
    assert not report_df.empty
