"""Tests for Step 16 Monte Carlo report preparation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.reports import monte_carlo_report as report_mod
from src.reports import monte_carlo_visuals as visuals_mod
from src.reports.prepare_monte_carlo_report import prepare_step16_monte_carlo_report


def _synthetic_outputs() -> dict:
    return {
        "simulation_results": pd.DataFrame({"simulation_id": [1, 2], "status": ["success", "success"]}),
        "team_stage_probabilities": pd.DataFrame(
            {
                "team": ["France", "Brazil"],
                "round_of_32_probability": [1.0, 1.0],
                "round_of_16_probability": [0.8, 0.7],
                "quarter_final_probability": [0.5, 0.4],
                "semi_final_probability": [0.3, 0.2],
                "final_probability": [0.2, 0.1],
                "champion_probability": [0.2, 0.1],
            }
        ),
        "champion_probabilities": pd.DataFrame(
            {
                "team": ["France", "Brazil"],
                "champion_count": [2, 1],
                "champion_probability": [0.2, 0.1],
            }
        ),
        "finalists": pd.DataFrame({"team": ["France"], "final_appearance_probability": [0.2]}),
        "semifinalists": pd.DataFrame({"team": ["France"], "semifinal_probability": [0.3]}),
        "summary": {
            "num_simulations": 10,
            "successful_simulations": 10,
            "failed_simulations": 0,
            "validation_passed": True,
            "top_champion": "France",
            "top_champion_probability": 0.2,
            "top_finalist": "France",
            "cache_info": {"cache_hits": 5, "cache_misses": 3},
        },
        "validation_report": pd.DataFrame({"check": ["ok"], "passed": [True]}),
    }


def test_prepare_step16_monte_carlo_report_returns_status_ok(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("src.reports.prepare_monte_carlo_report.load_monte_carlo_outputs", lambda: _synthetic_outputs())
    monkeypatch.setattr(report_mod, "REPORTS_DIR", tmp_path)
    monkeypatch.setattr(visuals_mod, "REPORTS_DIR", tmp_path)
    monkeypatch.setattr(visuals_mod, "FIGURES_DIR", tmp_path / "figures")

    summary = prepare_step16_monte_carlo_report()

    assert summary["status"] == "ok"
    assert Path(summary["report_path"]).is_file()
    assert Path(summary["summary_cards_path"]).is_file()
    assert Path(summary["dashboard_export_path"]).is_file()
    assert Path(summary["champion_chart_path"]).is_file()
    assert Path(summary["stage_heatmap_path"]).is_file()
