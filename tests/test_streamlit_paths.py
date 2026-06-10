"""Smoke tests for Streamlit path bootstrap."""

from __future__ import annotations

import runpy
from pathlib import Path


def test_streamlit_app_defines_project_root_before_official_paths() -> None:
    """Regression: OFFICIAL_DATA_DIR must not reference undefined PROJECT_ROOT."""
    app_path = Path(__file__).resolve().parents[1] / "app" / "streamlit_app.py"
    source = app_path.read_text(encoding="utf-8")
    project_root_idx = source.find("PROJECT_ROOT =")
    official_idx = source.find("OFFICIAL_TEAMS_FILE")
    assert project_root_idx != -1
    assert official_idx != -1
    assert project_root_idx < official_idx


def test_streamlit_app_module_loads() -> None:
    app_path = Path(__file__).resolve().parents[1] / "app" / "streamlit_app.py"
    namespace = runpy.run_path(str(app_path), run_name="streamlit_app_test")
    assert "PROJECT_ROOT" in namespace
    assert "OFFICIAL_DATA_DIR" in namespace
    assert namespace["PROJECT_ROOT"].exists()
