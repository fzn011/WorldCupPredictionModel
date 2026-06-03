"""Tests for Step 6 temporal backtesting."""

from __future__ import annotations

import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from src.models.backtesting import run_single_backtest, run_temporal_backtests
from tests.test_train_baseline_models import _synthetic_feature_df


def _simple_model_builder():
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("classifier", DecisionTreeClassifier(random_state=42)),
        ]
    )


def test_run_single_backtest_returns_metrics() -> None:
    df = _synthetic_feature_df()
    result = run_single_backtest(
        feature_df=df,
        model_builder=_simple_model_builder,
        model_name="simple_tree",
        test_start_date="2022-01-01",
    )
    assert result["model_name"] == "simple_tree"
    assert result["status"] == "ok"
    assert "accuracy" in result


def test_run_temporal_backtests_returns_dataframe() -> None:
    df = _synthetic_feature_df()
    out = run_temporal_backtests(
        feature_df=df,
        model_builders={"simple_tree": _simple_model_builder},
        backtest_windows=[{"name": "test_small", "test_start_date": "2022-01-01"}],
    )
    assert isinstance(out, pd.DataFrame)
    assert len(out) == 1


def test_run_temporal_backtests_handles_failed_builder() -> None:
    df = _synthetic_feature_df()

    def _bad_builder():
        raise RuntimeError("boom")

    out = run_temporal_backtests(
        feature_df=df,
        model_builders={"bad_model": _bad_builder},
        backtest_windows=[{"name": "test_small", "test_start_date": "2022-01-01"}],
    )
    assert out.iloc[0]["status"] == "failed"
    assert "boom" in str(out.iloc[0]["error"])
