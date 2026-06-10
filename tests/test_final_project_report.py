"""Tests for Step 19 final project reporting."""

from __future__ import annotations

from src.reports.final_project_report import (
    collect_final_project_status,
    create_final_project_summary,
    create_final_validation_report,
)


def test_collect_final_project_status_returns_expected_keys():
    status = collect_final_project_status()
    for key in (
        "official_final_enabled",
        "monte_carlo_available",
        "awards_available",
        "test_command",
        "key_outputs",
    ):
        assert key in status


def test_create_final_project_summary_returns_expected_keys():
    summary = create_final_project_summary()
    for key in (
        "project_name",
        "status",
        "official_final_enabled",
        "monte_carlo_available",
        "awards_available",
        "notes",
    ):
        assert key in summary


def test_create_final_validation_report_returns_dataframe():
    df = create_final_validation_report()
    assert not df.empty
    assert "check" in df.columns
    assert "passed" in df.columns
