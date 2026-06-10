"""Shared path bootstrap for Streamlit apps (avoids PROJECT_ROOT NameError)."""

from __future__ import annotations

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import src.utils.constants as C  # noqa: E402

PROJECT_ROOT = Path(getattr(C, "PROJECT_ROOT", ROOT))
PROCESSED_DATA_DIR = Path(getattr(C, "PROCESSED_DATA_DIR", PROJECT_ROOT / "data" / "processed"))
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
OFFICIAL_DATA_DIR = PROJECT_ROOT / str(getattr(C, "OFFICIAL_DATA_DIR", "data/official"))
OFFICIAL_PROCESSED_DIR = PROJECT_ROOT / str(getattr(C, "OFFICIAL_PROCESSED_DIR", "data/official/processed"))
