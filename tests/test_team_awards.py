"""Tests for Step 17 team-award utilities."""

from __future__ import annotations

import pandas as pd

from src.awards.team_awards import (
    add_team_stage_to_award_profiles,
    calculate_fair_play_predictions,
    calculate_most_entertaining_team_predictions,
    validate_team_award_profiles,
)


def _team_profiles_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "team": ["France", "England", "Brazil"],
            "attacking_style_score": [8.5, 8.2, 9.0],
            "discipline_score": [7.8, 7.4, 7.2],
            "entertainment_score_prior": [8.4, 8.1, 9.1],
            "fan_popularity_proxy": [8.8, 8.7, 9.2],
        }
    )


def _stage_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "team": ["France", "England", "Brazil"],
            "round_of_32_probability": [1.0, 1.0, 1.0],
            "round_of_16_probability": [0.8, 0.7, 0.75],
            "quarter_final_probability": [0.6, 0.5, 0.55],
            "semi_final_probability": [0.4, 0.3, 0.35],
            "final_probability": [0.25, 0.2, 0.22],
            "champion_probability": [0.2, 0.12, 0.15],
        }
    )


def _players_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "player": ["A", "B", "C"],
            "team": ["France", "England", "Brazil"],
            "star_role_score": [8.5, 7.8, 8.9],
        }
    )


def test_validate_team_award_profiles_passes_valid_data() -> None:
    valid, report = validate_team_award_profiles(_team_profiles_df())
    assert valid is True
    assert not report.empty


def test_calculate_fair_play_predictions_returns_ranked_teams() -> None:
    merged = add_team_stage_to_award_profiles(_team_profiles_df(), _stage_df())
    out = calculate_fair_play_predictions(merged)
    assert "fair_play_rank" in out.columns
    assert out.iloc[0]["fair_play_rank"] == 1


def test_calculate_most_entertaining_team_predictions_returns_ranked_teams() -> None:
    merged = add_team_stage_to_award_profiles(_team_profiles_df(), _stage_df())
    out = calculate_most_entertaining_team_predictions(merged, _players_df())
    assert "most_entertaining_rank" in out.columns
    assert out.iloc[0]["most_entertaining_rank"] == 1
