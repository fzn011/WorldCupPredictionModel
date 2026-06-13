"""Streamlit page: Quick Monte Carlo simulation (subset of Tournament Forecast)."""

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
    from app.components.layout import navigate_to
except ModuleNotFoundError:
    from components.layout import navigate_to

try:
    from app.components.ui import render_data_table, render_hero, render_metric_card, render_info_panel, render_section_header
except ModuleNotFoundError:
    from components.ui import render_data_table, render_hero, render_metric_card, render_info_panel, render_section_header

try:
    from app.streamlit_paths import PROCESSED_DATA_DIR, PROJECT_ROOT
except ModuleNotFoundError:
    from streamlit_paths import PROCESSED_DATA_DIR, PROJECT_ROOT

from src.simulation.monte_carlo_readiness import evaluate_monte_carlo_readiness  # noqa: E402
from src.simulation.prepare_monte_carlo import prepare_step15_monte_carlo_simulation  # noqa: E402
import src.utils.constants as C  # noqa: E402

MONTE_CARLO_CHAMPION_PROBABILITIES_FILE = getattr(
    C, "MONTE_CARLO_CHAMPION_PROBABILITIES_FILE", "monte_carlo_champion_probabilities.csv"
)
MONTE_CARLO_SUMMARY_FILE = getattr(C, "MONTE_CARLO_SUMMARY_FILE", "monte_carlo_summary.json")
MAX_MONTE_CARLO_SIMULATIONS = int(getattr(C, "MAX_MONTE_CARLO_SIMULATIONS", 5000))

QUICK_SIM_PRESETS: dict[str, dict[str, int]] = {
    "Quick — 10 sims, seed 42": {"num_simulations": 10, "base_seed": 42},
    "Standard — 25 sims, seed 42": {"num_simulations": 25, "base_seed": 42},
    "Extended — 50 sims, seed 42": {"num_simulations": 50, "base_seed": 42},
}

_SESSION_QUICK_MC_PENDING = "quick_mc_pending_run"
_SESSION_QUICK_MC_NOTICE = "quick_mc_run_notice"


def _load_champion_probs() -> pd.DataFrame:
    path = PROCESSED_DATA_DIR / MONTE_CARLO_CHAMPION_PROBABILITIES_FILE
    if not path.is_file():
        return pd.DataFrame()
    return pd.read_csv(path)


def _load_summary() -> dict:
    path = PROCESSED_DATA_DIR / MONTE_CARLO_SUMMARY_FILE
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _execute_pending_quick_run() -> None:
    pending = st.session_state.pop(_SESSION_QUICK_MC_PENDING, None)
    if not pending:
        return

    simulations = int(pending["num_simulations"])
    seed = int(pending["base_seed"])
    readiness = evaluate_monte_carlo_readiness(project_root=PROJECT_ROOT)
    if not readiness.get("ready"):
        st.session_state[_SESSION_QUICK_MC_NOTICE] = {
            "level": "error",
            "message": "Quick simulation blocked — fix readiness issues first.",
            "details": readiness,
        }
        return

    progress = st.progress(0.0, text="Running quick Monte Carlo simulation…")

    def _on_progress(completed: int, total: int, _latest: dict) -> None:
        progress.progress(completed / max(total, 1), text=f"Simulation {completed} of {total}")

    try:
        summary = prepare_step15_monte_carlo_simulation(
            num_simulations=simulations,
            base_seed=seed,
            progress_callback=_on_progress,
            skip_readiness_check=True,
        )
        if summary.get("successful_simulations", 0) == 0:
            st.session_state[_SESSION_QUICK_MC_NOTICE] = {
                "level": "error",
                "message": "All quick simulations failed.",
                "details": summary,
            }
        else:
            st.session_state[_SESSION_QUICK_MC_NOTICE] = {
                "level": "success",
                "message": (
                    f"Quick simulation complete — {summary.get('successful_simulations', 0):,} runs, "
                    f"top champion: {summary.get('top_champion', '—')} "
                    f"({float(summary.get('top_champion_probability', 0.0)):.1%})."
                ),
                "details": summary,
            }
    except Exception as exc:
        st.session_state[_SESSION_QUICK_MC_NOTICE] = {
            "level": "error",
            "message": f"Quick simulation failed: {exc}",
            "details": None,
        }
    finally:
        progress.empty()


