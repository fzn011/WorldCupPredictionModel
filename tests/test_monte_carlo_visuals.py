"""Tests for Step 16 Monte Carlo plotting utilities."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.reports.monte_carlo_visuals import (
    plot_champion_probabilities,
    plot_stage_probability_heatmap,
)


def test_plot_champion_probabilities_creates_png(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {
            "team": ["France", "Brazil"],
            "champion_count": [2, 1],
            "champion_probability": [0.2, 0.1],
        }
    )
    path = plot_champion_probabilities(df, top_n=2, output_path=str(tmp_path / "champions.png"))
    assert Path(path).is_file()


def test_plot_stage_probability_heatmap_creates_png(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {
            "team": ["France", "Brazil"],
            "round_of_32_probability": [1.0, 1.0],
            "round_of_16_probability": [0.8, 0.7],
            "quarter_final_probability": [0.5, 0.4],
            "semi_final_probability": [0.3, 0.2],
            "final_probability": [0.2, 0.1],
            "champion_probability": [0.2, 0.1],
        }
    )
    path = plot_stage_probability_heatmap(df, top_n=2, output_path=str(tmp_path / "heatmap.png"))
    assert Path(path).is_file()
