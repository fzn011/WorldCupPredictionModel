"""Tests for Step 7 ranking-aware prediction behavior."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import joblib
import pandas as pd

from src.models.predict_match import (
    load_best_available_model,
    predict_existing_match_by_id,
    predict_match_result,
)
from src.models.train_match_model import train_baseline_models
from tests.test_train_baseline_models import _synthetic_feature_df


def test_load_best_available_model_prefers_ranking_when_present(tmp_path) -> None:
    train_baseline_models(feature_df=_synthetic_feature_df(), test_start_date="2022-01-01")

    ranking_dir = tmp_path / "ranking"
    ranking_dir.mkdir(parents=True, exist_ok=True)
    baseline_model = joblib.load(Path("models/baseline/best_baseline_model.joblib"))
    joblib.dump(baseline_model, ranking_dir / "best_ranking_enhanced_model.joblib")

    with patch("src.models.predict_match.RANKING_ENHANCED_MODEL_DIR", str(ranking_dir)):
        model, model_type = load_best_available_model(prefer_ranking=True, prefer_improved=False)

    assert model is not None
    assert model_type == "ranking_enhanced"


def test_predict_existing_match_uses_ranking_dataset_when_available(tmp_path) -> None:
    feature_df = _synthetic_feature_df()
    train_baseline_models(feature_df=feature_df, test_start_date="2022-01-01")

    ranking_dir = tmp_path / "ranking"
    ranking_dir.mkdir(parents=True, exist_ok=True)
    baseline_model = joblib.load(Path("models/baseline/best_baseline_model.joblib"))
    joblib.dump(baseline_model, ranking_dir / "best_ranking_enhanced_model.joblib")

    processed_dir = tmp_path / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    ranking_df = feature_df.copy()
    ranking_df.to_csv(processed_dir / "ranking_feature_dataset.csv", index=False)

    with patch("src.models.predict_match.RANKING_ENHANCED_MODEL_DIR", str(ranking_dir)), \
         patch("src.models.predict_match.PROCESSED_DATA_DIR", processed_dir):
        result = predict_existing_match_by_id("m1")

    assert result["match_id"] == "m1"
    assert result["model_type"] == "ranking_enhanced"


def test_predict_match_result_calls_future_prediction(monkeypatch) -> None:
    monkeypatch.setattr(
        "src.models.predict_match.predict_future_match",
        lambda **_: {
            "team_a": "France",
            "team_b": "Brazil",
            "model_type": "ranking_enhanced",
            "predicted_class": 2,
            "predicted_label": "team_a_win",
            "probabilities": {"team_a_loss": 0.2, "draw": 0.2, "team_a_win": 0.6},
            "notes": [],
        },
    )
    out = predict_match_result("France", "Brazil")
    assert out["model_type"] == "ranking_enhanced"
