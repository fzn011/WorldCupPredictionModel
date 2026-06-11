"""Tests for branding helpers (CSS-only, no external logos)."""

from __future__ import annotations

from app.components.branding import render_branded_hero, render_sidebar_brand


def test_branding_exports_callable() -> None:
    assert callable(render_sidebar_brand)
    assert callable(render_branded_hero)
