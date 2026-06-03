"""Tests for the Step 3 dataset-preparation pipeline."""

from __future__ import annotations

from pathlib import Path

from src.data.prepare_datasets import prepare_step3_clean_datasets


def test_prepare_step3_returns_summary() -> None:
    summary = prepare_step3_clean_datasets()
    assert isinstance(summary, dict)
    assert summary["status"] == "ok"
    assert summary["canonical_rows"] >= 0
    assert summary["unique_teams"] >= 0


def test_prepare_step3_writes_outputs() -> None:
    summary = prepare_step3_clean_datasets()
    paths = summary["paths"]
    assert Path(paths["canonical_matches"]).is_file()
    assert Path(paths["team_registry"]).is_file()
    assert Path(paths["data_quality_report"]).is_file()
    assert Path(paths["cleaning_summary"]).is_file()
