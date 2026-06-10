"""Tests for Step 19 player prior enrichment."""

from __future__ import annotations

import pandas as pd
import pytest

import src.utils.constants as C
from src.awards.prior_enrichment import (
    apply_squad_role_heuristics,
    create_position_based_default_priors,
    measure_prior_quality,
    merge_enriched_priors_into_award_candidates,
)


def _sample_candidates() -> pd.DataFrame:
    rows = []
    for i, (code, group) in enumerate([("GK", "goalkeeper"), ("DF", "defender"), ("MF", "midfielder"), ("FW", "forward")]):
        rows.append(
            {
                "player_id": f"p{i:03d}",
                "player_name": f"Player {i}",
                "team": "France",
                "team_code": "FRA",
                "shirt_number": i + 1,
                "position_code": code,
                "position": code,
                "date_of_birth": "1995-01-01",
                "age_at_tournament_start": 28,
                "club": "Test FC",
                "height_cm": 180,
                "base_player_rating": 50,
                "expected_minutes_share": 0.5,
                "goals_prior": 0,
                "assists_prior": 0,
                "chance_creation_prior": 0,
                "defensive_actions_prior": 0,
                "goalkeeper_actions_prior": 0,
                "discipline_risk": 0.5,
                "star_role_score": 0,
                "flair_score": 0,
                "has_player_prior": True,
                "prior_source": "user_prior",
                "source": "test",
                "last_verified_at": "2026-01-01",
            }
        )
    return pd.DataFrame(rows)


def test_create_position_based_default_priors_preserves_official_players():
    df = _sample_candidates()
    enriched = create_position_based_default_priors(df)
    assert set(enriched["player_id"]) == set(df["player_id"])
    assert enriched["goals_prior"].nunique() > 1


def test_no_non_official_players_added():
    df = _sample_candidates()
    enriched = create_position_based_default_priors(df)
    assert len(enriched) == len(df)


def test_expected_minutes_share_clipped():
    df = _sample_candidates()
    enriched = create_position_based_default_priors(df)
    enriched = apply_squad_role_heuristics(enriched)
    mins = pd.to_numeric(enriched["expected_minutes_share"], errors="coerce")
    assert mins.min() >= 0.0
    assert mins.max() <= 1.0


def test_measure_prior_quality_returns_metrics():
    enriched = create_position_based_default_priors(_sample_candidates())
    summary, report = measure_prior_quality(enriched)
    assert summary["candidate_count"] == 4
    assert "flatness_score" in summary
    assert not report.empty


def test_merge_enriched_priors_keeps_player_id_set(monkeypatch, tmp_path):
    processed = tmp_path / "processed"
    processed.mkdir()
    monkeypatch.setattr("src.awards.prior_enrichment.PROCESSED_DATA_DIR", processed)
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)

    base = _sample_candidates()
    enriched = create_position_based_default_priors(base)
    enriched.to_csv(processed / C.ENRICHED_PLAYER_AWARD_PRIORS_FILE, index=False)
    base.to_csv(processed / C.OFFICIAL_AWARD_CANDIDATES_FILE, index=False)

    official_players = base[["player_id", "player_name", "team"]].copy()
    monkeypatch.setattr(
        "src.awards.prior_enrichment.load_official_players",
        lambda: official_players,
    )
    monkeypatch.setattr(
        "src.awards.prior_enrichment.load_current_award_candidates",
        lambda: base,
    )
    monkeypatch.setattr(
        "src.awards.prior_enrichment.require_official_final_ready",
        lambda: {"official_final_enabled": True},
    )

    result = merge_enriched_priors_into_award_candidates(update_official=False)
    merged = pd.read_csv(result["enriched_candidates_path"])
    assert set(merged["player_id"]) == set(base["player_id"])
