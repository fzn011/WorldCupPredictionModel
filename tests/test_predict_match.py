"""Tests for the baseline prediction helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from src.models.predict_match import (
    load_baseline_model,
    load_best_available_model,
    predict_existing_match_by_id,
    predict_from_feature_row,
)
from src.models.train_match_model import train_baseline_models
from tests.test_train_baseline_models import _synthetic_feature_df

BASELINE_MODEL_PATH = "models/baseline/best_baseline_model.joblib"
BASELINE_FEATURE_COLUMNS_PATH = "models/baseline/feature_columns.json"


def _clear_preferred_model_artifacts() -> None:
    """Remove ranking/improved artifacts so baseline-only tests stay isolated."""
    for rel in (
        "models/ranking_enhanced/best_ranking_enhanced_model.joblib",
        "models/ranking_enhanced/ranking_feature_columns.json",
        "models/improved/best_improved_model.joblib",
        "models/improved/improved_feature_columns.json",
    ):
        path = Path(rel)
        if path.is_file():
            path.unlink()


def test_load_baseline_model_raises_clear_error_for_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        load_baseline_model(model_path="models/baseline/does_not_exist.joblib")


def test_load_best_available_model_reuses_cached_instance() -> None:
    train_baseline_models(feature_df=_synthetic_feature_df(), test_start_date="2022-01-01")
    _clear_preferred_model_artifacts()
    first_model, first_type = load_best_available_model(prefer_ranking=False, prefer_improved=False)
    second_model, second_type = load_best_available_model(prefer_ranking=False, prefer_improved=False)
    assert first_type == "baseline"
    assert second_type == "baseline"
    assert first_model is second_model


def test_predict_from_feature_row_returns_probability_keys() -> None:
    train_baseline_models(feature_df=_synthetic_feature_df(), test_start_date="2022-01-01")
    _clear_preferred_model_artifacts()
    row = _synthetic_feature_df().iloc[0]
    prediction = predict_from_feature_row(
        row,
        model_path=BASELINE_MODEL_PATH,
        feature_columns_path=BASELINE_FEATURE_COLUMNS_PATH,
    )
    assert "predicted_class" in prediction
    assert "predicted_label" in prediction
    assert set(prediction["probabilities"].keys()) == {"team_a_loss", "draw", "team_a_win"}


def test_predict_existing_match_by_id_works_with_trained_model() -> None:
    feature_df = _synthetic_feature_df()
    train_baseline_models(feature_df=feature_df, test_start_date="2022-01-01")
    _clear_preferred_model_artifacts()
    with patch("src.models.predict_match.load_feature_dataset", return_value=feature_df):
        prediction = predict_existing_match_by_id("m1")
    assert prediction["match_id"] == "m1"
    assert prediction["team_a"] == feature_df.iloc[0]["team_a"]
    assert "probabilities" in prediction
