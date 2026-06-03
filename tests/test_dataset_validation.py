"""Tests for dataset validators."""

from __future__ import annotations

from src.data.load_data import (
    load_elo_ratings,
    load_fifa_rankings,
    load_historical_results,
    load_wc2026_schedule,
)
from src.data.validate_data import (
    validate_elo_ratings,
    validate_fifa_rankings,
    validate_historical_results,
    validate_wc2026_schedule,
)


def test_validate_historical_results_sample() -> None:
    assert validate_historical_results(load_historical_results()) is True


def test_validate_fifa_rankings_sample() -> None:
    assert validate_fifa_rankings(load_fifa_rankings()) is True


def test_validate_elo_ratings_sample() -> None:
    assert validate_elo_ratings(load_elo_ratings()) is True


def test_validate_wc2026_schedule_sample() -> None:
    assert validate_wc2026_schedule(load_wc2026_schedule()) is True
