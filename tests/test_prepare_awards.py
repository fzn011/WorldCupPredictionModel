"""Tests for Step 18 prepare awards orchestrator."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import src.utils.constants as C
from src.awards.prepare_awards import prepare_step18_world_cup_awards


def _official_candidates(n: int = 20) -> pd.DataFrame:
    rows = []
    positions = [("GK", "goalkeeper")] * 5 + [("DF", "defender")] * 5 + [("MF", "midfielder")] * 5 + [("FW", "forward")] * 5
    for i in range(n):
        code, group = positions[i % len(positions)]
        row = {col: "" for col in C.OFFICIAL_AWARD_CANDIDATES_REQUIRED_COLUMNS}
        row.update(
            {
                "player_id": f"p{i:03d}",
                "player_name": f"Player {i}",
                "team": "France" if i < 10 else "Brazil",
                "team_code": "FRA" if i < 10 else "BRA",
                "shirt_number": i + 1,
                "position_code": code,
                "position": code,
                "base_player_rating": 50 + i,
                "expected_minutes_share": 0.7,
                "goals_prior": 1,
                "assists_prior": 1,
                "chance_creation_prior": 1,
                "defensive_actions_prior": 1,
                "goalkeeper_actions_prior": 2 if code == "GK" else 0,
                "discipline_risk": 0.5,
                "star_role_score": 1,
                "flair_score": 1,
                "has_player_prior": True,
                "prior_source": "test",
                "source": "fifa_squad_pdf",
                "last_verified_at": "2026-01-01",
                "age_at_tournament_start": 19 if i == 0 else 28,
                "date_of_birth": "2010-01-01" if i == 0 else "1995-01-01",
            }
        )
        rows.append(row)
    return pd.DataFrame(rows)


def test_prepare_step18_world_cup_awards_returns_ok(tmp_path, monkeypatch):
    processed = tmp_path / "processed"
    processed.mkdir(parents=True)
    monkeypatch.setattr("src.awards.prepare_awards.PROCESSED_DATA_DIR", processed)

    candidates = _official_candidates()
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
    teams = pd.DataFrame({"team": ["France", "Brazil"]})
    profiles = pd.DataFrame(
        {
            "team": ["France", "Brazil"],
            "attacking_style_score": [50, 55],
            "discipline_score": [50, 55],
            "entertainment_score_prior": [50, 55],
            "fan_popularity_proxy": [50, 55],
        }
    )

    monkeypatch.setattr("src.awards.award_data.require_official_final_ready", lambda: {"official_final_enabled": True, "final_ready": True})
    monkeypatch.setattr("src.awards.prepare_awards.require_official_final_ready", lambda: {"official_final_enabled": True, "final_ready": True})
    monkeypatch.setattr("src.awards.prepare_awards.load_official_award_candidates", lambda **kwargs: candidates)
    monkeypatch.setattr("src.awards.prepare_awards.load_team_stage_probabilities", lambda: stages)
    monkeypatch.setattr("src.awards.prepare_awards.load_official_teams_for_awards", lambda: teams)
    monkeypatch.setattr("src.awards.team_awards.load_official_teams_for_awards", lambda: teams)
    monkeypatch.setattr("src.awards.prepare_awards.load_team_award_profiles", lambda: profiles)
    def _save_report(text: str) -> str:
        report_path = tmp_path / "report.md"
        report_path.write_text(text, encoding="utf-8")
        return str(report_path)

    monkeypatch.setattr("src.awards.prepare_awards.save_world_cup_awards_report", _save_report)

    summary = prepare_step18_world_cup_awards()
    assert summary["status"] == "ok"
    assert Path(processed / C.GOLDEN_BALL_PREDICTIONS_FILE).is_file()
