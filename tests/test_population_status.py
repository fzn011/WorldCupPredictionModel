"""Tests for population status tracking."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.official.population_status import (
    initialize_population_status,
    load_population_status,
    save_population_status,
    summarize_population_status,
    update_population_step,
)
from src.utils.constants import OFFICIAL_POPULATION_REQUIRED_STEPS


def test_initialize_population_status_returns_required_steps():
    status = initialize_population_status()
    for step in OFFICIAL_POPULATION_REQUIRED_STEPS:
        assert step in status["steps"]
        assert status["steps"][step]["status"] == "not_started"
    assert status["official_final_ready"] is False


def test_update_population_step_works(tmp_path, monkeypatch):
    status_file = tmp_path / "status.json"
    monkeypatch.setattr(
        "src.official.population_status._status_path",
        lambda path=None: status_file if path is None else Path(path),
    )

    updated = update_population_step("fill_teams", "in_progress", notes="started")
    assert updated["steps"]["fill_teams"]["status"] == "in_progress"
    assert updated["steps"]["fill_teams"]["notes"] == "started"


def test_invalid_status_is_rejected():
    with pytest.raises(ValueError, match="Invalid status"):
        update_population_step("fill_teams", "not_a_valid_status")


def test_summarize_population_status_returns_counts():
    status = initialize_population_status()
    summary = summarize_population_status(status)
    assert summary["total_steps"] == len(OFFICIAL_POPULATION_REQUIRED_STEPS)
    assert "overall_status" in summary
    assert "completed_steps" in summary
