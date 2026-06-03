"""Tests for Step 7 ranking-enhanced model training."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.models.train_ranking_enhanced_model import train_ranking_enhanced_model
from tests.test_train_baseline_models import _synthetic_feature_df


def _synthetic_ranking_feature_df() -> pd.DataFrame:
    df = _synthetic_feature_df().copy()
    df["team_a_fifa_rank"] = [1, 2, 3, 4, 5, 6, 7, 8]
    df["team_b_fifa_rank"] = [6, 5, 4, 3, 2, 1, 8, 7]
    df["diff_fifa_rank"] = df["team_b_fifa_rank"] - df["team_a_fifa_rank"]
    df["team_a_fifa_points"] = [1877.0, 1850.0, 1800.0, 1780.0, 1760.0, 1740.0, 1720.0, 1700.0]
    df["team_b_fifa_points"] = [1761.0, 1770.0, 1780.0, 1790.0, 1800.0, 1810.0, 1690.0, 1680.0]
    df["diff_fifa_points"] = df["team_a_fifa_points"] - df["team_b_fifa_points"]
    df["team_a_elo_rank"] = [3, 4, 5, 6, 7, 8, 9, 10]
    df["team_b_elo_rank"] = [8, 7, 6, 5, 4, 3, 11, 12]
    df["diff_elo_rank"] = df["team_b_elo_rank"] - df["team_a_elo_rank"]
    df["team_a_elo"] = [2081, 2050, 2020, 2000, 1980, 1960, 1940, 1920]
    df["team_b_elo"] = [1984, 1990, 2000, 2010, 2020, 2030, 1900, 1890]
    df["diff_elo"] = df["team_a_elo"] - df["team_b_elo"]
    df["team_a_has_fifa_ranking"] = 1
    df["team_b_has_fifa_ranking"] = 1
    df["team_a_has_elo"] = 1
    df["team_b_has_elo"] = 1
    df["team_a_strength_score"] = [0.9, 0.85, 0.8, 0.78, 0.76, 0.74, 0.72, 0.7]
    df["team_b_strength_score"] = [0.72, 0.74, 0.76, 0.78, 0.8, 0.82, 0.68, 0.66]
    df["diff_strength_score"] = df["team_a_strength_score"] - df["team_b_strength_score"]
    return df


def test_train_ranking_enhanced_model_status_ok() -> None:
    summary = train_ranking_enhanced_model(
        ranking_feature_df=_synthetic_ranking_feature_df(),
        test_start_date="2022-01-01",
    )
    assert summary["status"] == "ok"
    assert summary["train_rows"] > 0
    assert summary["test_rows"] > 0


def test_train_ranking_enhanced_model_artifacts_exist() -> None:
    summary = train_ranking_enhanced_model(
        ranking_feature_df=_synthetic_ranking_feature_df(),
        test_start_date="2022-01-01",
    )
    assert Path(summary["best_model_path"]).is_file()
    assert Path(summary["ranking_metrics_path"]).is_file()
    metadata_path = Path("models/ranking_enhanced/ranking_model_metadata.json")
    assert metadata_path.is_file()
    metadata = json.loads(metadata_path.read_text())
    assert metadata["best_model_name"]
