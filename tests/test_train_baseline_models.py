"""Tests for training the Step 5 baseline models."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.models.train_match_model import train_baseline_models


def _synthetic_feature_df() -> pd.DataFrame:
    rows = []
    dates = pd.to_datetime(
        [
            "2021-01-01",
            "2021-02-01",
            "2021-03-01",
            "2021-04-01",
            "2022-01-01",
            "2022-02-01",
            "2022-03-01",
            "2022-04-01",
        ]
    )
    results = [0, 1, 2, 0, 1, 2, 0, 1]
    teams = [
        ("A", "B"),
        ("C", "D"),
        ("E", "F"),
        ("G", "H"),
        ("A", "C"),
        ("B", "D"),
        ("E", "G"),
        ("F", "H"),
    ]
    for i, (date, result, (team_a, team_b)) in enumerate(zip(dates, results, teams), start=1):
        rows.append(
            {
                "match_id": f"m{i}",
                "date": date,
                "year": date.year,
                "team_a": team_a,
                "team_b": team_b,
                "tournament": "Friendly" if i % 2 else "FIFA World Cup",
                "city": "City",
                "country": "Country",
                "data_source": "test",
                "team_a_score": int(result == 2),
                "team_b_score": int(result == 0),
                "score_difference": 0,
                "total_goals": 1,
                "winner": team_a if result == 2 else team_b if result == 0 else pd.NA,
                "loser": team_b if result == 2 else team_a if result == 0 else pd.NA,
                "is_draw": int(result == 1),
                "has_shootout": 0,
                "shootout_winner": pd.NA,
                "shootout_loser": pd.NA,
                "progression_winner": team_a if result == 2 else team_b if result == 0 else pd.NA,
                "result": result,
                "result_label": {0: "team_a_loss", 1: "draw", 2: "team_a_win"}[result],
                "team_a_last_5_win_rate": 0.1 + i * 0.01,
                "team_b_last_5_win_rate": 0.2 + i * 0.01,
                "diff_last_5_win_rate": -0.1,
                "team_a_points_per_match_before": 1.0 + i * 0.1,
                "team_b_points_per_match_before": 0.8 + i * 0.1,
                "diff_points_per_match_before": 0.2,
                "team_a_is_host_2026": int(team_a in {"Canada", "Mexico", "United States"}),
                "team_b_is_host_2026": int(team_b in {"Canada", "Mexico", "United States"}),
                "is_world_cup": int("World Cup" in ("Friendly" if i % 2 else "FIFA World Cup")),
                "is_friendly": int(i % 2 == 1),
            }
        )
    return pd.DataFrame(rows)


def test_train_baseline_models_returns_ok_summary() -> None:
    summary = train_baseline_models(feature_df=_synthetic_feature_df(), test_start_date="2022-01-01")
    assert summary["status"] == "ok"
    assert summary["train_rows"] > 0
    assert summary["test_rows"] > 0
    assert summary["feature_count"] > 0


def test_train_baseline_models_saves_artifacts() -> None:
    summary = train_baseline_models(feature_df=_synthetic_feature_df(), test_start_date="2022-01-01")
    assert Path(summary["best_model_path"]).is_file()
    assert Path(summary["model_metrics_path"]).is_file()
    assert Path(summary["feature_columns_path"]).is_file()

    metadata_path = Path("models/baseline/model_metadata.json")
    assert metadata_path.is_file()
    metadata = json.loads(metadata_path.read_text())
    assert metadata["best_model_name"] in {"dummy", "logistic_regression", "random_forest"}
