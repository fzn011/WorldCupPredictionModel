"""Tests for Step 17 World Cup awards preparation orchestrator."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.awards import award_reports as reports_mod
from src.awards import prepare_awards as prepare_mod
from src.awards.prepare_awards import prepare_step17_world_cup_awards


def _players_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "player": [f"FWD {i}" for i in range(1, 4)] + [f"MID {i}" for i in range(1, 4)] + [f"DEF {i}" for i in range(1, 5)] + ["GK 1"],
            "team": ["France", "England", "Brazil", "France", "England", "Brazil", "France", "England", "Brazil", "Spain", "Argentina"],
            "position": ["forward", "forward", "forward", "midfielder", "midfielder", "midfielder", "defender", "defender", "defender", "defender", "goalkeeper"],
            "age": [21, 24, 26, 20, 25, 23, 27, 28, 29, 30, 31],
            "date_of_birth": ["2005-01-02", "2002-02-02", "2000-03-03", "2005-04-04", "2001-05-05", "2003-06-06", "1999-07-07", "1998-08-08", "1997-09-09", "1996-10-10", "1995-11-11"],
            "base_player_rating": [90, 88, 87, 86, 85, 84, 83, 82, 81, 80, 86],
            "expected_minutes_share": [0.9, 0.88, 0.87, 0.86, 0.85, 0.84, 0.9, 0.89, 0.88, 0.87, 0.92],
            "goals_prior": [15, 13, 12, 7, 6, 5, 2, 1, 1, 1, 0],
            "assists_prior": [6, 5, 4, 8, 7, 6, 1, 1, 1, 1, 0],
            "chance_creation_prior": [12, 11, 10, 15, 14, 13, 3, 3, 3, 3, 1],
            "defensive_actions_prior": [3, 3, 3, 11, 12, 13, 18, 18, 18, 18, 4],
            "goalkeeper_actions_prior": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 25],
            "discipline_risk": [0.12, 0.13, 0.14, 0.1, 0.11, 0.12, 0.18, 0.17, 0.16, 0.15, 0.08],
            "star_role_score": [8.5, 8.2, 8.0, 7.8, 7.6, 7.4, 6.5, 6.4, 6.3, 6.2, 7.5],
            "flair_score": [8.0, 7.5, 7.2, 7.0, 6.8, 6.5, 4.5, 4.4, 4.3, 4.2, 3.5],
        }
    )


def _team_profiles_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "team": ["France", "England", "Brazil", "Spain", "Argentina"],
            "attacking_style_score": [8.5, 8.2, 9.0, 8.4, 8.7],
            "discipline_score": [7.8, 7.4, 7.2, 8.0, 7.7],
            "entertainment_score_prior": [8.4, 8.1, 9.1, 8.5, 8.6],
            "fan_popularity_proxy": [8.8, 8.7, 9.2, 8.9, 9.0],
        }
    )


def _stage_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "team": ["France", "England", "Brazil", "Spain", "Argentina"],
            "round_of_32_probability": [1.0, 1.0, 1.0, 1.0, 1.0],
            "round_of_16_probability": [0.8, 0.7, 0.75, 0.78, 0.82],
            "quarter_final_probability": [0.6, 0.5, 0.55, 0.58, 0.62],
            "semi_final_probability": [0.4, 0.3, 0.35, 0.38, 0.42],
            "final_probability": [0.25, 0.2, 0.22, 0.24, 0.28],
            "champion_probability": [0.2, 0.12, 0.15, 0.17, 0.21],
        }
    )


def test_prepare_step17_world_cup_awards_returns_status_ok(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("src.awards.prepare_awards.load_player_candidates", lambda: _players_df())
    monkeypatch.setattr("src.awards.prepare_awards.validate_player_candidates", lambda df: (True, pd.DataFrame([{"check": "ok", "passed": True}])))
    monkeypatch.setattr("src.awards.prepare_awards.load_team_award_profiles", lambda: _team_profiles_df())
    monkeypatch.setattr("src.awards.prepare_awards.validate_team_award_profiles", lambda df: (True, pd.DataFrame([{"check": "ok", "passed": True}])))
    monkeypatch.setattr("src.awards.prepare_awards.load_team_stage_probabilities", lambda: _stage_df())

    monkeypatch.setattr(prepare_mod, "PROCESSED_DATA_DIR", tmp_path / "processed")
    monkeypatch.setattr(reports_mod, "REPORTS_DIR", tmp_path / "reports")

    summary = prepare_step17_world_cup_awards()
    assert summary["status"] == "ok"
    assert Path(summary["combined_predictions_path"]).is_file()
    assert Path(summary["report_path"]).is_file()
    assert Path(summary["validation_report_path"]).is_file()
