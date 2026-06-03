"""Tests for leakage-safe historical feature helpers."""

from __future__ import annotations

import pandas as pd

from src.features.historical_features import (
    build_historical_features_for_match,
    get_team_match_history,
    get_team_perspective_history,
    summarize_recent_form,
    summarize_team_history,
)


def _canonical_matches() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "match_id": "m1",
                "date": pd.Timestamp("1990-01-01"),
                "year": 1990,
                "team_a": "Argentina",
                "team_b": "Brazil",
                "team_a_score": 2,
                "team_b_score": 0,
                "score_difference": 2,
                "total_goals": 2,
                "result": 2,
                "result_label": "team_a_win",
                "winner": "Argentina",
                "loser": "Brazil",
                "is_draw": 0,
                "tournament": "Friendly",
                "city": "Buenos Aires",
                "country": "Argentina",
                "neutral": 0,
                "has_shootout": 0,
                "shootout_winner": pd.NA,
                "shootout_loser": pd.NA,
                "progression_winner": "Argentina",
                "data_source": "test",
            },
            {
                "match_id": "m2",
                "date": pd.Timestamp("1990-02-01"),
                "year": 1990,
                "team_a": "Chile",
                "team_b": "Argentina",
                "team_a_score": 1,
                "team_b_score": 1,
                "score_difference": 0,
                "total_goals": 2,
                "result": 1,
                "result_label": "draw",
                "winner": pd.NA,
                "loser": pd.NA,
                "is_draw": 1,
                "tournament": "Friendly",
                "city": "Santiago",
                "country": "Chile",
                "neutral": 1,
                "has_shootout": 0,
                "shootout_winner": pd.NA,
                "shootout_loser": pd.NA,
                "progression_winner": pd.NA,
                "data_source": "test",
            },
            {
                "match_id": "m3",
                "date": pd.Timestamp("1990-03-01"),
                "year": 1990,
                "team_a": "Argentina",
                "team_b": "Uruguay",
                "team_a_score": 0,
                "team_b_score": 1,
                "score_difference": -1,
                "total_goals": 1,
                "result": 0,
                "result_label": "team_a_loss",
                "winner": "Uruguay",
                "loser": "Argentina",
                "is_draw": 0,
                "tournament": "Friendly",
                "city": "Montevideo",
                "country": "Uruguay",
                "neutral": 1,
                "has_shootout": 0,
                "shootout_winner": pd.NA,
                "shootout_loser": pd.NA,
                "progression_winner": "Uruguay",
                "data_source": "test",
            },
            {
                "match_id": "m4",
                "date": pd.Timestamp("1990-04-01"),
                "year": 1990,
                "team_a": "Argentina",
                "team_b": "Paraguay",
                "team_a_score": 3,
                "team_b_score": 3,
                "score_difference": 0,
                "total_goals": 6,
                "result": 1,
                "result_label": "draw",
                "winner": pd.NA,
                "loser": pd.NA,
                "is_draw": 1,
                "tournament": "Friendly",
                "city": "Cordoba",
                "country": "Argentina",
                "neutral": 0,
                "has_shootout": 0,
                "shootout_winner": pd.NA,
                "shootout_loser": pd.NA,
                "progression_winner": pd.NA,
                "data_source": "test",
            },
        ]
    )


def test_get_team_match_history_excludes_current_and_future_matches() -> None:
    df = _canonical_matches()
    history = get_team_match_history(df, "Argentina", pd.Timestamp("1990-03-01"))
    assert list(history["match_id"]) == ["m1", "m2"]


def test_get_team_perspective_history_returns_correct_goals() -> None:
    df = _canonical_matches()
    history = get_team_match_history(df, "Argentina", pd.Timestamp("1990-03-01"))
    perspective = get_team_perspective_history(history, "Argentina")
    assert list(perspective["goals_for"]) == [2, 1]
    assert list(perspective["goals_against"]) == [0, 1]


def test_summarize_team_history_counts() -> None:
    df = _canonical_matches()
    history = get_team_match_history(df, "Argentina", pd.Timestamp("1990-03-01"))
    perspective = get_team_perspective_history(history, "Argentina")
    summary = summarize_team_history(perspective)
    assert summary["matches_played"] == 2
    assert summary["wins"] == 1
    assert summary["draws"] == 1
    assert summary["losses"] == 0
    assert summary["points_per_match"] == 2.0


def test_summarize_recent_form_respects_window_size() -> None:
    history = pd.DataFrame(
        {
            "date": pd.to_datetime(["1990-01-01", "1990-02-01", "1990-03-01"]),
            "goals_for": [1, 0, 2],
            "goals_against": [0, 0, 2],
            "points": [3, 3, 1],
            "win": [1, 1, 0],
            "draw": [0, 0, 1],
            "loss": [0, 0, 0],
            "clean_sheet": [1, 1, 0],
            "failed_to_score": [0, 0, 0],
            "goal_diff": [1, 0, 0],
        }
    )
    summary = summarize_recent_form(history, 2)
    assert summary["matches_played"] == 2
    assert summary["wins"] == 1
    assert summary["draws"] == 1
    assert summary["losses"] == 0


def test_build_historical_features_for_match_creates_diff_features() -> None:
    df = _canonical_matches()
    features = build_historical_features_for_match(df.iloc[2], df, windows=[5])
    assert features["diff_matches_played_before"] == 2
    assert features["team_a_matches_played_before"] == 2
    assert features["team_b_matches_played_before"] == 0
    assert features["diff_last_5_win_rate"] == 0.5
