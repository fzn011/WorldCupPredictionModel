"""Tests for model evaluation utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier

from src.models.evaluate_model import (
    classification_report_to_dataframe,
    choose_best_model,
    confusion_matrix_to_dataframe,
    evaluate_classifier,
    multiclass_brier_score,
)


def test_multiclass_brier_score_returns_float() -> None:
    y_true = np.array([0, 1, 2])
    y_proba = np.array(
        [
            [0.8, 0.1, 0.1],
            [0.2, 0.6, 0.2],
            [0.1, 0.2, 0.7],
        ]
    )
    score = multiclass_brier_score(y_true, y_proba, [0, 1, 2])
    assert isinstance(score, float)
    assert score >= 0


def test_evaluate_classifier_works_on_tiny_classifier() -> None:
    X = pd.DataFrame({"feature": [1, 2, 3, 4, 5, 6]})
    y = pd.Series([0, 1, 2, 0, 1, 2])
    model = DummyClassifier(strategy="most_frequent")
    model.fit(X, y)
    metrics = evaluate_classifier(model, X, y, model_name="dummy")
    assert metrics["model_name"] == "dummy"
    assert "accuracy" in metrics
    assert "macro_f1" in metrics
    assert "log_loss" in metrics
    assert "multiclass_brier_score" in metrics


def test_classification_report_to_dataframe_returns_dataframe() -> None:
    df = classification_report_to_dataframe([0, 1, 2], [0, 1, 1])
    assert isinstance(df, pd.DataFrame)
    assert "precision" in df.columns


def test_confusion_matrix_to_dataframe_returns_dataframe() -> None:
    df = confusion_matrix_to_dataframe([0, 1, 2], [0, 1, 1], labels=[0, 1, 2])
    assert isinstance(df, pd.DataFrame)
    assert list(df.index) == ["team_a_loss", "draw", "team_a_win"]
    assert list(df.columns) == ["team_a_loss", "draw", "team_a_win"]


def test_choose_best_model_prefers_lowest_log_loss() -> None:
    metrics_df = pd.DataFrame(
        {
            "model_name": ["dummy", "logistic", "rf"],
            "log_loss": [1.5, 0.8, 0.9],
            "macro_f1": [0.3, 0.5, 0.4],
        }
    )
    assert choose_best_model(metrics_df) == "logistic"
