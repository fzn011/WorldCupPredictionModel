"""End-to-end tests for awards generation with manual priors."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import src.utils.constants as C
from src.awards.prepare_awards import prepare_step18_world_cup_awards
from tests.test_prepare_awards import _official_candidates


def _write_manual_prior(path: Path) -> None:
    pd.DataFrame(
        [
            {
                "player_id": "p000",
                "player_name": "Player 0",
                "team": "France",
                "apply_manual_override": True,
                "manual_star_tier": "superstar",
                "manual_goal_prior_boost": 0.0,
                "manual_assist_prior_boost": 0.0,
                "manual_golden_ball_boost": 0.12,
                "manual_golden_boot_boost": 1.0,
                "manual_young_player_boost": 0.1,
                "manual_golden_glove_boost": 0.0,
                "manual_minutes_confidence": 0.08,
                "manual_notes": "test",
                "manual_prior_source": "unit_test",
            }
        ]
    ).to_csv(path, index=False)


def test_enriched_manual_prior_pipeline(tmp_path, monkeypatch):
    processed = tmp_path / "processed"
    processed.mkdir(parents=True)
    reports = tmp_path / "reports"
    reports.mkdir()
    monkeypatch.setattr("src.awards.prepare_awards.PROCESSED_DATA_DIR", processed)
    monkeypatch.setattr("src.awards.award_reports.REPORTS_DIR", reports)
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)

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
    profiles = pd.DataFrame(
        {
            "team": ["France", "Brazil"],
            "attacking_style_score": [50, 55],
            "discipline_score": [50, 55],
            "entertainment_score_prior": [50, 55],
            "fan_popularity_proxy": [50, 55],
        }
    )
    manual_path = tmp_path / "manual.csv"
    _write_manual_prior(manual_path)

    monkeypatch.setattr(
        "src.awards.prepare_awards.require_official_final_ready",
        lambda: {"official_final_enabled": True, "final_ready": True},
    )
    monkeypatch.setattr(
        "src.awards.award_data.require_official_final_ready",
        lambda: {"official_final_enabled": True, "final_ready": True},
    )
    monkeypatch.setattr(
        "src.official.promotion.load_official_final_mode",
        lambda: {"official_final_enabled": True},
    )
    monkeypatch.setattr(
        "src.awards.award_validation.load_official_final_mode",
        lambda: {"official_final_enabled": True},
    )
    monkeypatch.setattr("src.awards.manual_priors.PROCESSED_DATA_DIR", processed)
    monkeypatch.setattr(
        "src.awards.prepare_awards.load_official_award_candidates",
        lambda **kwargs: candidates,
    )
    monkeypatch.setattr("src.awards.prepare_awards.load_team_stage_probabilities", lambda: stages)
    monkeypatch.setattr("src.awards.prepare_awards.load_team_award_profiles", lambda: profiles)
    monkeypatch.setattr(
        "src.awards.prepare_awards.load_official_teams_for_awards",
        lambda: pd.DataFrame({"team": ["France", "Brazil"]}),
    )
    monkeypatch.setattr(
        "src.awards.prepare_awards.get_award_candidate_source",
        lambda **kwargs: C.ENRICHED_OFFICIAL_AWARD_CANDIDATES_FILE,
    )

    summary = prepare_step18_world_cup_awards(
        use_enriched_candidates=True,
        use_manual_priors=True,
        manual_prior_file=manual_path,
    )
    assert summary["validation_passed"] is True
    assert summary["use_manual_priors"] is True
    assert summary["manual_priors_applied"] == 1
    assert "manual_priors" in summary["candidate_source"]
    assert (processed / C.MANUAL_PRIOR_SUMMARY_FILE).is_file()
    assert (processed / C.MANUAL_PRIOR_VALIDATION_REPORT_FILE).is_file()


def test_awards_refuse_when_official_final_disabled(monkeypatch):
    monkeypatch.setattr(
        "src.awards.prepare_awards.require_official_final_ready",
        lambda: (_ for _ in ()).throw(RuntimeError("blocked")),
    )
    try:
        prepare_step18_world_cup_awards(use_manual_priors=True)
        raised = False
    except RuntimeError:
        raised = True
    assert raised
