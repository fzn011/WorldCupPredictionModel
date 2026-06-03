"""Temporal backtesting utilities for Step 6."""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from src.models.evaluate_model import evaluate_classifier
from src.models.model_features import select_model_features
from src.models.split_data import chronological_train_test_split
import src.utils.constants as C

BACKTEST_WINDOWS = getattr(C, "BACKTEST_WINDOWS", [{"name": "test_2022_onward", "test_start_date": "2022-01-01"}])
TARGET_CLASS_ORDER = getattr(C, "TARGET_CLASS_ORDER", [0, 1, 2])


def _align_features(df: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    return df.reindex(columns=feature_columns)


def run_single_backtest(
    feature_df: pd.DataFrame,
    model_builder: Callable[[], object],
    model_name: str,
    test_start_date: str,
) -> dict:
    """Run one temporal backtest for one model and one date window."""
    train_df, test_df = chronological_train_test_split(feature_df, test_start_date=test_start_date)
    X_train, y_train, feature_columns = select_model_features(train_df)
    X_test_base, y_test, _ = select_model_features(test_df)
    X_test = _align_features(X_test_base, feature_columns)

    model = model_builder()
    model.fit(X_train, y_train)
    metrics = evaluate_classifier(
        model,
        X_test,
        y_test,
        model_name=model_name,
        class_order=TARGET_CLASS_ORDER,
    )

    metrics.update(
        {
            "status": "ok",
            "backtest_window": f"test_{test_start_date}_onward",
            "test_start_date": test_start_date,
            "train_rows": int(len(train_df)),
            "test_rows": int(len(test_df)),
            "feature_count": int(len(feature_columns)),
            "train_date_min": str(pd.to_datetime(train_df["date"], errors="coerce").min()) if not train_df.empty else None,
            "train_date_max": str(pd.to_datetime(train_df["date"], errors="coerce").max()) if not train_df.empty else None,
            "test_date_min": str(pd.to_datetime(test_df["date"], errors="coerce").min()) if not test_df.empty else None,
            "test_date_max": str(pd.to_datetime(test_df["date"], errors="coerce").max()) if not test_df.empty else None,
        }
    )
    return metrics


def run_temporal_backtests(
    feature_df: pd.DataFrame,
    model_builders: dict[str, Callable[[], object]],
    backtest_windows: list[dict] | None = None,
) -> pd.DataFrame:
    """Run multiple temporal backtests and return a results DataFrame."""
    windows = backtest_windows or list(BACKTEST_WINDOWS)
    rows: list[dict] = []

    for window in windows:
        window_name = str(window.get("name"))
        test_start_date = str(window.get("test_start_date"))

        for model_name, builder in model_builders.items():
            if builder is None:
                rows.append(
                    {
                        "model_name": model_name,
                        "backtest_window": window_name,
                        "test_start_date": test_start_date,
                        "status": "skipped",
                        "error": "model builder unavailable",
                    }
                )
                continue

            try:
                metrics = run_single_backtest(
                    feature_df=feature_df,
                    model_builder=builder,
                    model_name=model_name,
                    test_start_date=test_start_date,
                )
                metrics["backtest_window"] = window_name
                rows.append(metrics)
            except Exception as exc:
                rows.append(
                    {
                        "model_name": model_name,
                        "backtest_window": window_name,
                        "test_start_date": test_start_date,
                        "status": "failed",
                        "error": str(exc),
                    }
                )

    return pd.DataFrame(rows)
