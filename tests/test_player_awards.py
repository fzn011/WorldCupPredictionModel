"""Tests for Step 18 player awards."""

from __future__ import annotations

import pandas as pd

from src.awards.player_awards import (
    calculate_expected_matches,
    calculate_golden_ball_predictions,
    calculate_golden_boot_predictions,
    calculate_golden_glove_predictions,
    calculate_goal_of_tournament_proxy,
    calculate_player_of_match_proxy,
    calculate_young_player_predictions,
    is_young_player_eligible,
)


def _sample_players(n: int = 4) -> pd.DataFrame:
    rows = []
    specs = [
        ("FW", "forward", 70, 3, 1),
        ("MF", "midfielder", 65, 1, 2),
        ("DF", "defender", 60, 0, 0),
        ("GK", "goalkeeper", 62, 0, 0),
    ]
    for i, (code, group, rating, goals, gk_actions) in enumerate(specs[:n]):
        rows.append(
            {
                "player_id": f"p{i}",
                "player_name": f"Player {i}",
                "team": "France",
                "position_code": code,
                "position": code,
                "position_group": group,
                "base_player_rating": rating,
                "expected_minutes_share": 0.8,
                "goals_prior": goals,
                "assists_prior": 1,
                "chance_creation_prior": 1,
                "defensive_actions_prior": 1,
                "goalkeeper_actions_prior": gk_actions,
                "discipline_risk": 0.5,
                "star_role_score": 1,
                "flair_score": 1,
                "round_of_32_probability": 0.9,
                "round_of_16_probability": 0.7,
                "quarter_final_probability": 0.4,
                "semi_final_probability": 0.2,
                "final_probability": 0.1,
                "champion_probability": 0.05,
                "team_progression_score": 2.0,
            }
        )
    return pd.DataFrame(rows)


def test_calculate_expected_matches_works():
    row = _sample_players(1).iloc[0]
    assert calculate_expected_matches(row) > 3.0


def test_calculate_golden_ball_predictions_probability_sum():
    df = calculate_golden_ball_predictions(_sample_players())
    assert abs(df["golden_ball_probability"].sum() - 1.0) < 1e-6


def test_calculate_golden_boot_predictions_probability_sum():
    df = calculate_golden_boot_predictions(_sample_players())
    assert abs(df["golden_boot_probability"].sum() - 1.0) < 1e-6


def test_calculate_golden_glove_predictions_goalkeepers_only():
    df = calculate_golden_glove_predictions(_sample_players())
    assert (df["position_code"] == "GK").all()


def test_is_young_player_eligible_from_age():
    row = pd.Series({"date_of_birth": "", "age_at_tournament_start": 20})
    assert is_young_player_eligible(row) is True


def test_calculate_young_player_predictions_eligible_only():
    players = _sample_players()
    players.loc[0, "age_at_tournament_start"] = 19
    players.loc[1, "age_at_tournament_start"] = 30
    df = calculate_young_player_predictions(players)
    assert len(df) == 1


def test_calculate_player_of_match_proxy_returns_ranks():
    df = calculate_player_of_match_proxy(_sample_players())
    assert "player_of_match_proxy_rank" in df.columns


def test_calculate_goal_of_tournament_proxy_returns_ranks():
    df = calculate_goal_of_tournament_proxy(_sample_players())
    assert "goal_of_tournament_proxy_rank" in df.columns
