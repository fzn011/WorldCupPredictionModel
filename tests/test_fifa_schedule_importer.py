"""Tests for Step 17F FIFA schedule importer."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import src.utils.constants as C
from src.official.fifa_schedule_importer import (
    load_fifa_downloadable_schedule,
    normalize_schedule_to_official_schema,
    save_populated_schedule_outputs,
)


def test_normalize_schedule_first_stage_to_group_stage():
    schedule_df = pd.DataFrame(
        [
            {
                "Match Number": 1,
                "Date": "2026-06-11",
                "Time": "13:00",
                "Group": "A",
                "Stage": "First Stage",
                "Stadium": "Test Stadium",
                "City": "Mexico City",
                "Country": "Mexico",
                "Team A": "Mexico",
                "Team B": "South Africa",
            }
        ]
    )
    fixtures_df, venues_df, audit_df = normalize_schedule_to_official_schema(schedule_df)
    assert fixtures_df.iloc[0]["stage"] == "group_stage"
    assert len(venues_df) == 1
    assert not audit_df.empty


def test_load_fifa_downloadable_schedule_csv(tmp_path):
    csv_path = tmp_path / "schedule.csv"
    pd.DataFrame(
        [{"Match Number": 1, "Team A": "France", "Team B": "England", "Date": "2026-06-12"}]
    ).to_csv(csv_path, index=False)
    fixtures_df, venues_df = load_fifa_downloadable_schedule(str(csv_path))
    assert len(fixtures_df) == 1


def test_save_populated_schedule_outputs(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    fixtures_df = pd.DataFrame([{"match_id": "wc2026_m001", "match_number": 1, "stage": "Group Stage", "group": "A", "date": "2026-06-11", "kickoff_local": "", "kickoff_utc": "", "timezone": "", "venue": "Stadium", "stadium": "Stadium", "city": "City", "country": "Country", "team_a": "A", "team_b": "B", "team_a_code": "", "team_b_code": "", "team_a_group_slot": "", "team_b_group_slot": "", "status": "scheduled", "source": "test"}])
    venues_df = pd.DataFrame([{"venue_id": "v_1", "stadium": "Stadium", "venue": "Stadium", "city": "City", "country": "Country", "timezone": "", "capacity": "", "latitude": "", "longitude": "", "source": "test"}])
    audit_df = pd.DataFrame([{"dataset": "fixtures", "source": "test", "status": "parsed", "rows_extracted": 1, "warnings": "", "notes": "", "extracted_at": "2026-01-01"}])
    outputs = save_populated_schedule_outputs(fixtures_df, venues_df, audit_df)
    assert Path(outputs["fixtures_path"]).is_file()
    assert Path(outputs["venues_path"]).is_file()
