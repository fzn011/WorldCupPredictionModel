"""Tests for Step 14 full tournament preparation orchestrator."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

from src.simulation.prepare_full_tournament import prepare_step14_full_tournament_single_run


@lru_cache(maxsize=1)
def _prepare_once() -> dict:
    return prepare_step14_full_tournament_single_run(random_seed=42)


def test_prepare_step14_full_tournament_single_run_returns_status_ok() -> None:
    summary = _prepare_once()
    assert summary["status"] == "ok"


def test_prepare_step14_full_tournament_outputs_exist() -> None:
    summary = _prepare_once()
    assert Path(summary["full_tournament_matches_path"]).is_file()
    assert Path(summary["full_tournament_group_tables_path"]).is_file()
    assert Path(summary["full_tournament_knockout_matches_path"]).is_file()
    assert Path(summary["full_tournament_path_report_path"]).is_file()
    assert Path(summary["full_tournament_result_path"]).is_file()
    assert Path(summary["validation_report_path"]).is_file()


def test_prepare_step14_full_tournament_validation_report_exists() -> None:
    summary = _prepare_once()
    report_path = Path(summary["validation_report_path"])
    assert report_path.is_file()
    report_df = pd.read_csv(report_path)
    assert not report_df.empty


def test_prepare_step14_full_tournament_match_log_has_104_rows() -> None:
    summary = _prepare_once()
    full_match_log_path = Path(summary["full_tournament_matches_path"])
    df = pd.read_csv(full_match_log_path)
    assert len(df) == 104
