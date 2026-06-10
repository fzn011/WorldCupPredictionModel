"""Tests for Step 17 awards reporting utilities."""

from __future__ import annotations

import pandas as pd

from src.awards.award_reports import create_combined_awards_table, create_world_cup_awards_markdown_report, create_world_cup_awards_summary


def _outputs() -> dict:
    golden_ball = pd.DataFrame({"golden_ball_rank": [1], "player": ["Player A"], "team": ["France"], "position": ["forward"], "golden_ball_probability": [0.5], "award_podium": ["Golden Ball"], "final_golden_ball_score": [100.0]})
    golden_boot = pd.DataFrame({"golden_boot_rank": [1], "player": ["Player B"], "team": ["England"], "position": ["forward"], "golden_boot_probability": [0.5], "boot_podium": ["Golden Boot"], "golden_boot_tiebreak_score": [8.0], "expected_goals_score": [7.5]})
    golden_glove = pd.DataFrame({"golden_glove_rank": [1], "player": ["Player C"], "team": ["Brazil"], "position": ["goalkeeper"], "golden_glove_probability": [1.0], "award": ["Golden Glove"], "golden_glove_score": [90.0]})
    young = pd.DataFrame({"young_player_rank": [1], "player": ["Player D"], "team": ["Spain"], "position": ["midfielder"], "young_player_probability": [1.0], "award": ["Young Player Award"], "young_player_score": [88.0]})
    fair = pd.DataFrame({"fair_play_rank": [1], "team": ["Japan"], "fair_play_probability": [1.0], "award": ["Fair Play Trophy"], "fair_play_score": [10.0]})
    entertaining = pd.DataFrame({"most_entertaining_rank": [1], "team": ["Brazil"], "most_entertaining_probability": [1.0], "award": ["Most Entertaining Team"], "most_entertaining_score": [15.0]})
    team_xi = pd.DataFrame({"formation_slot": ["GK1"], "player": ["Player C"], "team": ["Brazil"], "position": ["goalkeeper"], "final_golden_ball_score": [90.0], "golden_ball_probability": [0.2], "award": ["Predicted Team of the Tournament"]})
    potm = pd.DataFrame({"player_of_match_proxy_rank": [1], "player": ["Player A"], "team": ["France"], "position": ["forward"], "estimated_potm_count": [2.5], "player_impact_share_proxy": [0.4]})
    got = pd.DataFrame({"goal_of_tournament_proxy_rank": [1], "player": ["Player B"], "team": ["England"], "position": ["forward"], "goal_of_tournament_proxy_score": [5.0], "goal_of_tournament_proxy_probability": [0.5]})
    return {
        "golden_ball": golden_ball,
        "golden_boot": golden_boot,
        "golden_glove": golden_glove,
        "young_player": young,
        "fair_play": fair,
        "most_entertaining": entertaining,
        "team_of_tournament": team_xi,
        "player_of_match_proxy": potm,
        "goal_of_tournament_proxy": got,
    }


def test_create_world_cup_awards_markdown_report_returns_markdown_string() -> None:
    outputs = _outputs()
    summary = create_world_cup_awards_summary(outputs, validation_passed=True)
    report = create_world_cup_awards_markdown_report(outputs, summary)
    assert isinstance(report, str)
    assert "# FIFA World Cup Awards Predictor Report" in report


def test_create_combined_awards_table_returns_expected_columns() -> None:
    combined = create_combined_awards_table(_outputs())
    assert not combined.empty
    for col in ["award_category", "rank", "award", "player", "team", "position", "score", "probability", "notes"]:
        assert col in combined.columns