def render_page() -> None:
    render_hero(
        "Quick Simulation",
        "Fast Monte Carlo runs for champion probabilities. "
        "For full charts, reports, and presets up to 5,000 sims, use Tournament Forecast.",
        eyebrow="Quick simulation",
    )

    _execute_pending_quick_run()

    notice = st.session_state.pop(_SESSION_QUICK_MC_NOTICE, None)
    if isinstance(notice, dict):
        level = notice.get("level", "info")
        message = notice.get("message", "")
        if level == "success":
            st.success(message)
        elif level == "error":
            st.error(message)
        elif level == "warning":
            st.warning(message)
        else:
            st.info(message)
        if notice.get("details") is not None:
            with st.expander("Run details"):
                st.json(notice["details"])

    readiness = evaluate_monte_carlo_readiness(project_root=PROJECT_ROOT)
    if readiness.get("ready"):
        st.success("Ready to run quick Monte Carlo simulations.")
    else:
        st.error("Quick simulation is blocked:")
        for item in readiness.get("blockers", []):
            st.markdown(f"- {item}")

    render_info_panel(
        "This page runs the **same Monte Carlo engine** as Tournament Forecast, "
        "with smaller presets for faster feedback."
    )

    summary = _load_summary()
    champion_df = _load_champion_probs()

    if not champion_df.empty:
        render_section_header("Latest champion probabilities")
        top3 = champion_df.sort_values("champion_probability", ascending=False).head(3)
        t1, t2, t3 = st.columns(3)
        for col, (_, row) in zip((t1, t2, t3), top3.iterrows(), strict=False):
            with col:
                render_metric_card(
                    str(row["team"]),
                    f"{float(row['champion_probability']):.1%}",
                    sub="Champion probability",
                    variant="accent",
                )
        render_data_table(
            champion_df.sort_values("champion_probability", ascending=False).reset_index(drop=True),
            hide_index=True,
        )
        if summary:
            st.caption(
                f"Based on {summary.get('successful_simulations', summary.get('num_simulations', '—'))} "
                f"simulations (seed {summary.get('base_seed', '—')})."
            )

    render_section_header("Simulation settings")
    preset_names = list(QUICK_SIM_PRESETS.keys())
    if "quick_mc_preset" not in st.session_state:
        st.session_state.quick_mc_preset = preset_names[0]

    preset = st.selectbox(
        "Quick preset",
        preset_names,
        index=preset_names.index(st.session_state.quick_mc_preset)
        if st.session_state.quick_mc_preset in preset_names
        else 0,
        key="quick_mc_preset",
    )
    preset_values = QUICK_SIM_PRESETS[preset]
    sim_col, seed_col = st.columns(2)
    with sim_col:
        render_metric_card("Simulations", f"{preset_values['num_simulations']:,}", sub="From preset")
    with seed_col:
        render_metric_card("Base seed", str(preset_values["base_seed"]), sub="From preset")
    st.caption(
        f"Will run **{preset_values['num_simulations']:,}** simulations with base seed **{preset_values['base_seed']}**."
    )

    with st.form("quick_simulation_form", clear_on_submit=False):
        run_clicked = st.form_submit_button(
            "Run quick simulation",
            type="primary",
            disabled=not readiness.get("ready"),
        )
        open_forecast = st.form_submit_button("Open full Tournament Forecast")

    if run_clicked:
        st.session_state[_SESSION_QUICK_MC_PENDING] = dict(QUICK_SIM_PRESETS[st.session_state.quick_mc_preset])
        st.rerun()

    if open_forecast:
        navigate_to("Tournament Forecast")

    st.caption(f"For runs above {max(QUICK_SIM_PRESETS.values(), key=lambda x: x['num_simulations'])['num_simulations']:,} simulations, use Tournament Forecast (up to {MAX_MONTE_CARLO_SIMULATIONS:,}).")
