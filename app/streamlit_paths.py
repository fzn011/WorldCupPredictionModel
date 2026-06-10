"""Shared path bootstrap for Streamlit apps (avoids PROJECT_ROOT NameError).

Import path constants from this module only — never assign PROJECT_ROOT or
OFFICIAL_* paths in streamlit_app.py or pages before importing from here.

Windows-safe: PROJECT_ROOT is derived from this file's location first, with
no dependency on ``C`` or ``src`` until after the filesystem root exists.
"""

from __future__ import annotations

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 1) Filesystem root FIRST — always valid, even if src.utils.constants fails.
# ---------------------------------------------------------------------------
APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

# Defaults (used if constants import fails or omits values).
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
OFFICIAL_DATA_DIR = PROJECT_ROOT / "data" / "official"
OFFICIAL_PROCESSED_DIR = PROJECT_ROOT / "data" / "official" / "processed"

# ---------------------------------------------------------------------------
# 2) Optional alignment with src.utils.constants (never required for root).
# ---------------------------------------------------------------------------
try:
    import src.utils.constants as C  # noqa: E402

    _c_root = getattr(C, "PROJECT_ROOT", None)
    if _c_root is not None:
        PROJECT_ROOT = Path(_c_root)

    _c_processed = getattr(C, "PROCESSED_DATA_DIR", None)
    if _c_processed is not None:
        PROCESSED_DATA_DIR = Path(_c_processed)

    OFFICIAL_DATA_DIR = PROJECT_ROOT / str(getattr(C, "OFFICIAL_DATA_DIR", "data/official"))
    OFFICIAL_PROCESSED_DIR = PROJECT_ROOT / str(getattr(C, "OFFICIAL_PROCESSED_DIR", "data/official/processed"))
    REPORTS_DIR = PROJECT_ROOT / "reports"
    FIGURES_DIR = REPORTS_DIR / "figures"
except Exception:
    # Keep filesystem defaults above — Streamlit must still start.
    pass

__all__ = [
    "APP_DIR",
    "FIGURES_DIR",
    "OFFICIAL_DATA_DIR",
    "OFFICIAL_PROCESSED_DIR",
    "PROCESSED_DATA_DIR",
    "PROJECT_ROOT",
    "REPORTS_DIR",
]
