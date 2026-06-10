"""Streamlit page: Monte Carlo tournament simulator dashboard."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
_APP_DIR = Path(__file__).resolve().parents[1]
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

try:
    from app.streamlit_paths import PROCESSED_DATA_DIR, PROJECT_ROOT, REPORTS_DIR  # noqa: E402
except ModuleNotFoundError:
    from streamlit_paths import PROCESSED_DATA_DIR, PROJECT_ROOT, REPORTS_DIR  # noqa: E402

try:
    from app.components.ui import (  # noqa: E402
        inject_page_theme,
        render_download_card,
        render_hero,
        render_info_panel,
        render_metric_card,
        render_section_header,
    )
except ModuleNotFoundError:
    from components.ui import inject_page_theme, render_download_card, render_hero, render_info_panel, render_metric_card, render_section_header  # noqa: E402

from src.simulation.prepare_monte_carlo import prepare_step15_monte_carlo_simulation  # noqa: E402
from src.reports.monte_carlo_report import (  # noqa: E402
    create_champion_probability_table,
    create_monte_carlo_insight_text,
    create_stage_probability_table,
    create_summary_cards,
    load_monte_carlo_outputs,
)
from src.reports.prepare_monte_carlo_report import prepare_step16_monte_carlo_report  # noqa: E402
import src.utils.constants as C  # noqa: E402

FIGURES_DIR = REPORTS_DIR / "figures"
MONTE_CARLO_SIMULATION_RESULTS_FILE = getattr(C, "MONTE_CARLO_SIMULATION_RESULTS_FILE", "monte_carlo_simulation_results.csv")
MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE = getattr(C, "MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE", "monte_carlo_team_stage_probabilities.csv")
MONTE_CARLO_CHAMPION_PROBABILITIES_FILE = getattr(C, "MONTE_CARLO_CHAMPION_PROBABILITIES_FILE", "monte_carlo_champion_probabilities.csv")
MONTE_CARLO_FINALISTS_FILE = getattr(C, "MONTE_CARLO_FINALISTS_FILE", "monte_carlo_finalists.csv")
MONTE_CARLO_SEMIFINALISTS_FILE = getattr(C, "MONTE_CARLO_SEMIFINALISTS_FILE", "monte_carlo_semifinalists.csv")
MONTE_CARLO_SUMMARY_FILE = getattr(C, "MONTE_CARLO_SUMMARY_FILE", "monte_carlo_summary.json")
MONTE_CARLO_VALIDATION_REPORT_FILE = getattr(C, "MONTE_CARLO_VALIDATION_REPORT_FILE", "monte_carlo_validation_report.csv")
MONTE_CARLO_REPORT_MD_FILE = getattr(C, "MONTE_CARLO_REPORT_MD_FILE", "monte_carlo_report.md")
MONTE_CARLO_CHAMPION_CHART_FILE = getattr(C, "MONTE_CARLO_CHAMPION_CHART_FILE", "monte_carlo_champion_probabilities.png")
MONTE_CARLO_STAGE_HEATMAP_FILE = getattr(C, "MONTE_CARLO_STAGE_HEATMAP_FILE", "monte_carlo_stage_heatmap.png")
DEFAULT_MONTE_CARLO_SIMULATIONS = int(getattr(C, "DEFAULT_MONTE_CARLO_SIMULATIONS", 100))
DEFAULT_MONTE_CARLO_SEED = int(getattr(C, "DEFAULT_MONTE_CARLO_SEED", 42))


def _load_csv(file_name: str) -> pd.DataFrame:
    path = PROCESSED_DATA_DIR / file_name
    if not path.is_file():
        return pd.DataFrame()
    return pd.read_csv(path)


def _load_json(file_name: str) -> dict:
    path = PROCESSED_DATA_DIR / file_name
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


st.set_page_config(page_title="Monte Carlo Simulator", layout="wide", initial_sidebar_state="expanded")
inject_page_theme()
render_hero(
    "Monte Carlo Forecast",
    "Repeated full-tournament simulations to estimate champion and stage progression probabilities.",
    eyebrow="Monte Carlo simulation",
)

tab_overview, tab_results, tab_downloads = st.tabs(["Overview & settings", "Results & charts", "Downloads"])

report_md_path = REPORTS_DIR / MONTE_CARLO_REPORT_MD_FILE
champion_chart_path = FIGURES_DIR / MONTE_CARLO_CHAMPION_CHART_FILE
stage_heatmap_path = FIGURES_DIR / MONTE_CARLO_STAGE_HEATMAP_FILE

summary = _load_json(MONTE_CARLO_SUMMARY_FILE)
champion_prob_df = _load_csv(MONTE_CARLO_CHAMPION_PROBABILITIES_FILE)
stage_prob_df = _load_csv(MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE)
finalists_df = _load_csv(MONTE_CARLO_FINALISTS_FILE)
semifinalists_df = _load_csv(MONTE_CARLO_SEMIFINALISTS_FILE)
validation_df = _load_csv(MONTE_CARLO_VALIDATION_REPORT_FILE)
simulation_results_df = _load_csv(MONTE_CARLO_SIMULATION_RESULTS_FILE)

outputs: dict | None = None
summary_cards_df = pd.DataFrame()
champion_display_df = champion_prob_df.copy()
stage_display_df = stage_prob_df.copy()
insights: list[str] = []
try:
    outputs = load_monte_carlo_outputs()
    summary_cards_df = create_summary_cards(outputs)
    champion_display_df = create_champion_probability_table(outputs)
    stage_display_df = create_stage_probability_table(outputs)
    insights = create_monte_carlo_insight_text(outputs)
except FileNotFoundError:
    outputs = None

with tab_overview:
    render_section_header("Simulation settings")
    simulations = int(
        st.number_input(
            "Number of simulations",
            min_value=1,
            max_value=1000,
            value=DEFAULT_MONTE_CARLO_SIMULATIONS,
            step=1,
        )
    )
    seed = int(st.number_input("Base seed", min_value=0, max_value=1_000_000, value=DEFAULT_MONTE_CARLO_SEED, step=1))
    controls_col1, controls_col2 = st.columns(2)
    if controls_col1.button("Run Monte Carlo simulation", type="primary"):
        run_summary = prepare_step15_monte_carlo_simulation(num_simulations=simulations, base_seed=seed)
        if run_summary.get("validation_passed"):
            st.success("Monte Carlo simulation completed and validated.")
        else:
            st.warning("Monte Carlo simulation completed with validation issues.")
        with st.expander("Run details"):
            st.json(run_summary)
    if controls_col2.button("Generate report", type="secondary"):
        try:
            report_summary = prepare_step16_monte_carlo_report()
            st.success("Monte Carlo report artifacts generated successfully.")
            with st.expander("Report summary"):
                st.json(report_summary)
        except FileNotFoundError as exc:
            st.warning(str(exc))
    st.caption("Outputs are simulation estimates, not certainties.")

with tab_results:
    if not champion_display_df.empty:
        render_section_header("Top predicted champions")
        prob_col = "champion_probability" if "champion_probability" in champion_display_df.columns else champion_display_df.columns[-1]
        team_col = "team" if "team" in champion_display_df.columns else champion_display_df.columns[0]
        top3 = champion_display_df.sort_values(prob_col, ascending=False).head(3)
        t1, t2, t3 = st.columns(3)
        for col, (_, row) in zip((t1, t2, t3), top3.iterrows()):
            with col:
                render_metric_card(str(row[team_col]), f"{float(row[prob_col]):.1%}", sub="Champion probability", accent_value=True)

    render_section_header("Simulation summary")
    if summary:
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("Total simulations", summary.get("num_simulations", 0))
        col2.metric("Successful", summary.get("successful_simulations", 0))
        col3.metric("Failed", summary.get("failed_simulations", 0))
        col4.metric("Top champion", summary.get("top_champion", "—"))
        col5.metric("Top champion probability", f"{float(summary.get('top_champion_probability', 0.0)):.2%}")
        col6.metric("Validation", "passed" if summary.get("validation_passed") else "failed")
        if not summary_cards_df.empty:
            st.dataframe(summary_cards_df, use_container_width=True, hide_index=True)
        with st.expander("Raw summary JSON"):
            st.json(summary)
    else:
        render_info_panel("No Monte Carlo summary yet. Run a simulation from the Overview tab.")

    if insights:
        render_section_header("Insights")
        for item in insights:
            st.markdown(f"- {item}")

    render_section_header("Champion probability chart")
    if champion_chart_path.is_file():
        st.image(str(champion_chart_path), use_container_width=True)
    elif not champion_display_df.empty:
        st.bar_chart(champion_display_df.set_index("team")["champion_probability"])

    if not champion_display_df.empty:
        st.dataframe(champion_display_df, use_container_width=True)

    render_section_header("Stage progression")
    if stage_heatmap_path.is_file():
        st.image(str(stage_heatmap_path), use_container_width=True)
    if not stage_display_df.empty:
        st.dataframe(stage_display_df, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        render_section_header("Finalists")
        if not finalists_df.empty:
            st.dataframe(finalists_df, use_container_width=True)
    with c2:
        render_section_header("Semifinalists")
        if not semifinalists_df.empty:
            st.dataframe(semifinalists_df, use_container_width=True)

    with st.expander("Validation & raw results"):
        if not validation_df.empty:
            st.dataframe(validation_df, use_container_width=True)
        if not simulation_results_df.empty:
            st.dataframe(simulation_results_df, use_container_width=True)

with tab_downloads:
    render_section_header("Download artifacts")
    for file_name, label, mime in [
        (MONTE_CARLO_SIMULATION_RESULTS_FILE, "Simulation results CSV", "text/csv"),
        (MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE, "Stage probabilities CSV", "text/csv"),
        (MONTE_CARLO_CHAMPION_PROBABILITIES_FILE, "Champion probabilities CSV", "text/csv"),
        (MONTE_CARLO_FINALISTS_FILE, "Finalists CSV", "text/csv"),
        (MONTE_CARLO_SEMIFINALISTS_FILE, "Semifinalists CSV", "text/csv"),
        (MONTE_CARLO_SUMMARY_FILE, "Monte Carlo summary JSON", "application/json"),
        (MONTE_CARLO_VALIDATION_REPORT_FILE, "Validation report CSV", "text/csv"),
    ]:
        render_download_card(label, file_name, PROCESSED_DATA_DIR / file_name, file_name=file_name, mime=mime)
    render_download_card(
        "Monte Carlo markdown report",
        "Narrative report for portfolio",
        report_md_path,
        file_name=MONTE_CARLO_REPORT_MD_FILE,
        mime="text/markdown",
    )

st.caption("Simulation probabilities are educational analytics estimates. They are not guarantees.")
