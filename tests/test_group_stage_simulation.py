"""Tests for Step 12 group-stage simulation core functions."""

from __future__ import annotations

import pandas as pd

from src.simulation.group_stage import (
    normalize_probabilities,
    sample_match_result,
    sample_scoreline,
    simulate_group_match,
    simulate_group_stage,
)



def test_normalize_probabilities_handles_valid_probabilities() -> None:
    out = normalize_probabilities({"team_a_loss": 0.2, "draw": 0.3, "team_a_win": 0.5})
    assert abs(sum(out.values()) - 1.0) < 1e-9
    assert set(out.keys()) == {"team_a_loss", "draw", "team_a_win"}



def test_normalize_probabilities_handles_missing_or_zero_probabilities() -> None:
    out = normalize_probabilities({"team_a_win": 0})
    assert abs(out["team_a_loss"] - 1 / 3) < 1e-9
    assert abs(out["draw"] - 1 / 3) < 1e-9
    assert abs(out["team_a_win"] - 1 / 3) < 1e-9



def test_sample_match_result_returns_valid_label() -> None:
    result = sample_match_result({"team_a_loss": 0.1, "draw": 0.2, "team_a_win": 0.7})
    assert result in {"team_a_loss", "draw", "team_a_win"}



def test_sample_scoreline_consistent_with_result_label() -> None:
    a_win = sample_scoreline("team_a_win")
    draw = sample_scoreline("draw")
    a_loss = sample_scoreline("team_a_loss")

    assert a_win[0] > a_win[1]
    assert draw[0] == draw[1]
    assert a_loss[0] < a_loss[1]



def test_simulate_group_match_returns_required_columns(monkeypatch) -> None:
    fixture = pd.Series(
        {
            "match_id": "G-A-01",
            "group": "A",
            "matchday": 1,
            "date": "2026-06-11",
            "team_a": "Mexico",
            "team_b": "South Africa",
            "city": "TBD City",
            "country": "TBD Country",
            "neutral": 1,
            "tournament": "FIFA World Cup",
        }
    )

    monkeypatch.setattr(
        "src.simulation.group_stage.predict_future_match",
        lambda **_: {
            "model_type": "ranking_enhanced",
            "probabilities": {"team_a_loss": 0.25, "draw": 0.30, "team_a_win": 0.45},
        },
    )

    out = simulate_group_match(fixture, random_seed=42)
    required = {
        "match_id",
        "group",
        "matchday",
        "date",
        "team_a",
        "team_b",
        "model_type",
        "team_a_loss_probability",
        "draw_probability",
        "team_a_win_probability",
        "simulated_result",
        "team_a_score",
        "team_b_score",
        "winner",
        "is_draw",
        "points_team_a",
        "points_team_b",
    }
    assert required.issubset(set(out.keys()))



def test_simulate_group_stage_returns_expected_rows_for_small_fixture_set(monkeypatch) -> None:
    fixtures_df = pd.DataFrame(
        [
            {
                "match_id": "G-A-01",
                "stage": "group_stage",
                "group": "A",
                "matchday": 1,
                "date": "2026-06-11",
                "team_a": "Mexico",
                "team_b": "South Africa",
                "city": "TBD City",
                "country": "TBD Country",
                "neutral": 1,
                "tournament": "FIFA World Cup",
            },
            {
                "match_id": "G-A-02",
                "stage": "group_stage",
                "group": "A",
                "matchday": 1,
                "date": "2026-06-11",
                "team_a": "South Korea",
                "team_b": "Czechia",
                "city": "TBD City",
                "country": "TBD Country",
                "neutral": 1,
                "tournament": "FIFA World Cup",
            },
        ]
    )

    monkeypatch.setattr(
        "src.simulation.group_stage.predict_future_match",
        lambda **_: {
            "model_type": "ranking_enhanced",
            "probabilities": {"team_a_loss": 0.2, "draw": 0.2, "team_a_win": 0.6},
        },
    )

    out_df = simulate_group_stage(fixtures_df=fixtures_df, random_seed=42)
    assert len(out_df) == 2
