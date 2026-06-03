"""Tests for the Step 3 cleaning and canonical-conversion pipeline."""

from __future__ import annotations

import pandas as pd

from src.data.clean_data import (
    clean_historical_results,
    convert_historical_results_to_canonical,
)
from src.utils.constants import CANONICAL_MATCH_COLUMNS, RESULT_LABELS


def _raw_results() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": ["2022-12-18", "2018-07-15", "bad-date"],
            "home_team": ["Argentina", "France", "Brazil"],
            "away_team": ["France", "Croatia", "Brazil"],
            "home_score": [3, 4, 1],
            "away_score": [3, 2, 0],
            "tournament": ["FIFA World Cup", "FIFA World Cup", "Friendly"],
            "city": ["Lusail", "Moscow", "Rio"],
            "country": ["Qatar", "Russia", "Brazil"],
            "neutral": [True, True, False],
        }
    )


def test_clean_historical_results() -> None:
    cleaned = clean_historical_results(_raw_results())
    # The bad-date row and the team_a==team_b row are removed.
    assert len(cleaned) == 2
    assert (cleaned["home_score"] >= 0).all()
    assert cleaned["date"].notna().all()


def test_convert_historical_results_to_canonical() -> None:
    canonical = convert_historical_results_to_canonical(
        _raw_results(), data_source="test"
    )
    assert len(canonical) == 2
    assert (canonical["data_source"] == "test").all()


def test_canonical_contains_expected_columns() -> None:
    canonical = convert_historical_results_to_canonical(_raw_results())
    assert list(canonical.columns) == CANONICAL_MATCH_COLUMNS


def test_result_labels_are_valid() -> None:
    canonical = convert_historical_results_to_canonical(_raw_results())
    valid = set(RESULT_LABELS.values())
    assert set(canonical["result_label"].unique()).issubset(valid)


def test_team_a_not_equal_team_b() -> None:
    canonical = convert_historical_results_to_canonical(_raw_results())
    assert (canonical["team_a"] != canonical["team_b"]).all()
