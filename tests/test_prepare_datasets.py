"""Tests for the Step 2 prepare_datasets pipeline."""

from __future__ import annotations

from pathlib import Path

from src.data.prepare_datasets import prepare_step2_datasets


def test_prepare_step2_returns_dict() -> None:
    summary = prepare_step2_datasets()
    assert isinstance(summary, dict)
    assert summary.get("status") == "ok"


def test_prepare_step2_creates_canonical_file() -> None:
    summary = prepare_step2_datasets()
    path = Path(summary["canonical_matches_path"])
    assert path.is_file()


def test_prepare_step2_summary_has_row_counts() -> None:
    summary = prepare_step2_datasets()
    rows = summary["rows"]
    for key in (
        "historical_results",
        "canonical_matches",
        "fifa_rankings",
        "elo_ratings",
        "wc2026_teams",
        "wc2026_groups",
        "wc2026_schedule",
    ):
        assert key in rows
        assert rows[key] >= 0
