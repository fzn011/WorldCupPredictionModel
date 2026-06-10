"""Tests for Step 17A official data preparation."""

from __future__ import annotations

from pathlib import Path

from src.official.prepare_official_data import prepare_step17a_official_worldcup_data


def test_prepare_step17a_official_worldcup_data_creates_outputs() -> None:
    summary = prepare_step17a_official_worldcup_data()
    assert summary["status"] in {"ok", "needs_verification", "error"}
    assert Path(summary["official_teams_path"]).is_file()
    assert Path(summary["official_groups_path"]).is_file()
    assert Path(summary["official_fixtures_path"]).is_file()
    assert Path(summary["official_venues_path"]).is_file()
    assert Path(summary["official_summary_path"]).is_file()
    assert Path(summary["validation_report_path"]).is_file()
