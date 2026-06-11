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


def test_navigate_to_syncs_sidebar_radio_key() -> None:
    from app.components.layout import _NAV_RADIO_KEY, _SESSION_ACTIVE, _set_active_page

    class _State(dict):
        def __getattr__(self, key):
            return self[key]

        def __setattr__(self, key, value):
            self[key] = value

    fake_state = _State(
        {
            _SESSION_ACTIVE: "Home",
            "show_advanced_tools": False,
            _NAV_RADIO_KEY: "Home",
        }
    )
    import app.components.layout as layout

    layout.st.session_state = fake_state
    _set_active_page("Match Predictor")
    assert fake_state[_SESSION_ACTIVE] == "Match Predictor"
    assert fake_state[_NAV_RADIO_KEY] == "Match Predictor"


def test_theme_inject_helper_imports() -> None:
    from app.styles.worldcup_theme import inject_worldcup_css

    assert callable(inject_worldcup_css)
