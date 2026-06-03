"""Chronological train/test splitting helpers for sports forecasting."""

from __future__ import annotations

import pandas as pd

from src.utils.constants import DEFAULT_TEST_START_DATE, TARGET_COLUMN, TARGET_CLASS_ORDER


def chronological_train_test_split(
    df: pd.DataFrame,
    test_start_date: str = DEFAULT_TEST_START_DATE,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split rows chronologically without shuffling.

    Primary split: train rows strictly before ``test_start_date`` and test rows
    on/after it. If either split is empty, fall back to an 80/20 chronological
    split by date.
    """
    if df is None or df.empty:
        return pd.DataFrame(), pd.DataFrame()
    if "date" not in df.columns:
        raise ValueError("chronological_train_test_split requires a 'date' column.")

    working = df.copy()
    working["date"] = pd.to_datetime(working["date"], errors="coerce")
    working = working.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    if working.empty:
        return pd.DataFrame(), pd.DataFrame()

    boundary = pd.Timestamp(test_start_date)
    train_df = working.loc[working["date"] < boundary].copy()
    test_df = working.loc[working["date"] >= boundary].copy()

    if train_df.empty or test_df.empty:
        split_idx = max(1, int(len(working) * 0.8))
        split_idx = min(split_idx, len(working) - 1)
        train_df = working.iloc[:split_idx].copy()
        test_df = working.iloc[split_idx:].copy()

    return train_df.reset_index(drop=True), test_df.reset_index(drop=True)


def summarize_split(train_df: pd.DataFrame, test_df: pd.DataFrame) -> dict:
    """Summarize a chronological split for reporting."""
    def _target_distribution(frame: pd.DataFrame) -> dict:
        if TARGET_COLUMN not in frame.columns:
            return {}
        values = pd.to_numeric(frame[TARGET_COLUMN], errors="coerce")
        values = values[values.isin(TARGET_CLASS_ORDER)]
        return values.astype(int).value_counts().sort_index().to_dict()

    def _date_value(frame: pd.DataFrame, which: str) -> str | None:
        if frame.empty or "date" not in frame.columns:
            return None
        date_series = pd.to_datetime(frame["date"], errors="coerce")
        date_value = getattr(date_series, which)()
        return str(date_value) if pd.notna(date_value) else None

    return {
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "train_date_min": _date_value(train_df, "min"),
        "train_date_max": _date_value(train_df, "max"),
        "test_date_min": _date_value(test_df, "min"),
        "test_date_max": _date_value(test_df, "max"),
        "train_target_distribution": _target_distribution(train_df),
        "test_target_distribution": _target_distribution(test_df),
    }
