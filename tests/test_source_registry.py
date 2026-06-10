"""Tests for Step 17E official source registry."""

from __future__ import annotations

from src.official.source_registry import (
    create_default_official_source_registry,
    validate_source_url,
)


def test_create_default_official_source_registry_returns_expected_sources():
    reg = create_default_official_source_registry()
    assert "teams" in reg["sources"]
    assert "schedule" in reg["sources"]
    assert "scores_fixtures" in reg["sources"]
    assert "squad_announcements" in reg["sources"]
    assert "fifa.com" in reg["sources"]["teams"]["url"]


def test_validate_source_url_accepts_fifa_domains():
    assert validate_source_url("https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/teams")
    assert validate_source_url("https://fdp.fifa.org/asset/download/example.json")


def test_validate_source_url_rejects_unrelated_domains():
    assert not validate_source_url("https://example.com/data.csv")
    assert not validate_source_url("")
