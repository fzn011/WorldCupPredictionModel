"""Tests for Step 17G official import execution."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import src.utils.constants as C
from src.official.import_execution import (
    create_import_execution_summary,
    detect_available_import_inputs,
    run_import_preview,
    run_import_staging,
    save_import_execution_report,
)
from src.official.prepare_import_execution import prepare_step17g_official_import_execution


def test_detect_available_import_inputs_detects_supplied_files(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    sched = tmp_path / "sched.xlsx"
    sched.write_bytes(b"x")
    result = detect_available_import_inputs(schedule_file=str(sched))
    assert result["has_schedule_file"] is True
    assert "schedule_file" in result["detected_files"]


def test_run_import_staging_no_input_files(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    (tmp_path / C.OFFICIAL_SOURCE_STAGING_DIR).mkdir(parents=True)
    result = run_import_staging()
    assert result["status"] == "no_input_files"


def test_run_import_preview_empty_staged(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    (tmp_path / C.OFFICIAL_SOURCE_STAGING_DIR).mkdir(parents=True)
    result = run_import_preview()
    assert result["status"] == "no_staged_data"


def test_create_import_execution_summary_returns_expected_keys():
    summary = create_import_execution_summary(
        {"status": "no_input_files", "staged_fixtures_count": 0, "staged_players_count": 0},
        {"status": "no_staged_data"},
        None,
        {"is_official_final_ready": False, "summary": {"blocker_count": 1, "warning_count": 0}},
    )
    for key in (
        "status",
        "ready_for_apply",
        "final_ready",
        "official_final_enabled",
        "next_action",
    ):
        assert key in summary


def test_prepare_step17g_returns_valid_status(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    (tmp_path / C.OFFICIAL_SOURCE_STAGING_DIR).mkdir(parents=True)
    (tmp_path / C.OFFICIAL_POPULATED_REPORTS_DIR).mkdir(parents=True)
    (tmp_path / C.OFFICIAL_PROCESSED_DIR).mkdir(parents=True)
    result = prepare_step17g_official_import_execution()
    assert result["status"] in {
        "no_input_files",
        "staged_needs_review",
        "blocked_not_ready",
        "ready_for_apply",
    }
    assert Path(result["import_execution_report_path"]).is_file()


def test_save_import_execution_report(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    path = save_import_execution_report({"status": "test"})
    assert Path(path).is_file()
