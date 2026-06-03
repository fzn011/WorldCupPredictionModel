"""Tests for the DATA_SOURCES registry."""

from __future__ import annotations

from src.data.data_sources import DATA_SOURCES

EXPECTED_KEYS = {
    "historical_results",
    "fifa_rankings",
    "elo_ratings",
    "wc2026_teams",
    "wc2026_groups",
    "wc2026_schedule",
}


def test_data_sources_has_expected_keys() -> None:
    assert EXPECTED_KEYS.issubset(set(DATA_SOURCES))


def test_each_source_has_required_columns() -> None:
    for key, cfg in DATA_SOURCES.items():
        assert cfg.required_columns, f"{key} has no required_columns"
        assert isinstance(cfg.required_columns, list)


def test_each_sample_path_exists() -> None:
    for key, cfg in DATA_SOURCES.items():
        assert cfg.sample_path.is_file(), (
            f"Missing sample file for '{key}': {cfg.sample_path}"
        )
