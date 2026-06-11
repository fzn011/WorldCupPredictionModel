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
    assert colors["background"] == "#050505"
    assert colors["primary"] == "#8B0000"
    assert colors["gold"] == "#8B0000"
    assert colors["green"] == "#16A36A"
    assert colors["white"] == "#F8F8F8"
    assert colors["muted"] == "#C7C7C7"
    assert colors["input_bg"] == "#161616"
    assert colors["warning"] == "#F59E0B"
    assert colors["danger"] == "#EF4444"


def test_worldcup_theme_no_legacy_gold_or_navy() -> None:
    source = THEME_PATH.read_text(encoding="utf-8")
    for forbidden in ("#0f2844", "214,168,79", "#b5832a", "rgba(14,27,42"):
        assert forbidden not in source, f"Legacy color still in theme: {forbidden}"


def test_worldcup_theme_inject_css_contains_key_classes() -> None:
    source = THEME_PATH.read_text(encoding="utf-8")
    for token in (
        ".wc-hero",
        ".wc-card",
        ".wc-badge-ok",
        ".wc-brand-hero",
        ".wc-sidebar-brand",
        ".wc-nav-tile",
        ".wc-formation",
        "inject_worldcup_css",
        "st.html",
        ".stTextInput input",
        "#8B0000",
        "#161616",
        '[data-baseweb="select"]',
        "Sprintura",
        "html[data-theme=\"light\"]",
        "stHeader",
    ):
        assert token in source


def test_ui_module_exports_render_helpers() -> None:
    source = UI_PATH.read_text(encoding="utf-8")
    for name in (
        "render_hero",
        "render_metric_card",
        "render_status_card",
        "render_section_header",
        "render_pipeline_stepper",
        "render_download_card",
        "render_warning_panel",
        "render_success_panel",
        "render_info_panel",
        "render_error_panel",
        "render_podium_cards",
        "render_formation_diagram",
        "render_progress_bar",
        "render_readiness_item",
        "render_champion_spotlight",
        "render_quick_nav_grid",
        "render_action_grid",
        "render_action_card",
        "render_page_header",
        "render_empty_state",
        "render_clean_table",
        "inject_global_theme",
        "inject_page_theme",
        ):
        assert f"def {name}" in source or f"{name} = inject_page_theme" in source


def test_app_styles_package_exports() -> None:
    from app.styles import COLORS, inject_worldcup_css

    assert COLORS["primary"] == "#8B0000"
    assert callable(inject_worldcup_css)


def test_app_components_package_exports() -> None:
    from app.components.ui import render_hero, render_metric_card

    assert callable(render_hero)
    assert callable(render_metric_card)


@pytest.mark.parametrize(
    "page_path",
    [
        "app/pages/1_Match_Predictor.py",
        "app/pages/2_Tournament_Simulator.py",
        "app/pages/3_Data_Health.py",
        "app/pages/4_Reports_Downloads.py",
        "app/pages/9_Monte_Carlo_Simulator.py",
        "app/pages/17_World_Cup_Awards.py",
        "app/pages/_dev/4_Model_Explanation.py",
        "app/pages/_dev/5_Tournament_Setup.py",
        "app/pages/_dev/6_Group_Stage_Simulation.py",
        "app/pages/_dev/7_Knockout_Simulation.py",
        "app/pages/_dev/8_Full_Tournament_Run.py",
        "app/pages/_dev/11_Official_Data_Health.py",
        "app/pages/_dev/12_Official_Squads_Health.py",
        "app/pages/_dev/14_Official_Data_Population.py",
        "app/pages/_dev/15_Source_Assisted_Population.py",
        "app/pages/_dev/16_Official_Data_Population_Completion.py",
    ],
)
def test_all_streamlit_pages_apply_theme(page_path: str) -> None:
    path = REPO_ROOT / page_path
    assert path.is_file(), f"Missing page: {page_path}"
    source = path.read_text(encoding="utf-8")
    assert "inject_page_theme" in source or "begin_themed_page" in source


@pytest.mark.parametrize(
    "page_name",
    [
        "1_Match_Predictor.py",
        "2_Tournament_Simulator.py",
        "3_Data_Health.py",
        "4_Reports_Downloads.py",
        "9_Monte_Carlo_Simulator.py",
        "17_World_Cup_Awards.py",
    ],
)
def test_themed_pages_reference_inject_page_theme(page_name: str) -> None:
    path = REPO_ROOT / "app" / "pages" / page_name
    assert path.is_file(), f"Missing themed page: {page_name}"
    source = path.read_text(encoding="utf-8")
    assert "inject_page_theme" in source


def test_streamlit_app_uses_navigation() -> None:
    source = (REPO_ROOT / "app" / "streamlit_app.py").read_text(encoding="utf-8")
    assert "st.navigation" in source
    assert "pages/3_Data_Health.py" in source
    assert "Show technical tools" in source
    assert "pages/_dev/" in source
