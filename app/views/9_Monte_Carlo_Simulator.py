"""Streamlit page: Monte Carlo forecast dashboard."""

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
        render_data_table,
        render_download_card,
        render_hero,
        render_metric_card,
        render_section_header,
    )
except ModuleNotFoundError:
    from components.ui import (  # noqa: E402
        inject_page_theme,
        render_data_table,
        render_download_card,
        render_hero,
        render_metric_card,
        render_section_header,
    )

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
MAX_MONTE_CARLO_SIMULATIONS = int(getattr(C, "MAX_MONTE_CARLO_SIMULATIONS", 5000))


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


def render_page() -> None:
    render_hero(
        "Tournament Forecast",
        "Monte Carlo simulation of the full tournament — champion and stage progression probabilities.",
        eyebrow="Tournament analytics",
    )

    with st.spinner("Loading forecast data..."):
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

    render_section_header("Current forecast")
    if summary:
        top = summary.get("top_champion", "—")
        prob = float(summary.get("top_champion_probability", 0.0))
        n_sims = int(summary.get("num_simulations", 0) or summary.get("successful_simulations", 0))
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            render_metric_card("Top champion", str(top), variant="accent")
        with m2:
            render_metric_card("Win probability", f"{prob:.1%}", variant="accent")
        with m3:
            render_metric_card("Simulations", f"{n_sims:,}", sub="Completed runs")
        with m4:
            render_metric_card("Validation", "Ready" if summary.get("validation_passed") else "Needs review", variant="ok" if summary.get("validation_passed") else "warn")
        if not champion_display_df.empty:
            render_data_table(champion_display_df.head(5), use_container_width=True, hide_index=True)
    else:
        st.info("No forecast yet. Run a simulation below to generate champion probabilities.")

    tab_overview, tab_results, tab_downloads = st.tabs(["Simulation settings", "Results and charts", "Downloads"])

    report_md_path = REPORTS_DIR / MONTE_CARLO_REPORT_MD_FILE
    champion_chart_path = FIGURES_DIR / MONTE_CARLO_CHAMPION_CHART_FILE
    stage_heatmap_path = FIGURES_DIR / MONTE_CARLO_STAGE_HEATMAP_FILE

    with tab_overview:
        render_section_header("Simulation settings")

        if st.session_state.get("mc_run_notice"):
            notice = st.session_state.pop("mc_run_notice")
            level = notice.get("level", "info")
            message = notice.get("message", "")
            if level == "success":
                st.success(message)
            elif level == "warning":
                st.warning(message)
            elif level == "error":
                st.error(message)
            else:
                st.info(message)
            if notice.get("details") is not None:
                with st.expander("Run details"):
                    st.json(notice["details"])

        if st.session_state.get("mc_report_notice"):
            notice = st.session_state.pop("mc_report_notice")
            level = notice.get("level", "info")
            message = notice.get("message", "")
            if level == "success":
                st.success(message)
            elif level == "warning":
                st.warning(message)
            else:
                st.info(message)
            if notice.get("details") is not None:
                with st.expander("Report summary"):
                    st.json(notice["details"])

        with st.form("mc_simulation_controls", clear_on_submit=False):
            simulations = int(
                st.number_input(
                    "Number of simulations",
                    min_value=1,
                    max_value=MAX_MONTE_CARLO_SIMULATIONS,
                    value=DEFAULT_MONTE_CARLO_SIMULATIONS,
                    step=1,
                    help=f"Run between 1 and {MAX_MONTE_CARLO_SIMULATIONS:,} full-tournament simulations.",
                )
            )
            seed = int(
                st.number_input(
                    "Base seed",
                    min_value=0,
                    max_value=1_000_000,
                    value=DEFAULT_MONTE_CARLO_SEED,
                    step=1,
                )
            )
            controls_col1, controls_col2 = st.columns(2)
            run_clicked = controls_col1.form_submit_button(
                "Run Monte Carlo simulation",
                type="primary",
            )
            report_clicked = controls_col2.form_submit_button("Generate report")

        if run_clicked:
            with st.spinner(f"Running {simulations:,} Monte Carlo simulations…"):
                try:
                    run_summary = prepare_step15_monte_carlo_simulation(
                        num_simulations=simulations,
                        base_seed=seed,
                    )
                    if run_summary.get("successful_simulations", 0) == 0:
                        st.session_state["mc_run_notice"] = {
                            "level": "error",
                            "message": "All simulations failed. Check model/data readiness, then retry.",
                            "details": run_summary,
                        }
                    elif run_summary.get("validation_passed"):
                        st.session_state["mc_run_notice"] = {
                            "level": "success",
                            "message": "Monte Carlo simulation completed and validated.",
                            "details": run_summary,
                        }
                    else:
                        st.session_state["mc_run_notice"] = {
                            "level": "warning",
                            "message": "Monte Carlo simulation completed with validation issues.",
                            "details": run_summary,
                        }
                except Exception as exc:
                    st.session_state["mc_run_notice"] = {
                        "level": "error",
                        "message": f"Monte Carlo simulation failed: {exc}",
                        "details": None,
                    }
            st.rerun()

        if report_clicked:
            with st.spinner("Generating Monte Carlo report artifacts…"):
                try:
                    report_summary = prepare_step16_monte_carlo_report()
                    st.session_state["mc_report_notice"] = {
                        "level": "success",
                        "message": "Monte Carlo report artifacts generated successfully.",
                        "details": report_summary,
                    }
                except FileNotFoundError as exc:
                    st.session_state["mc_report_notice"] = {
                        "level": "warning",
                        "message": str(exc),
                        "details": None,
                    }
                except Exception as exc:
                    st.session_state["mc_report_notice"] = {
                        "level": "error",
                        "message": f"Report generation failed: {exc}",
                        "details": None,
                    }
            st.rerun()

        st.caption("Outputs are simulation estimates, not certainties.")

    with tab_results:
        render_section_header("Simulation summary")
        if summary:
            m1, m2, m3, m4, m5, m6 = st.columns(6)
            with m1:
                render_metric_card("Simulations", str(summary.get("num_simulations", 0)))
            with m2:
                render_metric_card("Successful", str(summary.get("successful_simulations", 0)), variant="ok")
            with m3:
                failed = summary.get("failed_simulations", 0)
                render_metric_card("Failed", str(failed), variant="danger" if failed else "ok")
            with m4:
                render_metric_card("Top champion", str(summary.get("top_champion", "—")), variant="accent")
            with m5:
                render_metric_card(
                    "Champion prob.",
                    f"{float(summary.get('top_champion_probability', 0.0)):.1%}",
                    variant="accent",
                )
            with m6:
                passed = summary.get("validation_passed")
                render_metric_card(
                    "Validation",
                    "Passed" if passed else "Failed",
                    variant="ok" if passed else "danger",
                )
            if not summary_cards_df.empty:
                render_data_table(summary_cards_df, use_container_width=True, hide_index=True)
            with st.expander("Raw summary JSON"):
                st.json(summary)
        else:
            st.info("No Monte Carlo summary found yet. Run a simulation from the Simulation settings tab.")

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
            render_data_table(champion_display_df, use_container_width=True)

        render_section_header("Stage progression")
        if stage_heatmap_path.is_file():
            st.image(str(stage_heatmap_path), use_container_width=True)
        if not stage_display_df.empty:
            render_data_table(stage_display_df, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            render_section_header("Finalists")
            if not finalists_df.empty:
                render_data_table(finalists_df, use_container_width=True)
        with c2:
            render_section_header("Semifinalists")
            if not semifinalists_df.empty:
                render_data_table(semifinalists_df, use_container_width=True)

        with st.expander("Validation & raw results"):
            if not validation_df.empty:
                render_data_table(validation_df, use_container_width=True)
            if not simulation_results_df.empty:
                render_data_table(simulation_results_df, use_container_width=True)

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
