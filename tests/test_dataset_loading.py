"""Tests for dataset loaders (with sample fallback)."""

from __future__ import annotations

import pandas as pd

from src.data.load_data import (
    load_elo_ratings,
    load_fifa_rankings,
    load_historical_results,
    load_wc2026_groups,
    load_wc2026_schedule,
    load_wc2026_teams,
)


def test_load_historical_results_returns_dataframe() -> None:
    df = load_historical_results()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_load_fifa_rankings_returns_dataframe() -> None:
    df = load_fifa_rankings()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_load_elo_ratings_returns_dataframe() -> None:
    df = load_elo_ratings()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_load_wc2026_teams_returns_dataframe() -> None:
    df = load_wc2026_teams()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_load_wc2026_groups_returns_dataframe() -> None:
    df = load_wc2026_groups()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_load_wc2026_schedule_returns_dataframe() -> None:
    df = load_wc2026_schedule()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
