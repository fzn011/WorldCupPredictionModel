"""Tests for the Step 4 feature-building module."""

from __future__ import annotations

import pandas as pd

from src.features.build_features import (
    add_host_flags,
    add_match_context_features,
    build_feature_dataset,
)


def _canonical_matches() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "match_id": "m1",
                "date": pd.Timestamp("1990-01-01"),
                "year": 1990,
                "team_a": "Canada",
                "team_b": "Mexico",
                "team_a_score": 1,
                "team_b_score": 0,
                "score_difference": 1,
                "total_goals": 1,
                "result": 2,
                "result_label": "team_a_win",
                "winner": "Canada",
                "loser": "Mexico",
                "is_draw": 0,
                "tournament": "Friendly",
                "city": "Toronto",
                "country": "Canada",
                "neutral": 0,
                "has_shootout": 0,
                "shootout_winner": pd.NA,
                "shootout_loser": pd.NA,
                "progression_winner": "Canada",
                "data_source": "test",
            },
            {
                "match_id": "m2",
                "date": pd.Timestamp("1990-02-01"),
                "year": 1990,
                "team_a": "United States",
                "team_b": "Argentina",
                "team_a_score": 0,
                "team_b_score": 2,
                "score_difference": -2,
                "total_goals": 2,
                "result": 0,
                "result_label": "team_a_loss",
                "winner": "Argentina",
                "loser": "United States",
                "is_draw": 0,
                "tournament": "FIFA World Cup",
                "city": "New York",
                "country": "United States",
                "neutral": 1,
                "has_shootout": 0,
                "shootout_winner": pd.NA,
                "shootout_loser": pd.NA,
                "progression_winner": "Argentina",
                "data_source": "test",
            },
            {
                "match_id": "m3",
                "date": pd.Timestamp("1990-03-01"),
                "year": 1990,
                "team_a": "France",
                "team_b": "Brazil",
                "team_a_score": 1,
                "team_b_score": 1,
                "score_difference": 0,
                "total_goals": 2,
                "result": 1,
                "result_label": "draw",
                "winner": pd.NA,
                "loser": pd.NA,
                "is_draw": 1,
                "tournament": "World Cup qualification",
                "city": "Paris",
                "country": "France",
                "neutral": 1,
                "has_shootout": 0,
                "shootout_winner": pd.NA,
                "shootout_loser": pd.NA,
                "progression_winner": pd.NA,
                "data_source": "test",
            },
            {
                "match_id": "m4",
                "date": pd.Timestamp("1990-04-01"),
                "year": 1990,
                "team_a": "Germany",
                "team_b": "England",
                "team_a_score": 0,
                "team_b_score": 1,
                "score_difference": -1,
                "total_goals": 1,
                "result": 0,
                "result_label": "team_a_loss",
                "winner": "England",
                "loser": "Germany",
                "is_draw": 0,
                "tournament": "Copa América",
                "city": "Berlin",
                "country": "Germany",
                "neutral": 0,
                "has_shootout": 0,
                "shootout_winner": pd.NA,
                "shootout_loser": pd.NA,
                "progression_winner": "England",
                "data_source": "test",
            },
        ]
    )


def test_add_match_context_features_creates_expected_columns() -> None:
    df = add_match_context_features(_canonical_matches())
    expected = {
        "is_neutral",
        "is_world_cup",
        "is_world_cup_qualifier",
        "is_friendly",
        "is_continental_tournament",
        "is_major_tournament",
        "is_knockout_like_match",
    }
    assert expected.issubset(df.columns)
    assert df.loc[df["match_id"] == "m1", "is_friendly"].iloc[0] == 1
    assert df.loc[df["match_id"] == "m2", "is_world_cup"].iloc[0] == 1
    assert df.loc[df["match_id"] == "m3", "is_world_cup_qualifier"].iloc[0] == 1


def test_add_host_flags_correctly_flags_hosts() -> None:
    df = add_host_flags(_canonical_matches())
    assert df.loc[df["team_a"] == "Canada", "team_a_is_host_2026"].iloc[0] == 1
    assert df.loc[df["team_b"] == "Mexico", "team_b_is_host_2026"].iloc[0] == 1
    assert df.loc[df["team_a"] == "United States", "team_a_is_host_2026"].iloc[0] == 1


def test_build_feature_dataset_returns_dataframe() -> None:
    feature_df = build_feature_dataset(_canonical_matches(), min_year=1990)
    assert isinstance(feature_df, pd.DataFrame)
    assert len(feature_df) > 0


def test_build_feature_dataset_contains_recent_form_features() -> None:
    feature_df = build_feature_dataset(_canonical_matches(), min_year=1990)
    assert "team_a_last_5_win_rate" in feature_df.columns
    assert "team_b_last_10_points_per_match" in feature_df.columns
    assert "diff_last_5_goal_diff_avg" in feature_df.columns


def test_build_feature_dataset_keeps_targets() -> None:
    feature_df = build_feature_dataset(_canonical_matches(), min_year=1990)
    assert "result" in feature_df.columns
    assert "result_label" in feature_df.columns
