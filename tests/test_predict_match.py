"""Tests for the baseline prediction helpers."""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd
import pytest

from src.models.predict_match import (
    load_baseline_model,
    predict_existing_match_by_id,
    predict_from_feature_row,
)
from src.models.train_match_model import train_baseline_models
from tests.test_train_baseline_models import _synthetic_feature_df


def test_load_baseline_model_raises_clear_error_for_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        load_baseline_model(model_path="models/baseline/does_not_exist.joblib")


def test_predict_from_feature_row_returns_probability_keys() -> None:
    train_baseline_models(feature_df=_synthetic_feature_df(), test_start_date="2022-01-01")
    row = _synthetic_feature_df().iloc[0]
    prediction = predict_from_feature_row(row)
    assert "predicted_class" in prediction
    assert "predicted_label" in prediction
    assert set(prediction["probabilities"].keys()) == {"team_a_loss", "draw", "team_a_win"}


def test_predict_existing_match_by_id_works_with_trained_model() -> None:
    feature_df = _synthetic_feature_df()
    train_baseline_models(feature_df=feature_df, test_start_date="2022-01-01")
    with patch("src.models.predict_match.load_feature_dataset", return_value=feature_df):
        prediction = predict_existing_match_by_id("m1")
    assert prediction["match_id"] == "m1"
    assert prediction["team_a"] == feature_df.iloc[0]["team_a"]
    assert "probabilities" in prediction
