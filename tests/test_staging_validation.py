"""Tests for Step 17E staging validation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import src.utils.constants as C
from src.official.staging_validation import (
    save_staging_validation_report,
    validate_all_staged_data,
)


def test_validate_all_staged_data_returns_report(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    staging = tmp_path / C.OFFICIAL_SOURCE_STAGING_DIR
    staging.mkdir(parents=True, exist_ok=True)

    passed, report = validate_all_staged_data()
    assert passed is False
    assert not report.empty


def test_save_staging_validation_report_writes_file(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    report = pd.DataFrame([{"check": "test", "passed": True}])
    path = save_staging_validation_report(report)
    assert Path(path).is_file()
