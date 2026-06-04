"""Tests for Step 11 tournament setup preparation pipeline."""

from __future__ import annotations

from pathlib import Path

from src.tournament.prepare_tournament import prepare_step11_tournament_setup


def test_prepare_step11_tournament_setup_returns_status_ok() -> None:
    summary = prepare_step11_tournament_setup()
    assert summary["status"] == "ok"


def test_prepare_step11_tournament_setup_output_files_exist() -> None:
    summary = prepare_step11_tournament_setup()
    assert Path(summary["tournament_groups_path"]).is_file()
    assert Path(summary["tournament_fixtures_path"]).is_file()
    assert Path(summary["knockout_placeholders_path"]).is_file()


def test_prepare_step11_tournament_setup_validation_report_exists() -> None:
    summary = prepare_step11_tournament_setup()
    assert Path(summary["validation_report_path"]).is_file()


def test_prepare_step11_tournament_setup_structure_json_exists() -> None:
    summary = prepare_step11_tournament_setup()
    assert Path(summary["tournament_structure_path"]).is_file()
