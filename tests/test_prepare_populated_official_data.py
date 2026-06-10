"""Tests for Step 17F prepare_populated_official_data orchestrator."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pandas as pd

import src.utils.constants as C
from src.official.prepare_populated_official_data import prepare_step17f_populated_official_data


def test_prepare_step17f_needs_more_data_incomplete(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    result = prepare_step17f_populated_official_data()
    assert result["status"] == "needs_more_data"
    assert result["ready_for_apply"] is False
    assert result["applied"] is False
    assert Path(result["summary_path"]).is_file()


def test_prepare_step17f_ready_for_apply_monkeypatched(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)

    complete_metrics = {
        "teams_count": 48,
        "groups_count": 12,
        "group_rows_count": 48,
        "fixtures_count": 104,
        "group_stage_fixtures_count": 72,
        "knockout_fixtures_count": 32,
        "venues_count": 16,
        "players_count": 1248,
        "teams_with_26_players": 48,
        "sample_to_be_verified_count": 0,
        "placeholder_issues_count": 0,
        "missing_required_values_count": 0,
    }

    with patch("src.official.prepare_populated_official_data.build_all_populated_official_data") as build_mock, patch(
        "src.official.prepare_populated_official_data.calculate_population_completeness",
        return_value=(complete_metrics, pd.DataFrame()),
    ), patch(
        "src.official.prepare_populated_official_data.population_is_ready_for_apply",
        return_value=True,
    ), patch(
        "src.official.prepare_populated_official_data.evaluate_official_final_readiness",
        return_value={"is_official_final_ready": False},
    ):
        build_mock.return_value = {"paths": {}}
        result = prepare_step17f_populated_official_data(apply_if_complete=False)
    assert result["status"] == "ready_for_apply"
    assert result["ready_for_apply"] is True
    assert result["applied"] is False


def test_prepare_step17f_does_not_apply_when_incomplete(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    with patch("src.official.prepare_populated_official_data._apply_populated_files") as apply_mock:
        result = prepare_step17f_populated_official_data(apply_if_complete=True)
    apply_mock.assert_not_called()
    assert result["applied"] is False
