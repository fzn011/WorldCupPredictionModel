"""Tests for Step 17F population completeness."""

from __future__ import annotations

import pandas as pd

import src.utils.constants as C
from src.official.population_completeness import (
    calculate_population_completeness,
    population_is_ready_for_apply,
)


def test_calculate_population_completeness_detects_incomplete(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    pop = tmp_path / C.OFFICIAL_POPULATED_DATA_DIR
    pop.mkdir(parents=True)
    metrics, report_df = calculate_population_completeness()
    assert metrics["teams_count"] == 0
    assert not report_df.empty
    assert population_is_ready_for_apply(metrics) is False


def test_population_is_ready_for_apply_true_for_complete_metrics():
    metrics = {
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
        "blocking_placeholder_count": 0,
        "optional_metadata_warning_count": 100,
        "placeholder_issues_count": 0,
        "missing_required_values_count": 0,
    }
    assert population_is_ready_for_apply(metrics) is True


def test_first_stage_counts_as_group_stage(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    pop = tmp_path / C.OFFICIAL_POPULATED_DATA_DIR
    pop.mkdir(parents=True)
    rows = []
    for i in range(1, 73):
        rows.append(
            {
                "match_id": f"m{i}",
                "match_number": i,
                "stage": "First Stage",
                "group": "A",
                "date": "2026-06-11",
                "kickoff_local": "13:00",
                "kickoff_utc": "",
                "timezone": "",
                "venue": "Stadium",
                "stadium": "Stadium",
                "city": "City",
                "country": "USA",
                "team_a": "A",
                "team_b": "B",
                "team_a_code": "",
                "team_b_code": "",
                "team_a_group_slot": "",
                "team_b_group_slot": "",
                "status": "scheduled",
                "source": "fifa_schedule_api",
            }
        )
    pd.DataFrame(rows).to_csv(pop / C.POPULATED_OFFICIAL_FIXTURES_FILE, index=False)
    metrics, _ = calculate_population_completeness()
    assert metrics["group_stage_fixtures_count"] == 72
