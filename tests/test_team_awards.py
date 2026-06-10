"""Tests for Step 18 team awards."""

from __future__ import annotations

import pandas as pd

from src.awards.team_awards import (
    calculate_fair_play_predictions,
    calculate_most_entertaining_team_predictions,
    prepare_team_award_data,
)


def test_prepare_team_award_data_merges_profiles_and_probabilities(monkeypatch):
    profiles = pd.DataFrame(
        {
            "team": ["France", "Brazil"],
            "attacking_style_score": [60, 70],
            "discipline_score": [55, 50],
            "entertainment_score_prior": [50, 60],
            "fan_popularity_proxy": [50, 65],
        }
    )
    stages = pd.DataFrame(
        {
            "team": ["France", "Brazil"],
            "round_of_32_probability": [0.9, 0.8],
            "round_of_16_probability": [0.7, 0.6],
            "quarter_final_probability": [0.4, 0.3],
            "semi_final_probability": [0.2, 0.15],
            "final_probability": [0.1, 0.08],
            "champion_probability": [0.05, 0.04],
        }
    )
    monkeypatch.setattr(
        "src.awards.team_awards.load_official_teams_for_awards",
        lambda: pd.DataFrame({"team": ["France", "Brazil"]}),
    )
    merged = prepare_team_award_data(profiles, stages, players_df=None)
    assert "round_of_32_probability" in merged.columns
    assert len(merged) == 2


def test_calculate_fair_play_predictions_returns_official_teams():
    team_df = pd.DataFrame(
        {
            "team": ["France", "Brazil"],
            "discipline_score": [60, 55],
            "round_of_32_probability": [0.9, 0.8],
            "round_of_16_probability": [0.7, 0.6],
            "average_discipline_risk": [0.4, 0.5],
        }
    )
    out = calculate_fair_play_predictions(team_df)
    assert set(out["team"]) == {"France", "Brazil"}


def test_calculate_most_entertaining_team_predictions_returns_ranked_teams():
    team_df = pd.DataFrame(
        {
            "team": ["France", "Brazil"],
            "attacking_style_score": [60, 70],
            "entertainment_score_prior": [50, 60],
            "fan_popularity_proxy": [50, 65],
            "semi_final_probability": [0.2, 0.15],
            "final_probability": [0.1, 0.08],
            "champion_probability": [0.05, 0.04],
        }
    )
    out = calculate_most_entertaining_team_predictions(team_df)
    assert "most_entertaining_rank" in out.columns
