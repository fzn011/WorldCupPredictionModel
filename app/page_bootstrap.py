"""Shared Streamlit page setup — paths, theme, and hero for every page."""

from __future__ import annotations

import sys
from pathlib import Path


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
    """Path setup + inject blood-red theme + hero banner. Call at top of every page."""
    root, app_dir = setup_streamlit_paths(caller_file)
    try:
        from app.components.ui import inject_page_theme, render_hero
    except ModuleNotFoundError:
        from components.ui import inject_page_theme, render_hero

    inject_page_theme()
    render_hero(
        title,
        subtitle,
        eyebrow=eyebrow or "FIFA World Cup 2026 Analytics",
    )
    return root, app_dir
