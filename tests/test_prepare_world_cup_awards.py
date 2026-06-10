"""Tests for Step 17/18 World Cup awards preparation orchestrator."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import src.utils.constants as C
from src.awards import award_reports as reports_mod
from src.awards import prepare_awards as prepare_mod
from src.awards.prepare_awards import prepare_step17_world_cup_awards


def _official_candidates() -> pd.DataFrame:
    rows = []
    positions = [("GK", "goalkeeper")] * 5 + [("DF", "defender")] * 5 + [("MF", "midfielder")] * 5 + [("FW", "forward")] * 5
    for i in range(20):
        code, _group = positions[i % len(positions)]
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


def _team_profiles_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "team": ["France", "Brazil"],
            "attacking_style_score": [50, 55],
            "discipline_score": [50, 55],
            "entertainment_score_prior": [50, 55],
            "fan_popularity_proxy": [50, 55],
        }
    )


def _stage_df() -> pd.DataFrame:
    return pd.DataFrame(
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


def test_prepare_step17_world_cup_awards_returns_status_ok(monkeypatch, tmp_path: Path) -> None:
    processed = tmp_path / "processed"
    processed.mkdir(parents=True)
    teams = pd.DataFrame({"team": ["France", "Brazil"]})
    candidates = _official_candidates()

    monkeypatch.setattr(prepare_mod, "PROCESSED_DATA_DIR", processed)
    monkeypatch.setattr(reports_mod, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr("src.awards.award_data.require_official_final_ready", lambda: {"official_final_enabled": True, "final_ready": True})
    monkeypatch.setattr("src.awards.prepare_awards.require_official_final_ready", lambda: {"official_final_enabled": True, "final_ready": True})
    monkeypatch.setattr("src.awards.prepare_awards.load_official_award_candidates", lambda **kwargs: candidates)
    monkeypatch.setattr("src.awards.prepare_awards.load_team_stage_probabilities", lambda: _stage_df())
    monkeypatch.setattr("src.awards.prepare_awards.load_official_teams_for_awards", lambda: teams)
    monkeypatch.setattr("src.awards.team_awards.load_official_teams_for_awards", lambda: teams)
    monkeypatch.setattr("src.awards.prepare_awards.load_team_award_profiles", lambda: _team_profiles_df())
    def _save_report(text: str) -> str:
        report_path = tmp_path / "report.md"
        report_path.write_text(text, encoding="utf-8")
        return str(report_path)

    monkeypatch.setattr("src.awards.prepare_awards.save_world_cup_awards_report", _save_report)

    summary = prepare_step17_world_cup_awards()
    assert summary["status"] == "ok"
    assert Path(summary["combined_predictions_path"]).is_file()
    assert Path(summary["report_path"]).is_file()
    assert Path(summary["validation_report_path"]).is_file()
