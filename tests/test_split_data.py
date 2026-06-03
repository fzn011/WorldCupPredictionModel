"""Tests for chronological train/test splitting."""

from __future__ import annotations

import pandas as pd

from src.models.split_data import chronological_train_test_split, summarize_split


def test_chronological_split_respects_date_boundary() -> None:
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2021-01-01", "2021-12-31", "2022-01-01", "2022-06-01"]),
            "result": [0, 1, 2, 0],
        }
    )
    train_df, test_df = chronological_train_test_split(df, test_start_date="2022-01-01")
    assert train_df["date"].max() < pd.Timestamp("2022-01-01")
    assert test_df["date"].min() >= pd.Timestamp("2022-01-01")


def test_chronological_split_falls_back_when_test_empty() -> None:
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2020-01-01", "2020-02-01", "2020-03-01", "2020-04-01"]),
            "result": [0, 1, 2, 0],
        }
    )
    train_df, test_df = chronological_train_test_split(df, test_start_date="2022-01-01")
    assert len(train_df) > 0
    assert len(test_df) > 0
    assert len(train_df) + len(test_df) == len(df)


def test_summarize_split_returns_expected_keys() -> None:
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2021-01-01", "2021-12-31", "2022-01-01", "2022-06-01"]),
            "result": [0, 1, 2, 0],
        }
    )
    train_df, test_df = chronological_train_test_split(df, test_start_date="2022-01-01")
    summary = summarize_split(train_df, test_df)
    expected = {
        "train_rows",
        "test_rows",
        "train_date_min",
        "train_date_max",
        "test_date_min",
        "test_date_max",
        "train_target_distribution",
        "test_target_distribution",
    }
    assert expected.issubset(summary.keys())
