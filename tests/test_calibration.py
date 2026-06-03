"""Tests for Step 6 calibration helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.models.calibration import (
    create_calibration_report,
    create_probability_quality_report,
    split_train_calibration,
)


def test_split_train_calibration_is_chronological() -> None:
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2021-01-01", "2021-02-01", "2021-03-01", "2021-04-01", "2021-05-01"]
            ),
            "result": [0, 1, 2, 0, 1],
        }
    )
    train_df, calibration_df = split_train_calibration(df, calibration_fraction=0.2)
    assert len(train_df) > 0
    assert len(calibration_df) > 0
    assert train_df["date"].max() <= calibration_df["date"].min()


def test_create_calibration_report_columns() -> None:
    y_true = pd.Series([0, 1, 2, 0])
    y_proba = np.array(
        [
            [0.7, 0.2, 0.1],
            [0.2, 0.6, 0.2],
            [0.1, 0.3, 0.6],
            [0.6, 0.2, 0.2],
        ]
    )
    report = create_calibration_report("demo", y_true, y_proba, [0, 1, 2])
    expected_cols = {
        "model_name",
        "class_label",
        "mean_predicted_probability",
        "observed_frequency",
        "absolute_gap",
    }
    assert expected_cols.issubset(report.columns)
    assert len(report) == 3


def test_probability_quality_report_ranks_models() -> None:
    metrics_df = pd.DataFrame(
        {
            "model_name": ["a", "b", "c"],
            "log_loss": [1.2, 0.9, 1.0],
            "multiclass_brier_score": [0.25, 0.18, 0.2],
        }
    )
    ranking = create_probability_quality_report(metrics_df)
    assert list(ranking["model_name"]) == ["b", "c", "a"]
    assert list(ranking["probability_quality_rank"]) == [1, 2, 3]
