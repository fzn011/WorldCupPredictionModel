"""Tests for Step 17 player-award utilities."""

from __future__ import annotations

import pandas as pd

from src.awards.player_awards import (
    add_team_progression_to_players,
    calculate_golden_ball_predictions,
    calculate_golden_boot_predictions,
    calculate_golden_glove_predictions,
    calculate_goal_of_tournament_proxy,
    calculate_player_of_match_proxy,
    calculate_position_impact_score,
    calculate_team_progression_score,
    calculate_young_player_predictions,
    filter_young_player_candidates,
    validate_player_candidates,
)


def _players_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "player": ["A", "B", "C", "D"],
            "team": ["France", "England", "Brazil", "Argentina"],
            "position": ["forward", "midfielder", "defender", "goalkeeper"],
            "age": [21, 24, 28, 30],
            "date_of_birth": ["2005-01-02", "2002-02-02", "1998-03-03", "1996-04-04"],
            "base_player_rating": [90, 86, 84, 85],
            "expected_minutes_share": [0.9, 0.85, 0.8, 0.92],
            "goals_prior": [15, 8, 2, 0],
            "assists_prior": [6, 10, 1, 0],
            "chance_creation_prior": [12, 16, 3, 1],
            "defensive_actions_prior": [3, 12, 18, 4],
            "goalkeeper_actions_prior": [0, 0, 0, 25],
            "discipline_risk": [0.12, 0.15, 0.18, 0.08],
            "star_role_score": [8.5, 7.8, 6.6, 7.1],
            "flair_score": [8.0, 7.2, 4.5, 3.0],
        }
    )


def _stage_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "team": ["France", "England", "Brazil", "Argentina"],
            "round_of_32_probability": [1.0, 1.0, 1.0, 1.0],
            "round_of_16_probability": [0.8, 0.7, 0.75, 0.85],
            "quarter_final_probability": [0.6, 0.5, 0.55, 0.65],
            "semi_final_probability": [0.4, 0.3, 0.35, 0.5],
            "final_probability": [0.25, 0.2, 0.22, 0.35],
            "champion_probability": [0.2, 0.12, 0.15, 0.25],
        }
    )


def test_validate_player_candidates_passes_valid_data() -> None:
    valid, report = validate_player_candidates(_players_df())
    assert valid is True
    assert not report.empty


def test_validate_player_candidates_fails_invalid_position() -> None:
    df = _players_df().copy()
    df.loc[0, "position"] = "striker"
    valid, report = validate_player_candidates(df)
    assert valid is False
    assert (report["check"] == "position_allowed").any()


def test_calculate_position_impact_score_works_for_all_positions() -> None:
    df = _players_df()
    scores = [calculate_position_impact_score(df.iloc[i]) for i in range(4)]
    assert all(score >= 0 for score in scores)
    assert len(set(round(score, 3) for score in scores)) == 4


def test_calculate_team_progression_score_returns_expected_positive_score() -> None:
    score = calculate_team_progression_score(_stage_df().iloc[0])
    assert score > 0


def test_add_team_progression_to_players_merges_team_probabilities() -> None:
    merged = add_team_progression_to_players(_players_df(), _stage_df())
    assert "team_progression_score" in merged.columns
    assert "has_team_progression_data" in merged.columns
    assert bool(merged["has_team_progression_data"].all()) is True


def test_calculate_golden_ball_predictions_returns_probabilities_summing_to_one() -> None:
    merged = add_team_progression_to_players(_players_df(), _stage_df())
    out = calculate_golden_ball_predictions(merged)
    assert abs(float(out["golden_ball_probability"].sum()) - 1.0) < 1e-9
    assert out.iloc[0]["golden_ball_rank"] == 1


def test_calculate_golden_boot_predictions_returns_probabilities_summing_to_one() -> None:
    merged = add_team_progression_to_players(_players_df(), _stage_df())
    out = calculate_golden_boot_predictions(merged)
    assert abs(float(out["golden_boot_probability"].sum()) - 1.0) < 1e-9
    assert out.iloc[0]["golden_boot_rank"] == 1


def test_calculate_golden_glove_predictions_only_includes_goalkeepers() -> None:
    merged = add_team_progression_to_players(_players_df(), _stage_df())
    out = calculate_golden_glove_predictions(merged)
    assert not out.empty
    assert set(out["position"].str.lower()) == {"goalkeeper"}


def test_filter_young_player_candidates_works() -> None:
    out = filter_young_player_candidates(_players_df())
    assert not out.empty
    assert (pd.to_numeric(out["age"], errors="coerce") <= 21).any() or (pd.to_datetime(out["date_of_birth"]) >= pd.Timestamp("2005-01-01")).any()


def test_calculate_young_player_predictions_only_includes_eligible_players() -> None:
    merged = add_team_progression_to_players(_players_df(), _stage_df())
    out = calculate_young_player_predictions(merged)
    assert not out.empty
    assert ((pd.to_numeric(out["age"], errors="coerce") <= 21) | (pd.to_datetime(out["date_of_birth"], errors="coerce") >= pd.Timestamp("2005-01-01"))).all()


def test_calculate_player_of_match_proxy_returns_rank() -> None:
    merged = add_team_progression_to_players(_players_df(), _stage_df())
    golden_ball = calculate_golden_ball_predictions(merged)
    out = calculate_player_of_match_proxy(golden_ball)
    assert "player_of_match_proxy_rank" in out.columns
    assert out.iloc[0]["player_of_match_proxy_rank"] == 1


def test_calculate_goal_of_tournament_proxy_returns_rank() -> None:
    merged = add_team_progression_to_players(_players_df(), _stage_df())
    out = calculate_goal_of_tournament_proxy(merged)
    assert "goal_of_tournament_proxy_rank" in out.columns
    assert out.iloc[0]["goal_of_tournament_proxy_rank"] == 1
