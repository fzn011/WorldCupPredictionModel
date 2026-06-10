"""Tests for Step 17E manual file ingestion."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import src.utils.constants as C
from src.official.manual_file_ingestion import ingest_manual_official_file


def test_ingest_manual_official_file_stages_csv(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    staging = tmp_path / C.OFFICIAL_SOURCE_STAGING_DIR
    staging.mkdir(parents=True, exist_ok=True)

    src = tmp_path / "teams.csv"
    df = pd.DataFrame(
        {
            "team": ["Mexico"],
            "team_code": ["MEX"],
            "confederation": ["CONCACAF"],
            "group": ["A"],
            "group_slot": [1],
            "is_host": [1],
            "qualified": [1],
            "source": ["manual_test"],
        }
    )
    df.to_csv(src, index=False)

    result = ingest_manual_official_file(str(src), "teams")
    assert result["success"] is True
    assert Path(result["staged_path"]).is_file()
