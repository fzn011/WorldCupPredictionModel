"""Streamlit page: Tournament Simulator."""

from __future__ import annotations

import json
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
    from app.components.ui import (
        inject_page_theme,
        load_json_if_exists,
        render_hero,
        render_metric_card,
        render_section_header,
        render_warning_panel,
    )
    from app.streamlit_paths import PROCESSED_DATA_DIR, REPORTS_DIR
except ModuleNotFoundError:
    from components.ui import inject_page_theme, load_json_if_exists, render_hero, render_metric_card, render_section_header, render_warning_panel  # type: ignore
    from streamlit_paths import PROCESSED_DATA_DIR, REPORTS_DIR  # type: ignore

from src.simulation.simulate_tournament import simulate_tournament  # noqa: E402
import src.utils.constants as C  # noqa: E402

FIGURES_DIR = REPORTS_DIR / "figures"
CHART_FILE = getattr(C, "MONTE_CARLO_CHAMPION_CHART_FILE", "monte_carlo_champion_probabilities.png")
SUMMARY_FILE = getattr(C, "MONTE_CARLO_SUMMARY_FILE", "monte_carlo_summary.json")
CHAMPION_CSV = getattr(C, "MONTE_CARLO_CHAMPION_PROBABILITIES_FILE", "monte_carlo_champion_probabilities.csv")

st.set_page_config(page_title="Tournament Simulator", layout="wide", initial_sidebar_state="expanded")
inject_page_theme()
render_hero(
    "Tournament Simulator",
    "Quick champion probability estimates. For full bracket progression and stage heatmaps, use the Monte Carlo Simulator.",
    eyebrow="Tournament outlook",
)

tab_quick, tab_monte_carlo = st.tabs(["Quick simulation", "Monte Carlo results"])

with tab_quick:
    render_section_header("Simulation settings")
    num_simulations = st.number_input(
        "Number of simulations",
        min_value=100,
        max_value=100_000,
        value=10_000,
        step=100,
    )

    if st.button("Run simulation", type="primary"):
        probs = simulate_tournament(num_simulations=int(num_simulations))
        df = (
            pd.DataFrame([{"team": t, "champion_probability": p} for t, p in probs.items()])
            .sort_values("champion_probability", ascending=False)
            .reset_index(drop=True)
        )
        render_section_header("Champion probabilities")
        top3 = df.head(3)
        c1, c2, c3 = st.columns(3)
        for col, (_, row) in zip((c1, c2, c3), top3.iterrows()):
            with col:
                render_metric_card(
                    str(row["team"]),
                    f"{float(row['champion_probability']):.1%}",
                    sub="Quick estimate",
                )
        st.dataframe(df.head(20), use_container_width=True, hide_index=True)

with tab_monte_carlo:
    mc_summary = load_json_if_exists(PROCESSED_DATA_DIR / SUMMARY_FILE)
    champion_df = pd.read_csv(PROCESSED_DATA_DIR / CHAMPION_CSV) if (PROCESSED_DATA_DIR / CHAMPION_CSV).is_file() else pd.DataFrame()
    chart_path = FIGURES_DIR / CHART_FILE

    if champion_df.empty and not mc_summary:
        render_warning_panel(
            "No Monte Carlo outputs yet. Open the Monte Carlo Simulator page to run a full tournament simulation."
        )
        st.page_link("pages/9_Monte_Carlo_Simulator.py", label="Open Monte Carlo Simulator")
    else:
        render_section_header("Top predicted champions")
        if not champion_df.empty:
            prob_col = "champion_probability" if "champion_probability" in champion_df.columns else champion_df.columns[-1]
            team_col = "team" if "team" in champion_df.columns else champion_df.columns[0]
            top = champion_df.sort_values(prob_col, ascending=False).head(3)
            c1, c2, c3 = st.columns(3)
            for col, (_, row) in zip((c1, c2, c3), top.iterrows()):
                with col:
                    render_metric_card(str(row[team_col]), f"{float(row[prob_col]):.1%}", sub="Monte Carlo")
            st.dataframe(champion_df.head(15), use_container_width=True, hide_index=True)
        if chart_path.is_file():
            render_section_header("Champion probability chart")
            st.image(str(chart_path), use_container_width=True)
        if mc_summary:
            render_metric_card(
                "Simulation count",
                str(mc_summary.get("simulation_count", "—")),
                sub=f"Top champion: {mc_summary.get('top_champion', '—')}",
            )
