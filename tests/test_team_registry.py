"""Tests for the Step 3 team registry."""

from __future__ import annotations

import pandas as pd

from src.data.clean_data import (
    build_team_registry,
    convert_historical_results_to_canonical,
)
from src.utils.constants import TEAM_REGISTRY_COLUMNS


def _canonical() -> pd.DataFrame:
    results = pd.DataFrame(
        {
            "date": ["2022-12-18", "2018-07-15", "2014-07-13"],
            "home_team": ["Argentina", "France", "Germany"],
            "away_team": ["France", "Croatia", "Argentina"],
            "home_score": [3, 4, 1],
            "away_score": [3, 2, 0],
            "tournament": ["FIFA World Cup"] * 3,
            "city": ["Lusail", "Moscow", "Rio"],
            "country": ["Qatar", "Russia", "Brazil"],
            "neutral": [True, True, True],
        }
    )
    return convert_historical_results_to_canonical(results)


def test_team_registry_columns() -> None:
    registry = build_team_registry(_canonical())
    assert list(registry.columns) == TEAM_REGISTRY_COLUMNS


def test_team_registry_unique_names_and_slugs() -> None:
    registry = build_team_registry(_canonical())
    assert not registry["team"].duplicated().any()
    assert not registry["team_slug"].duplicated().any()


def test_team_registry_matches_played() -> None:
    registry = build_team_registry(_canonical())
    assert (registry["matches_played"] >= 1).all()
    argentina = registry[registry["team"] == "Argentina"].iloc[0]
    assert argentina["matches_played"] == 2
