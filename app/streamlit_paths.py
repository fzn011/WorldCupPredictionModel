"""Shared path bootstrap for Streamlit apps (avoids PROJECT_ROOT NameError).

Import path constants from this module only — do not recompute PROJECT_ROOT in pages.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Define repo root immediately (no other project imports yet).
APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import src.utils.constants as C  # noqa: E402

# Prefer constants module when available; fall back to filesystem root above.
PROJECT_ROOT = Path(getattr(C, "PROJECT_ROOT", PROJECT_ROOT))
PROCESSED_DATA_DIR = Path(getattr(C, "PROCESSED_DATA_DIR", PROJECT_ROOT / "data" / "processed"))
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
OFFICIAL_DATA_DIR = PROJECT_ROOT / str(getattr(C, "OFFICIAL_DATA_DIR", "data/official"))
OFFICIAL_PROCESSED_DIR = PROJECT_ROOT / str(getattr(C, "OFFICIAL_PROCESSED_DIR", "data/official/processed"))

__all__ = [
    "APP_DIR",
    "FIGURES_DIR",
    "OFFICIAL_DATA_DIR",
    "OFFICIAL_PROCESSED_DIR",
    "PROCESSED_DATA_DIR",
    "PROJECT_ROOT",
    "REPORTS_DIR",
]
