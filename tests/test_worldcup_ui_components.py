"""Tests for World Cup Streamlit theme and UI component modules."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
THEME_PATH = REPO_ROOT / "app" / "styles" / "worldcup_theme.py"
UI_PATH = REPO_ROOT / "app" / "components" / "ui.py"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_worldcup_theme_colors_palette() -> None:
    theme = _load_module(THEME_PATH, "worldcup_theme_test")
    colors = theme.COLORS
    assert colors["background"] == "#07111F"
    assert colors["card"] == "#0E1B2A"
    assert colors["gold"] == "#D6A84F"
    assert colors["green"] == "#16A36A"
    assert colors["white"] == "#F8FAFC"
    assert colors["muted"] == "#94A3B8"
    assert colors["warning"] == "#F59E0B"
    assert colors["danger"] == "#EF4444"


def test_worldcup_theme_inject_css_contains_key_classes() -> None:
    theme = _load_module(THEME_PATH, "worldcup_theme_css_test")
    # inject_worldcup_css uses streamlit; verify source contains expected selectors.
    source = THEME_PATH.read_text(encoding="utf-8")
    for token in (".wc-hero", ".wc-card", ".wc-badge-ok", ".wc-formation", "inject_worldcup_css"):
        assert token in source


def test_ui_module_exports_render_helpers() -> None:
    source = UI_PATH.read_text(encoding="utf-8")
    for name in (
        "render_hero",
        "render_metric_card",
        "render_status_card",
        "render_section_header",
        "render_pipeline_stepper",
        "render_action_cards",
        "render_download_card",
        "render_warning_panel",
        "render_success_panel",
        "render_podium_cards",
        "render_formation_diagram",
        "inject_page_theme",
    ):
        assert f"def {name}" in source


def test_app_styles_package_exports() -> None:
    from app.styles import COLORS, inject_worldcup_css

    assert COLORS["gold"] == "#D6A84F"
    assert callable(inject_worldcup_css)


def test_app_components_package_exports() -> None:
    from app.components.ui import render_hero, render_metric_card

    assert callable(render_hero)
    assert callable(render_metric_card)


@pytest.mark.parametrize(
    "page_name",
    [
        "1_Match_Predictor.py",
        "2_Tournament_Simulator.py",
        "3_Data_Health_Dashboard.py",
        "9_Monte_Carlo_Simulator.py",
        "10_Reports_and_Downloads.py",
        "17_World_Cup_Awards.py",
    ],
)
def test_themed_pages_reference_inject_page_theme(page_name: str) -> None:
    path = REPO_ROOT / "app" / "pages" / page_name
    assert path.is_file(), f"Missing themed page: {page_name}"
    source = path.read_text(encoding="utf-8")
    assert "inject_page_theme" in source


def test_streamlit_app_uses_reports_hub() -> None:
    source = (REPO_ROOT / "app" / "streamlit_app.py").read_text(encoding="utf-8")
    assert "render_reports_hub" in source
    assert "pages/13_Official_Final_Readiness.py" not in source
