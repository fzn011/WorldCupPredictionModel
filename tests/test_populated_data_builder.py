"""Tests for Step 17F populated data builder."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import src.utils.constants as C
from src.official.populated_data_builder import (
    build_all_populated_official_data,
    build_populated_player_priors,
)


def test_build_populated_player_priors_excludes_non_official(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(C, "PROCESSED_DATA_DIR", Path("data/processed"))
    monkeypatch.setattr(C, "SAMPLE_DATA_DIR", Path("data/sample"))
    processed = tmp_path / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    existing = pd.DataFrame(
        [
            {"player": "Official One", "team": "France", "base_player_rating": 60, "expected_minutes_share": 0.5, "goals_prior": 0, "assists_prior": 0, "chance_creation_prior": 0, "defensive_actions_prior": 0, "goalkeeper_actions_prior": 0, "discipline_risk": 0.5, "star_role_score": 0, "flair_score": 0, "notes": ""},
            {"player": "Random Guy", "team": "Otherland", "base_player_rating": 50, "expected_minutes_share": 0.5, "goals_prior": 0, "assists_prior": 0, "chance_creation_prior": 0, "defensive_actions_prior": 0, "goalkeeper_actions_prior": 0, "discipline_risk": 0.5, "star_role_score": 0, "flair_score": 0, "notes": ""},
        ]
    )
    existing.to_csv(processed / C.PLAYER_AWARD_PRIORS_FILE, index=False)
    players_df = pd.DataFrame(
        [
            {"player_name": "Official One", "team": "France"},
            {"player_name": "Official Two", "team": "France"},
        ]
    )
    priors_df, unmatched = build_populated_player_priors(players_df)
    assert len(unmatched) == 1
    assert len(priors_df) == 2
    assert "Random Guy" not in priors_df["player"].values


def test_build_all_populated_official_data_returns_paths(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    processed = tmp_path / C.OFFICIAL_PROCESSED_DIR
    processed.mkdir(parents=True)
    teams = pd.DataFrame(
        {
            "team": ["Mexico"],
            "team_code": ["MEX"],
            "confederation": ["CONCACAF"],
            "group": ["A"],
            "group_slot": [1],
            "is_host": [1],
            "qualified": [1],
            "source": ["fifa_official_manual"],
        }
    )
    teams.to_csv(processed / C.OFFICIAL_TEAMS_FILE, index=False)
    result = build_all_populated_official_data()
    assert "paths" in result
    assert Path(result["paths"]["teams"]).is_file()
