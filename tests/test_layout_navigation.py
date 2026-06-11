"""Tests for stable sidebar navigation layout."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_layout_main_pages_default_only() -> None:
    from app.components.layout import ADMIN_PAGES, MAIN_PAGES

    assert "Home" in MAIN_PAGES
    assert "Match Predictor" in MAIN_PAGES
    assert "Tournament Forecast" in MAIN_PAGES
    assert "Quick Simulation" in ADMIN_PAGES
    assert "Monte Carlo Forecast" not in MAIN_PAGES


def test_layout_page_files_use_views_directory() -> None:
    from app.components.layout import PAGE_FILES

    for rel in PAGE_FILES.values():
        assert rel.startswith("views/"), rel


def test_theme_inject_helper_imports() -> None:
    from app.styles.worldcup_theme import inject_worldcup_css

    assert callable(inject_worldcup_css)
