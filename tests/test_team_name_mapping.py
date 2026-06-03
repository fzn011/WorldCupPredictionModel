"""Tests for team-name standardization and slugify helpers."""

from __future__ import annotations

import math

from src.utils.team_name_mapping import (
    slugify_team_name,
    standardize_team_name,
)


def test_standardize_team_name_basic_aliases() -> None:
    assert standardize_team_name("USA") == "United States"
    assert standardize_team_name("Korea Republic") == "South Korea"
    assert standardize_team_name("IR Iran") == "Iran"
    assert standardize_team_name("Czech Republic") == "Czechia"
    assert standardize_team_name("Ivory Coast") == "Côte d'Ivoire"


def test_standardize_team_name_handles_none() -> None:
    assert standardize_team_name(None) == ""
    assert standardize_team_name(float("nan")) == ""
    assert standardize_team_name("   ") == ""
    assert standardize_team_name("  Brazil  ") == "Brazil"


def test_slugify_team_name() -> None:
    assert slugify_team_name("United States") == "united-states"
    assert slugify_team_name("South Korea") == "south-korea"
    assert slugify_team_name("Côte d'Ivoire") == "cote-divoire"
    assert slugify_team_name(None) == ""
