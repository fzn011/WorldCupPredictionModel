"""Tests for the Step 4 preparation pipeline."""

from __future__ import annotations

from pathlib import Path

from src.features.prepare_features import prepare_step4_features


def test_prepare_step4_features_returns_summary_dict() -> None:
    summary = prepare_step4_features(min_year=1990)
    assert isinstance(summary, dict)
    assert summary["status"] in {"ok", "empty"}
    assert summary["feature_rows"] >= 0


def test_prepare_step4_features_writes_outputs() -> None:
    summary = prepare_step4_features(min_year=1990)
    assert Path(summary["feature_output_path"]).is_file()
    assert Path(summary["feature_quality_report_path"]).is_file()
    assert Path(summary["feature_summary_path"]).is_file()


def test_prepare_step4_features_has_rows() -> None:
    summary = prepare_step4_features(min_year=1990)
    assert summary["feature_rows"] > 0
