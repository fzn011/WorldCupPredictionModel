"""Tests for Step 7 ranking feature preparation pipeline."""

from __future__ import annotations

from pathlib import Path

from src.features.prepare_ranking_features import prepare_step7_ranking_features


def test_prepare_step7_ranking_features_outputs_exist() -> None:
    summary = prepare_step7_ranking_features()
    assert summary["status"] in {"ok", "empty"}
    assert Path(summary["output_path"]).is_file()
    assert Path(summary["team_strength_snapshot_path"]).is_file()
    assert Path(summary["ranking_merge_report_path"]).is_file()
