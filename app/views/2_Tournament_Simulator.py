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
    from app.components.ui import inject_page_theme, render_hero, render_metric_card, render_section_header, render_info_panel
except ModuleNotFoundError:
    from components.ui import inject_page_theme, render_hero, render_metric_card, render_section_header, render_info_panel

from src.simulation.simulate_tournament import simulate_tournament  # noqa: E402

def render_page() -> None:
    render_hero(
        "Quick Simulation",
        "Lightweight bracket simulation for fast exploration. "
        "For full probabilistic forecasts with charts and reports, open Tournament Forecast in the sidebar.",
        eyebrow="Quick simulation",
    )
    render_info_panel(
        "This page runs a lightweight simulation for rapid exploration. "
        "Use **Tournament Forecast** in the sidebar for production-grade Monte Carlo estimates."
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
        top3 = df.head(3)
        if not top3.empty:
            t1, t2, t3 = st.columns(3)
            for col, (_, row) in zip((t1, t2, t3), top3.iterrows(), strict=False):
                with col:
                    render_metric_card(
                        str(row["team"]),
                        f"{float(row['champion_probability']):.1%}",
                        sub="Champion probability",
                        variant="accent",
                    )
        st.dataframe(df, use_container_width=True, hide_index=True)
