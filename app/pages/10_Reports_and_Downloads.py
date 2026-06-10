"""Streamlit page: Reports & Downloads hub."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
APP_DIR = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

try:
    from app.components.reports_hub import render_reports_hub
    from app.components.ui import inject_page_theme, render_hero
except ModuleNotFoundError:
    from components.reports_hub import render_reports_hub  # type: ignore
    from components.ui import inject_page_theme, render_hero  # type: ignore

st.set_page_config(page_title="Reports & Downloads", layout="wide", initial_sidebar_state="expanded")
inject_page_theme()
render_hero(
    "Reports & Downloads",
    "Central hub for Monte Carlo forecasts, awards analytics, official data summaries, and portfolio files.",
    eyebrow="Exports",
)
render_reports_hub()
