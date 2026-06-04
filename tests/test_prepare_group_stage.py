"""Tests for Step 12 group-stage preparation orchestrator."""

from __future__ import annotations

from pathlib import Path

from src.simulation.prepare_group_stage import prepare_step12_group_stage_simulation


def test_prepare_step12_group_stage_simulation_returns_status_ok() -> None:
    summary = prepare_step12_group_stage_simulation(random_seed=42)
    assert summary["status"] == "ok"


def test_prepare_step12_group_stage_simulation_output_files_exist() -> None:
    summary = prepare_step12_group_stage_simulation(random_seed=42)
    assert Path(summary["group_stage_simulated_matches_path"]).is_file()
    assert Path(summary["group_stage_tables_path"]).is_file()
    assert Path(summary["group_stage_rankings_path"]).is_file()


def test_prepare_step12_group_stage_simulation_qualifiers_file_has_32_rows() -> None:
    summary = prepare_step12_group_stage_simulation(random_seed=42)
    qualifiers_path = Path(summary["round_of_32_qualifiers_path"])
    assert qualifiers_path.is_file()
    import pandas as pd

    qualifiers_df = pd.read_csv(qualifiers_path)
    assert len(qualifiers_df) == 32


def test_prepare_step12_group_stage_simulation_validation_report_exists() -> None:
    summary = prepare_step12_group_stage_simulation(random_seed=42)
    assert Path(summary["group_stage_simulation_validation_report_path"]).is_file()
