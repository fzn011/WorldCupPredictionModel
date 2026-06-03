"""Tests for penalty-shootout handling in the canonical pipeline."""

from __future__ import annotations

import pandas as pd

from src.data.clean_data import convert_historical_results_to_canonical


def test_drawn_match_with_shootout_winner() -> None:
    results = pd.DataFrame(
        {
            "date": ["2022-12-18"],
            "home_team": ["Argentina"],
            "away_team": ["France"],
            "home_score": [3],
            "away_score": [3],
            "tournament": ["FIFA World Cup"],
            "city": ["Lusail"],
            "country": ["Qatar"],
            "neutral": [True],
        }
    )
    shootouts = pd.DataFrame(
        {
            "date": ["2022-12-18"],
            "home_team": ["Argentina"],
            "away_team": ["France"],
            "winner": ["Argentina"],
        }
    )

    canonical = convert_historical_results_to_canonical(
        results, shootouts_df=shootouts, data_source="test"
    )
    row = canonical.iloc[0]

    assert row["result_label"] == "draw"
    assert row["is_draw"] == 1
    assert row["has_shootout"] == 1
    assert row["shootout_winner"] == "Argentina"
    assert row["shootout_loser"] == "France"
    assert row["progression_winner"] == "Argentina"


def test_match_without_shootout_has_no_shootout_flag() -> None:
    results = pd.DataFrame(
        {
            "date": ["2018-07-15"],
            "home_team": ["France"],
            "away_team": ["Croatia"],
            "home_score": [4],
            "away_score": [2],
            "tournament": ["FIFA World Cup"],
            "city": ["Moscow"],
            "country": ["Russia"],
            "neutral": [True],
        }
    )
    canonical = convert_historical_results_to_canonical(results)
    row = canonical.iloc[0]
    assert row["has_shootout"] == 0
    assert row["progression_winner"] == "France"
