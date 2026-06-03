"""Tests for model-feature selection helpers."""

from __future__ import annotations

import pandas as pd

from src.models.model_features import (
    load_feature_dataset,
    select_model_features,
)


def _feature_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "match_id": ["m1", "m2", "m3"],
            "date": pd.to_datetime(["2021-01-01", "2021-01-02", "2021-01-03"]),
            "year": [2021, 2021, 2021],
            "team_a": ["A", "B", "C"],
            "team_b": ["D", "E", "F"],
            "tournament": ["Friendly", "Friendly", "Friendly"],
            "city": ["x", "y", "z"],
            "country": ["x", "y", "z"],
            "data_source": ["test", "test", "test"],
            "team_a_score": [1, 2, 0],
            "team_b_score": [0, 1, 1],
            "score_difference": [1, 1, -1],
            "total_goals": [1, 3, 1],
            "winner": ["A", "B", "F"],
            "loser": ["D", "E", "C"],
            "is_draw": [0, 0, 0],
            "has_shootout": [0, 0, 0],
            "shootout_winner": [None, None, None],
            "shootout_loser": [None, None, None],
            "progression_winner": ["A", "B", "F"],
            "result": [2, 1, 0],
            "result_label": ["team_a_win", "draw", "team_a_loss"],
            "team_a_last_5_win_rate": [0.5, 0.6, 0.7],
            "team_b_last_5_win_rate": [0.4, 0.5, 0.6],
            "diff_last_5_win_rate": [0.1, 0.1, 0.1],
            "team_a_points_per_match_before": [1.2, 1.3, 1.4],
            "team_b_points_per_match_before": [1.0, 1.1, 1.2],
            "diff_points_per_match_before": [0.2, 0.2, 0.2],
            "team_a_is_host_2026": [0, 0, 0],
            "team_b_is_host_2026": [0, 0, 0],
            "is_world_cup": [0, 0, 0],
            "is_friendly": [1, 1, 1],
        }
    )


def test_load_feature_dataset_returns_dataframe() -> None:
    df = load_feature_dataset()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_select_model_features_excludes_leakage_columns() -> None:
    X, y, feature_columns = select_model_features(_feature_frame())
    assert "team_a_score" not in feature_columns
    assert "result" not in feature_columns
    assert "result_label" not in feature_columns
    assert "team_a" not in feature_columns
    assert "team_b" not in feature_columns
    assert len(feature_columns) > 0


def test_select_model_features_returns_numeric_only() -> None:
    X, y, feature_columns = select_model_features(_feature_frame())
    assert all(
        pd.api.types.is_numeric_dtype(X[column]) or pd.api.types.is_bool_dtype(X[column])
        for column in X.columns
    )


def test_select_model_features_y_contains_valid_classes() -> None:
    X, y, feature_columns = select_model_features(_feature_frame())
    assert set(y.unique()).issubset({0, 1, 2})


def test_select_model_features_feature_columns_not_empty() -> None:
    X, y, feature_columns = select_model_features(_feature_frame())
    assert feature_columns
