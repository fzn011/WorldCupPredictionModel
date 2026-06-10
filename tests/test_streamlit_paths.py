"""Regression tests for Streamlit PROJECT_ROOT bootstrap (Windows-safe)."""

from __future__ import annotations

import ast
import importlib.util
import runpy
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = REPO_ROOT / "app"
STREAMLIT_APP = APP_DIR / "streamlit_app.py"
STREAMLIT_PATHS = APP_DIR / "streamlit_paths.py"


def test_streamlit_paths_defines_project_root_before_official_data_dir() -> None:
    source = STREAMLIT_PATHS.read_text(encoding="utf-8")
    root_idx = source.find("PROJECT_ROOT =")
    official_idx = source.find("OFFICIAL_DATA_DIR =")
    assert root_idx != -1
    assert official_idx != -1
    assert root_idx < official_idx


def test_streamlit_app_imports_paths_from_streamlit_paths_module() -> None:
    source = STREAMLIT_APP.read_text(encoding="utf-8")
    assert "from app.streamlit_paths import" in source or "from streamlit_paths import" in source
    assert "OFFICIAL_DATA_DIR = PROJECT_ROOT" not in source
    assert "PROJECT_ROOT = getattr(C" not in source
    assert "PROJECT_ROOT = Path(__file__)" not in source


def test_streamlit_app_never_uses_project_root_before_path_import() -> None:
    """Regression: OFFICIAL_* = PROJECT_ROOT must not appear before streamlit_paths import."""
    source = STREAMLIT_APP.read_text(encoding="utf-8")
    import_idx = source.find("from app.streamlit_paths import")
    if import_idx == -1:
        import_idx = source.find("from streamlit_paths import")
    assert import_idx != -1, "streamlit_app.py must import streamlit_paths"
    header = source[:import_idx]
    assert "OFFICIAL_DATA_DIR = PROJECT_ROOT" not in header
    assert "OFFICIAL_PROCESSED_DIR = PROJECT_ROOT" not in header
    assert "PROJECT_ROOT = getattr(C" not in header


def test_streamlit_paths_has_filesystem_fallback_before_constants() -> None:
    """Paths must define PROJECT_ROOT from APP_DIR before touching OFFICIAL_* or importing C."""
    source = STREAMLIT_PATHS.read_text(encoding="utf-8")
    root_idx = source.find("PROJECT_ROOT = APP_DIR.parent")
    official_idx = source.find("OFFICIAL_DATA_DIR =")
    constants_idx = source.find("import src.utils.constants as C")
    assert root_idx != -1
    assert official_idx != -1
    assert root_idx < official_idx
    assert root_idx < constants_idx
    assert "except Exception:" in source


def test_streamlit_app_has_no_local_project_root_before_path_import() -> None:
    """Ensure streamlit_app.py never assigns path constants locally (uses streamlit_paths)."""
    tree = ast.parse(STREAMLIT_APP.read_text(encoding="utf-8"))
    import_found = False
    path_assign_lines: list[int] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and "streamlit_paths" in node.module:
            import_found = True
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {
                    "PROJECT_ROOT",
                    "OFFICIAL_DATA_DIR",
                    "OFFICIAL_PROCESSED_DIR",
                    "PROCESSED_DATA_DIR",
                    "REPORTS_DIR",
                }:
                    path_assign_lines.append(node.lineno)

    assert import_found, "streamlit_app.py must import from streamlit_paths"
    assert path_assign_lines == [], f"streamlit_app.py must not assign path constants locally: {path_assign_lines}"


def test_streamlit_paths_module_loads() -> None:
    spec = importlib.util.spec_from_file_location("streamlit_paths_test", STREAMLIT_PATHS)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.PROJECT_ROOT.exists()
    assert module.OFFICIAL_DATA_DIR.exists() or module.OFFICIAL_DATA_DIR.parent.exists()


def test_streamlit_app_module_loads() -> None:
    namespace = runpy.run_path(str(STREAMLIT_APP), run_name="streamlit_app_test")
    assert "PROJECT_ROOT" in namespace
    assert "OFFICIAL_DATA_DIR" in namespace
    assert namespace["PROJECT_ROOT"].exists()


@pytest.mark.parametrize("page_path", sorted((APP_DIR / "pages").glob("*.py")))
def test_streamlit_page_modules_import_without_project_root_name_error(page_path: Path) -> None:
    """Smoke-import each Streamlit page (catches undefined PROJECT_ROOT in pages)."""
    runpy.run_path(str(page_path), run_name=f"page_test_{page_path.stem}")


def test_streamlit_page_url_pathnames_are_unique() -> None:
    """Regression: numbered pages must not share the same Streamlit URL slug."""
    import re

    slugs: dict[str, str] = {}
    for page_path in sorted((APP_DIR / "pages").glob("*.py")):
        slug = re.sub(r"^\d+_", "", page_path.stem)
        if slug in slugs:
            pytest.fail(f"Duplicate Streamlit page slug '{slug}': {slugs[slug]} and {page_path.name}")
        slugs[slug] = page_path.name

