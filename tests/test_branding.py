"""Tests for branding / logo helpers."""

from __future__ import annotations

from pathlib import Path

from app.components.branding import LOGO_STANDARD, resolve_logo_path


def test_logo_standard_path_under_app_static() -> None:
    assert "static" in str(LOGO_STANDARD)
    assert LOGO_STANDARD.name == "world_cup_logo.png"


def test_resolve_logo_path_returns_none_when_missing() -> None:
    # Repo may not ship the user's PNG; function must not crash.
    path = resolve_logo_path()
    assert path is None or path.is_file()
