"""Tests for Step 13 knockout simulation core functions."""

from __future__ import annotations

import pandas as pd

from src.simulation.knockout_stage import (
    assign_knockout_seeds,
    build_next_round_matches,
    convert_to_no_draw_probabilities,
    create_round_of_32_bracket,
    sample_knockout_scoreline,
    sample_knockout_winner,
)


def _sample_qualifiers() -> pd.DataFrame:
    rows = []
    for seed in range(1, 33):
        rows.append(
            {
                "team": f"Team {seed:02d}",
                "group": chr(64 + ((seed - 1) % 12) + 1),
                "group_rank": 1 if seed <= 16 else 3,
                "qualification_type": "automatic_top_two" if seed <= 24 else "best_third_place",
                "points": 6 + (seed % 4),
                "goal_difference": 3 - (seed % 5),
                "goals_for": 5 + (seed % 6),
            }
        )
    return pd.DataFrame(rows)


def test_convert_to_no_draw_probabilities_returns_normalized_knockout_distribution() -> None:
    out = convert_to_no_draw_probabilities({"team_a_loss": 0.35, "draw": 0.25, "team_a_win": 0.40})
    assert abs(out["team_a_knockout_win_probability"] + out["team_b_knockout_win_probability"] - 1.0) < 1e-9
    assert abs(out["team_a_knockout_win_probability"] - (0.40 / 0.75)) < 1e-9
    assert abs(out["team_b_knockout_win_probability"] - (0.35 / 0.75)) < 1e-9


def test_sample_knockout_winner_returns_one_of_the_two_teams() -> None:
    winner = sample_knockout_winner(
        "Team A",
        "Team B",
        {
            "team_a_knockout_win_probability": 0.6,
            "team_b_knockout_win_probability": 0.4,
        }
    )
    assert winner in {"Team A", "Team B"}


def test_sample_knockout_scoreline_returns_valid_scoreline_and_method() -> None:
    team_a_score, team_b_score, method = sample_knockout_scoreline("team_a_win_regular")
    assert team_a_score > team_b_score
    assert method == "regular_time"

    team_a_score, team_b_score, method = sample_knockout_scoreline("team_b_win_extra")
    assert team_a_score == team_b_score
    assert method == "extra_time_or_penalties"

    team_a_score, team_b_score, method = sample_knockout_scoreline("Team A", "Team B", "Team A", "draw")
    assert team_a_score == team_b_score
    assert method == "extra_time_or_penalties"


def test_create_round_of_32_bracket_creates_sixteen_matches() -> None:
    seeded = assign_knockout_seeds(_sample_qualifiers())
    bracket = create_round_of_32_bracket(seeded)
    assert len(bracket) == 16
    assert list(bracket["match_id"]) == [f"R32-{i:02d}" for i in range(1, 17)]
    assert bracket.iloc[0]["seed_a"] == 1
    assert bracket.iloc[0]["seed_b"] == 32
    assert bracket.iloc[0]["winner_to"] == "R16-01"


def test_build_next_round_matches_pairs_winners_in_order() -> None:
    previous = pd.DataFrame(
        [
            {"match_id": "R32-01", "winner": "Team A"},
            {"match_id": "R32-02", "winner": "Team B"},
            {"match_id": "R32-03", "winner": "Team C"},
            {"match_id": "R32-04", "winner": "Team D"},
        ]
    )
    next_round = build_next_round_matches(previous, "round_of_16")
    assert len(next_round) == 2
    assert next_round.iloc[0]["team_a"] == "Team A"
    assert next_round.iloc[0]["team_b"] == "Team B"
    assert next_round.iloc[1]["team_a"] == "Team C"
    assert next_round.iloc[1]["team_b"] == "Team D"
