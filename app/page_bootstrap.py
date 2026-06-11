"""Shared Streamlit page setup — paths, theme, and hero for every page."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

# Ensure repo root is on sys.path when this module is imported from a page file.
_PB_ROOT = Path(__file__).resolve().parent.parent
_PB_APP = Path(__file__).resolve().parent
for _path in (_PB_ROOT, _PB_APP):
    _entry = str(_path)
    if _entry not in sys.path:
        sys.path.insert(0, _entry)


def safe_sort_dataframe(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Sort only by columns that exist — avoids KeyError on schema drift."""
    cols = [c for c in columns if c in df.columns]
    return df.sort_values(cols) if cols else df


def repo_root_from(caller_file: str | Path) -> Path:
    """Walk up from any page file until repo root (contains src/ + app/)."""
    current = Path(caller_file).resolve().parent
    for _ in range(8):
        if (current / "src").is_dir() and (current / "app").is_dir():
            return current
        current = current.parent
    raise RuntimeError("Could not locate repository root from page file.")


def setup_streamlit_paths(caller_file: str | Path) -> tuple[Path, Path]:
    """Ensure repo root and app/ are on sys.path. Returns (repo_root, app_dir)."""
    root = repo_root_from(caller_file)
    app_dir = root / "app"
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))
    return root, app_dir


def begin_themed_page(
    caller_file: str | Path,
    title: str,
    subtitle: str,
    *,
    eyebrow: str | None = None,
) -> tuple[Path, Path]:
    """Path setup + hero banner. Global theme is injected by streamlit_app.py."""
    root, app_dir = setup_streamlit_paths(caller_file)
    try:
        from app.components.ui import render_hero
    except ModuleNotFoundError:
        from components.ui import render_hero

    render_hero(
        title,
        subtitle,
        eyebrow=eyebrow or "FIFA World Cup 2026 Analytics",
    )
    return root, app_dir
