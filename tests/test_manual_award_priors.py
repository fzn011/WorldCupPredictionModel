"""Tests for Step 20 manual star-player prior overrides."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

import src.utils.constants as C
from src.awards.manual_priors import (
    apply_manual_priors_to_candidates,
    export_manual_prior_template,
    load_manual_prior_file,
    match_manual_rows_to_candidates,
    validate_manual_prior_columns,
)


def _sample_candidates() -> pd.DataFrame:
    rows = [
        {
            "player_id": "p001",
            "player_name": "STAR One",
            "team": "France",
            "team_code": "FRA",
            "shirt_number": 10,
            "position_code": "FW",
            "position": "FW",
            "date_of_birth": "1998-01-01",
            "age_at_tournament_start": 28,
            "club": "Test FC",
            "height_cm": 180,
            "base_player_rating": 60,
            "expected_minutes_share": 0.45,
            "goals_prior": 1.5,
            "assists_prior": 0.7,
            "chance_creation_prior": 2,
            "defensive_actions_prior": 0.5,
            "goalkeeper_actions_prior": 0,
            "discipline_risk": 0.25,
            "star_role_score": 1.5,
            "flair_score": 1.0,
            "has_player_prior": True,
            "prior_source": "test",
            "source": "test",
            "last_verified_at": "2026-01-01",
        },
        {
            "player_id": "p002",
            "player_name": "KEEPER Two",
            "team": "France",
            "team_code": "FRA",
            "shirt_number": 1,
            "position_code": "GK",
            "position": "GK",
            "date_of_birth": "1995-01-01",
            "age_at_tournament_start": 31,
            "club": "Test FC",
            "height_cm": 190,
            "base_player_rating": 58,
            "expected_minutes_share": 0.35,
            "goals_prior": 0,
            "assists_prior": 0,
            "chance_creation_prior": 0,
            "defensive_actions_prior": 3,
            "goalkeeper_actions_prior": 5,
            "discipline_risk": 0.25,
            "star_role_score": 1.0,
            "flair_score": 0.2,
            "has_player_prior": True,
            "prior_source": "test",
            "source": "test",
            "last_verified_at": "2026-01-01",
        },
    ]
    return pd.DataFrame(rows)


def _manual_row(**overrides) -> dict:
    base = {
        "player_id": "p001",
        "player_name": "STAR One",
        "team": "France",
        "apply_manual_override": True,
        "manual_star_tier": "superstar",
        "manual_goal_prior_boost": 0.5,
        "manual_assist_prior_boost": 0.0,
        "manual_golden_ball_boost": 0.08,
        "manual_golden_boot_boost": 0.5,
        "manual_young_player_boost": 0.0,
        "manual_golden_glove_boost": 0.0,
        "manual_minutes_confidence": 0.05,
        "manual_notes": "test",
        "manual_prior_source": "unit_test",
    }
    base.update(overrides)
    return base


def test_validate_manual_prior_columns():
    ok, missing = validate_manual_prior_columns(pd.DataFrame({"player_id": ["p1"], "player_name": ["A"], "team": ["X"], "apply_manual_override": [False]}))
    assert ok
    assert missing == []


def test_unmatched_manual_players_are_ignored():
    candidates = _sample_candidates()
    manual = pd.DataFrame(
        [
            _manual_row(player_id="ghost", player_name="Ghost Player", team="Nowhere"),
        ]
    )
    matched = match_manual_rows_to_candidates(manual, candidates)
    assert matched.iloc[0]["match_status"] == "unmatched"
    updated, summary = apply_manual_priors_to_candidates(candidates, manual)
    assert summary["overrides_applied"] == 0
    assert summary["unmatched_manual_rows_ignored"] == 1
    assert set(updated["player_id"]) == set(candidates["player_id"])


def test_manual_priors_cannot_add_new_candidates():
    candidates = _sample_candidates()
    manual = pd.DataFrame([_manual_row()])
    updated, summary = apply_manual_priors_to_candidates(candidates, manual)
    assert len(updated) == len(candidates)
    assert summary["overrides_applied"] == 1
    assert updated.loc[updated["player_id"] == "p001", "prior_source"].iloc[0] == "manual_override"


def test_boosts_are_clipped_to_safe_limits():
    candidates = _sample_candidates()
    manual = pd.DataFrame(
        [
            _manual_row(
                manual_golden_ball_boost=99.0,
                manual_golden_boot_boost=99.0,
                manual_minutes_confidence=99.0,
            )
        ]
    )
    updated, summary = apply_manual_priors_to_candidates(candidates, manual)
    assert summary["invalid_boost_rows_clipped"] >= 1
    row = updated[updated["player_id"] == "p001"].iloc[0]
    assert float(row["expected_minutes_share"]) <= 1.0


def test_apply_manual_override_false_is_skipped():
    candidates = _sample_candidates()
    manual = pd.DataFrame([_manual_row(apply_manual_override=False)])
    updated, summary = apply_manual_priors_to_candidates(candidates, manual)
    assert summary["overrides_applied"] == 0


def test_export_manual_prior_template_has_manual_columns():
    template = export_manual_prior_template(_sample_candidates())
    for col in C.MANUAL_PRIOR_EDITABLE_COLUMNS:
        assert col in template.columns
    assert len(template) == 2


def test_load_manual_prior_file(tmp_path: Path):
    path = tmp_path / "manual.csv"
    pd.DataFrame([_manual_row()]).to_csv(path, index=False)
    loaded = load_manual_prior_file(path)
    assert len(loaded) == 1


def test_manual_prior_missing_columns_raises():
    candidates = _sample_candidates()
    manual = pd.DataFrame([{"player_id": "p001"}])
    with pytest.raises(ValueError, match="missing required columns"):
        apply_manual_priors_to_candidates(candidates, manual)
