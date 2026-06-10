"""Tests for Step 17H blocker cleanup."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

import src.utils.constants as C
from src.official.blocker_cleanup import (
    analyze_apply_blockers,
    apply_safe_blocker_cleanups,
    save_blocker_cleanup_report,
)


def test_analyze_apply_blockers_returns_categories(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    pop = tmp_path / C.OFFICIAL_POPULATED_DATA_DIR
    pop.mkdir(parents=True)
    pd.DataFrame({"stage": ["First Stage"], "source": ["fifa_downloadable_schedule"]}).to_csv(
        pop / C.POPULATED_OFFICIAL_FIXTURES_FILE, index=False
    )
    summary, report_df = analyze_apply_blockers()
    assert "metrics_before" in summary
    assert "category" in report_df.columns


def test_apply_safe_blocker_cleanups_does_not_promote_official_final(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    pop = tmp_path / C.OFFICIAL_POPULATED_DATA_DIR
    rep = tmp_path / C.OFFICIAL_POPULATED_REPORTS_DIR
    pop.mkdir(parents=True)
    rep.mkdir(parents=True)

    fixtures = pd.DataFrame(
        [
            {
                "match_id": f"wc2026_m{i:03d}",
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
                "team_a": "Mexico",
                "team_b": "Brazil",
                "team_a_code": "",
                "team_b_code": "",
                "team_a_group_slot": "",
                "team_b_group_slot": "",
                "status": "scheduled",
                "source": "fifa_downloadable_schedule",
            }
            for i in range(1, 105)
        ]
    )
    fixtures.to_csv(pop / C.POPULATED_OFFICIAL_FIXTURES_FILE, index=False)

    result = apply_safe_blocker_cleanups()
    assert result.get("official_final_enabled") is False
    assert "metrics_after" in result


def test_cleanup_report_writes_file(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    rep = tmp_path / C.OFFICIAL_POPULATED_REPORTS_DIR
    rep.mkdir(parents=True)
    df = pd.DataFrame([{"category": "stage_normalization", "blocking": True, "issue": "test", "suggested_fix": "fix"}])
    path = save_blocker_cleanup_report(df)
    assert Path(path).is_file()
