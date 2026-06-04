"""Tests for Step 14 full tournament single-run simulation."""

from __future__ import annotations

from functools import lru_cache

from src.simulation.full_tournament import run_full_tournament_single


@lru_cache(maxsize=1)
def _run_once() -> dict:
    return run_full_tournament_single(random_seed=42)


def test_run_full_tournament_single_returns_expected_keys() -> None:
    result = _run_once()
    assert {
        "group_result",
        "knockout_result",
        "full_match_log",
        "stage_results",
        "path_report",
        "full_validation_report",
        "summary",
    }.issubset(set(result.keys()))


def test_full_match_log_has_104_matches_for_full_setup() -> None:
    result = _run_once()
    assert len(result["full_match_log"]) == 104


def test_summary_has_podium_fields() -> None:
    result = _run_once()
    summary = result["summary"]
    assert bool(summary.get("champion"))
    assert bool(summary.get("runner_up"))
    assert bool(summary.get("third_place"))


def test_validation_passes_for_real_seed_42_run() -> None:
    result = _run_once()
    assert result["summary"]["validation_passed"] is True
