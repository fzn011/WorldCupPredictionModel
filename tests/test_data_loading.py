"""Tests for sample-data loading."""

from __future__ import annotations

import pandas as pd

from src.data.load_data import load_sample_matches


def test_load_sample_matches_returns_dataframe() -> None:
    df = load_sample_matches()
    assert isinstance(df, pd.DataFrame)


def test_load_sample_matches_has_rows() -> None:
    df = load_sample_matches()
    assert len(df) > 0
