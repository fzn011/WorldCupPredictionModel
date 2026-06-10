"""Streamlit page: Tournament Simulator (placeholder)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
APP_DIR = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

try:
    from app.components.ui import inject_page_theme, render_hero, render_section_header, render_warning_panel
except ModuleNotFoundError:
    from components.ui import inject_page_theme, render_hero, render_section_header, render_warning_panel

from src.simulation.simulate_tournament import simulate_tournament  # noqa: E402

st.set_page_config(page_title="Tournament Simulator", layout="wide", initial_sidebar_state="expanded")
inject_page_theme()
render_hero(
    "Tournament Simulator",
    "Quick champion probability estimates from the legacy placeholder simulator. "
    "For full World Cup Monte Carlo forecasts, use the Monte Carlo Simulator page.",
    eyebrow="Legacy placeholder",
)
render_warning_panel(
    "This page runs a lightweight placeholder simulation. Production demo flow uses "
    "<strong>Monte Carlo Simulator</strong> (sidebar) for official bracket progression."
)

render_section_header("Simulation settings")
num_simulations = st.number_input(
    "Number of simulations",
    min_value=100,
    max_value=100_000,
    value=10_000,
    step=100,
)

if st.button("Run Simulation", type="primary"):
    probs = simulate_tournament(num_simulations=int(num_simulations))
    df = (
        pd.DataFrame([{"team": t, "champion_probability": p} for t, p in probs.items()])
        .sort_values("champion_probability", ascending=False)
        .reset_index(drop=True)
    )
    render_section_header("Champion probabilities")
    st.dataframe(df, use_container_width=True, hide_index=True)
