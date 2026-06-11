"""Tests for branding / logo helpers."""

from __future__ import annotations

from pathlib import Path

from app.components.branding import LOGO_STANDARD, render_branded_hero, render_sidebar_brand, resolve_logo_path


def test_logo_standard_path_under_app_static() -> None:
    assert "static" in str(LOGO_STANDARD)
    assert LOGO_STANDARD.name == "world_cup_logo.png"


def test_resolve_logo_path_returns_none_or_file() -> None:
    path = resolve_logo_path()
    assert path is None or path.is_file()


def test_branding_exports_callable() -> None:
    assert callable(render_sidebar_brand)
    assert callable(render_branded_hero)
