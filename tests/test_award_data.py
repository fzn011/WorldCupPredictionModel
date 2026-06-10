"""Tests for Step 18 award data loaders."""

from __future__ import annotations

import json

import pandas as pd
import pytest

import src.utils.constants as C
from src.awards.award_data import (
    load_official_award_candidates,
    merge_players_with_team_progression,
    require_official_final_ready,
)


def test_require_official_final_ready_raises_when_disabled(tmp_path, monkeypatch):
    processed = tmp_path / "data" / "official" / "processed"
    processed.mkdir(parents=True)
    (processed / C.OFFICIAL_FINAL_MODE_FLAG_FILE).write_text(
        json.dumps({"official_final_enabled": False}),
        encoding="utf-8",
    )
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr("src.awards.award_data.PROJECT_ROOT", tmp_path)
    monkeypatch.setattr("src.awards.award_data.OFFICIAL_PROCESSED_DIR", processed)
    monkeypatch.setattr("src.awards.award_data.PROCESSED_DATA_DIR", tmp_path / "data" / "processed")

    with pytest.raises(RuntimeError, match="official_final"):
        require_official_final_ready()


def test_load_official_award_candidates_loads_official_candidates(tmp_path, monkeypatch):
    processed = tmp_path / "data" / "processed"
    official = tmp_path / "data" / "official" / "processed"
    processed.mkdir(parents=True)
    official.mkdir(parents=True)
    (official / C.OFFICIAL_FINAL_MODE_FLAG_FILE).write_text(
        json.dumps({"official_final_enabled": True}),
        encoding="utf-8",
    )

    row = {col: "" for col in C.OFFICIAL_AWARD_CANDIDATES_REQUIRED_COLUMNS}
    row.update(
        {
            "player_id": "p1",
            "team": "France",
            "team_code": "FRA",
            "shirt_number": 10,
            "position_code": "FW",
            "position": "FW",
            "player_name": "Test Player",
            "base_player_rating": 60,
            "expected_minutes_share": 0.8,
            "goals_prior": 2,
            "assists_prior": 1,
            "chance_creation_prior": 1,
            "defensive_actions_prior": 0,
            "goalkeeper_actions_prior": 0,
            "discipline_risk": 0.5,
            "star_role_score": 1,
            "flair_score": 1,
            "has_player_prior": True,
            "prior_source": "test",
            "source": "fifa_squad_pdf",
            "last_verified_at": "2026-01-01",
        }
    )
    pd.DataFrame([row]).to_csv(processed / C.OFFICIAL_AWARD_CANDIDATES_FILE, index=False)
    pd.DataFrame({"team": ["France"] * 48}).to_csv(official / C.OFFICIAL_TEAMS_FILE, index=False)

    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr("src.awards.award_data.PROJECT_ROOT", tmp_path)
    monkeypatch.setattr("src.awards.award_data.PROCESSED_DATA_DIR", processed)
    monkeypatch.setattr("src.awards.award_data.OFFICIAL_PROCESSED_DIR", official)
    monkeypatch.setattr(
        "src.awards.award_data.evaluate_official_final_readiness",
        lambda: {"is_official_final_ready": True},
    )
    monkeypatch.setattr(
        "src.official.loaders.load_official_teams",
        lambda: pd.DataFrame({"team": ["France"]}),
    )

    df = load_official_award_candidates()
    assert len(df) == 1
    assert df.iloc[0]["player_name"] == "Test Player"


def test_merge_players_with_team_progression_adds_fields():
    players = pd.DataFrame(
        {
            "player_name": ["A"],
            "team": ["France"],
            "position_code": ["FW"],
            "position": "FW",
        }
    )
    stages = pd.DataFrame(
        {
            "team": ["France"],
            "round_of_32_probability": [0.8],
            "round_of_16_probability": [0.5],
            "quarter_final_probability": [0.2],
            "semi_final_probability": [0.1],
            "final_probability": [0.05],
            "champion_probability": [0.02],
        }
    )
    merged = merge_players_with_team_progression(players, stages)
    assert "team_progression_score" in merged.columns
    assert bool(merged.iloc[0]["has_team_progression_data"])
