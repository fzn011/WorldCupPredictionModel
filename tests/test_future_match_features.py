"""Tests for Step 8 future match feature generation."""

from __future__ import annotations

import pandas as pd
import pytest

from src.features.future_match_features import (
    create_future_canonical_match_row,
    generate_future_match_feature_row,
    get_available_teams,
)



def _canonical_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "match_id": ["m_before", "m_after"],
            "date": pd.to_datetime(["2026-06-01", "2026-06-20"]),
            "year": [2026, 2026],
            "team_a": ["Argentina", "Argentina"],
            "team_b": ["France", "Brazil"],
            "team_a_score": [1, 2],
            "team_b_score": [0, 2],
            "score_difference": [1, 0],
            "total_goals": [1, 4],
            "result": [2, 1],
            "result_label": ["team_a_win", "draw"],
            "winner": ["Argentina", None],
            "loser": ["France", None],
            "is_draw": [0, 1],
            "tournament": ["Friendly", "Friendly"],
            "city": ["A", "B"],
            "country": ["C", "D"],
            "neutral": [1, 1],
            "has_shootout": [0, 0],
            "shootout_winner": [None, None],
            "shootout_loser": [None, None],
            "progression_winner": [None, None],
            "data_source": ["sample_fallback", "sample_fallback"],
        }
    )



def _team_strength_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "team": ["Argentina", "France"],
            "fifa_rank": [3, 1],
            "fifa_points": [1874.8, 1877.3],
            "fifa_ranking_date": ["2026-04-01", "2026-04-01"],
            "elo_rank": [2, 3],
            "elo": [2113, 2081],
            "elo_rating_date": ["2026-05-23", "2026-05-23"],
            "has_fifa_ranking": [1, 1],
            "has_elo": [1, 1],
            "fifa_points_norm": [0.9, 1.0],
            "elo_norm": [1.0, 0.8],
            "team_strength_score": [0.95, 0.9],
        }
    )



def test_create_future_canonical_match_row_validates_and_builds() -> None:
    row = create_future_canonical_match_row(
        team_a="Argentina",
        team_b="France",
        match_date="2026-06-11",
    )
    assert len(row) == 1
    assert row.iloc[0]["team_a"] == "Argentina"
    assert row.iloc[0]["team_b"] == "France"
    assert str(row.iloc[0]["match_id"]).startswith("future_20260611_")



def test_create_future_canonical_match_row_rejects_same_team() -> None:
    with pytest.raises(ValueError):
        create_future_canonical_match_row("Argentina", "Argentina", "2026-06-11")



def test_generate_future_match_feature_row_returns_one_row(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "src.features.future_match_features.load_best_available_processed_data",
        lambda: {
            "canonical_matches": _canonical_df(),
            "ranking_feature_dataset": pd.DataFrame(),
            "team_strength_snapshot": pd.DataFrame(),
            "team_registry": pd.DataFrame(),
        },
    )
    out = generate_future_match_feature_row("Argentina", "France", "2026-06-11")
    assert len(out) == 1
    assert out.iloc[0]["team_a"] == "Argentina"



def test_future_features_use_only_matches_before_date(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "src.features.future_match_features.load_best_available_processed_data",
        lambda: {
            "canonical_matches": _canonical_df(),
            "ranking_feature_dataset": pd.DataFrame(),
            "team_strength_snapshot": pd.DataFrame(),
            "team_registry": pd.DataFrame(),
        },
    )

    out = generate_future_match_feature_row("Argentina", "France", "2026-06-11")

    # Argentina has one match before 2026-06-11 and one after; only the first should count.
    assert int(out.iloc[0]["team_a_matches_played_before"]) == 1



def test_ranking_features_are_added_when_team_strength_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "src.features.future_match_features.load_best_available_processed_data",
        lambda: {
            "canonical_matches": _canonical_df(),
            "ranking_feature_dataset": pd.DataFrame(),
            "team_strength_snapshot": _team_strength_df(),
            "team_registry": pd.DataFrame(),
        },
    )

    out = generate_future_match_feature_row("Argentina", "France", "2026-06-11")
    assert "team_a_fifa_rank" in out.columns
    assert "team_b_elo" in out.columns
    assert "diff_strength_score" in out.columns



def test_get_available_teams_returns_sorted_non_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = pd.DataFrame({"team": ["France", "Argentina", "Brazil"]})
    monkeypatch.setattr(
        "src.features.future_match_features.load_best_available_processed_data",
        lambda: {
            "canonical_matches": pd.DataFrame(),
            "ranking_feature_dataset": pd.DataFrame(),
            "team_strength_snapshot": pd.DataFrame(),
            "team_registry": registry,
        },
    )

    teams = get_available_teams(official_only=False)
    assert teams == ["Argentina", "Brazil", "France"]
