"""Smoke tests for predictor UI helper utilities."""

from __future__ import annotations

import pandas as pd

from src.models.prediction_utils import (
    extract_prediction_explanation_features,
    get_prediction_confidence,
)



def test_prediction_ui_helper_smoke() -> None:
    conf = get_prediction_confidence({"team_a_loss": 0.4, "draw": 0.3, "team_a_win": 0.3})
    assert conf["confidence_label"] == "Low"

    features = extract_prediction_explanation_features(
        pd.Series({"team_a_last_5_win_rate": 0.7, "team_b_last_5_win_rate": 0.6})
    )
    assert {"feature", "value"}.issubset(features.columns)
