"""Tests for manual prior template export script."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd

import src.utils.constants as C


def test_export_player_award_prior_template_script(tmp_path, monkeypatch):
    processed = tmp_path / "processed"
    processed.mkdir()
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)

    candidates = pd.DataFrame(
        {
            "player_id": ["p001"],
            "player_name": ["Test Player"],
            "team": ["France"],
            "team_code": ["FRA"],
            "shirt_number": [10],
            "position_code": ["FW"],
            "position": ["FW"],
            "date_of_birth": ["2000-01-01"],
            "age_at_tournament_start": [26],
            "club": ["Test FC"],
            "height_cm": [180],
            "base_player_rating": [60],
            "expected_minutes_share": [0.45],
            "goals_prior": [1.5],
            "assists_prior": [0.7],
            "chance_creation_prior": [2],
            "defensive_actions_prior": [0.5],
            "goalkeeper_actions_prior": [0],
            "discipline_risk": [0.25],
            "star_role_score": [1.5],
            "flair_score": [1.0],
            "has_player_prior": [True],
            "prior_source": ["test"],
            "source": ["test"],
            "last_verified_at": ["2026-01-01"],
        }
    )
    monkeypatch.setattr(
        "src.awards.award_data.load_official_award_candidates",
        lambda **kwargs: candidates,
    )
    monkeypatch.setattr(
        "src.awards.award_data.require_official_final_ready",
        lambda: {"official_final_enabled": True},
    )

    output = tmp_path / "manual_template.csv"
    script = Path(__file__).resolve().parents[1] / "scripts" / "export_player_award_prior_template.py"
    mod = _load_export_script(script)
    rc = mod.main(["--output", str(output), "--no-enriched"])
    assert rc == 0
    assert output.is_file()
    df = pd.read_csv(output)
    assert "apply_manual_override" in df.columns
    assert len(df) == 1


def _load_export_script(path: Path):
    import importlib.util

    spec = importlib.util.spec_from_file_location("export_player_award_prior_template", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module
