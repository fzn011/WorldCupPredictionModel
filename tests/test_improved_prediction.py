"""Tests for improved-model-aware prediction helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import joblib

from src.models.predict_match import (
    load_best_available_model,
    predict_from_feature_row,
    predict_match_result,
)
from src.models.train_match_model import train_baseline_models
from tests.test_train_baseline_models import _synthetic_feature_df


def test_load_best_available_model_falls_back_to_baseline_if_missing_improved(tmp_path) -> None:
    train_baseline_models(feature_df=_synthetic_feature_df(), test_start_date="2022-01-01")

    with patch("src.models.predict_match.IMPROVED_MODEL_DIR", str(tmp_path / "no_improved")):
        model, model_type = load_best_available_model(prefer_ranking=False, prefer_improved=True)
        assert model is not None
        assert model_type == "baseline"


def test_predict_from_feature_row_prefers_improved_when_available(tmp_path) -> None:
    feature_df = _synthetic_feature_df()
    train_baseline_models(feature_df=feature_df, test_start_date="2022-01-01")

    improved_dir = tmp_path / "improved"
    improved_dir.mkdir(parents=True, exist_ok=True)

    baseline_model_path = Path("models/baseline/best_baseline_model.joblib")
    baseline_columns_path = Path("models/baseline/feature_columns.json")

    improved_model_path = improved_dir / "best_improved_model.joblib"
    improved_columns_path = improved_dir / "improved_feature_columns.json"

    model = joblib.load(baseline_model_path)
    joblib.dump(model, improved_model_path)
    improved_columns_path.write_text(baseline_columns_path.read_text())

    row = feature_df.iloc[0]
    with patch("src.models.predict_match.IMPROVED_MODEL_DIR", str(improved_dir)):
        prediction = predict_from_feature_row(row, prefer_ranking=False, prefer_improved=True)

    assert prediction["model_type"] == "improved"
    assert set(prediction["probabilities"].keys()) == {"team_a_loss", "draw", "team_a_win"}


def test_predict_match_result_returns_real_future_prediction(monkeypatch) -> None:
    monkeypatch.setattr(
        "src.models.predict_match.predict_future_match",
        lambda **_: {
            "team_a": "France",
            "team_b": "Brazil",
            "model_type": "ranking_enhanced",
            "predicted_class": 2,
            "predicted_label": "team_a_win",
            "probabilities": {"team_a_loss": 0.2, "draw": 0.3, "team_a_win": 0.5},
            "notes": [],
        },
    )
    payload = predict_match_result("France", "Brazil")
    assert payload["predicted_label"] == "team_a_win"
