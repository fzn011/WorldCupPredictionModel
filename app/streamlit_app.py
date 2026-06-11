"""FIFA World Cup 2026 AI Predictor — main entry point and command center."""

from __future__ import annotations

import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _APP_DIR.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

import streamlit as st

st.set_page_config(
    page_title="World Cup 2026 AI Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    from app.styles.worldcup_theme import inject_worldcup_css
except ModuleNotFoundError:
    from styles.worldcup_theme import inject_worldcup_css

inject_worldcup_css()

try:
    from app.streamlit_paths import OFFICIAL_DATA_DIR, PROCESSED_DATA_DIR, PROJECT_ROOT
except ModuleNotFoundError:
    from streamlit_paths import OFFICIAL_DATA_DIR, PROCESSED_DATA_DIR, PROJECT_ROOT

try:
    from app.components.branding import render_branded_hero
except ModuleNotFoundError:
    from components.branding import render_branded_hero

try:
    from app.components.layout import navigate_to, render_app_shell
except ModuleNotFoundError:
    from components.layout import navigate_to, render_app_shell

try:
    from app.components.ui import (
        load_json_if_exists,
        render_action_grid,
        render_champion_spotlight,
        render_metric_card,
        render_section_header,
        render_success_panel,
        render_warning_panel,
    )
except ImportError:
    from app.components.ui import (
        load_json_if_exists,
        render_champion_spotlight,
        render_metric_card,
        render_quick_nav_cards,
        render_section_header,
        render_success_panel,
        render_warning_panel,
    )

    render_action_grid = render_quick_nav_cards
except ModuleNotFoundError:
    from components.ui import (
        load_json_if_exists,
        render_action_grid,
        render_champion_spotlight,
        render_metric_card,
        render_section_header,
        render_success_panel,
        render_warning_panel,
    )

try:
    from app.product_status import load_product_data_status
except ModuleNotFoundError:
    from product_status import load_product_data_status

import src.utils.constants as C

_MC_SUMMARY = getattr(C, "MONTE_CARLO_SUMMARY_FILE", "monte_carlo_summary.json")
_AWARDS_SUMMARY = getattr(C, "WORLD_CUP_AWARDS_SUMMARY_FILE", "world_cup_awards_summary.json")
_GOLDEN_BALL_FILE = getattr(C, "GOLDEN_BALL_PREDICTIONS_FILE", "golden_ball_predictions.csv")
_GOLDEN_BOOT_FILE = getattr(C, "GOLDEN_BOOT_PREDICTIONS_FILE", "golden_boot_predictions.csv")

_DEMO_SIM_THRESHOLD = 100


@st.cache_data(show_spinner=False, ttl=30)
def _load_status() -> dict:
    mc = load_json_if_exists(PROCESSED_DATA_DIR / _MC_SUMMARY)
    awards = load_json_if_exists(PROCESSED_DATA_DIR / _AWARDS_SUMMARY)
    pdata = load_product_data_status()
    return dict(mc=mc, awards=awards, pdata=pdata)


def _award_leader(file_name: str, col: str = "player_name") -> str:
    try:
        import pandas as pd

        path = PROCESSED_DATA_DIR / file_name
        if not path.is_file():
            return ""
        df = pd.read_csv(path)
        if df.empty or col not in df.columns:
            return ""
        return str(df.iloc[0][col])
    except Exception:
        return ""


def render_home_page() -> None:
    with st.spinner("Loading dashboard..."):
        d = _load_status()
    mc, awards, pdata = d["mc"], d["awards"], d["pdata"]

    top_champion = mc.get("top_champion", "")
    top_champ_prob = float(mc.get("top_champion_probability", 0.0))
    num_sims = int(mc.get("num_simulations", 0) or mc.get("successful_simulations", 0))
    mc_ready = bool(mc) and bool(top_champion)

    render_branded_hero(
        "World Cup 2026 AI Predictor",
        "Predict matches, simulate the tournament, and explore awards forecasts using official World Cup data.",
        eyebrow="Analytics Command Center",
    )

    cta1, cta2, cta3 = st.columns(3)
    with cta1:
        st.button(
            "Predict a Match",
            use_container_width=True,
            type="primary",
            key="home_cta_match",
            on_click=navigate_to,
            kwargs={"page": "Match Predictor"},
        )
    with cta2:
        st.button(
            "Forecast Tournament",
            use_container_width=True,
            type="primary",
            key="home_cta_forecast",
            on_click=navigate_to,
            kwargs={"page": "Tournament Forecast"},
        )
    with cta3:
        st.button(
            "Explore Awards",
            use_container_width=True,
            type="primary",
            key="home_cta_awards",
            on_click=navigate_to,
            kwargs={"page": "World Cup Awards"},
        )

    render_section_header("System status")
    s1, s2, s3, s4, s5, s6 = st.columns(6)
    with s1:
        render_metric_card(
            "Official Data",
            pdata["data_label"],
            sub="Tournament dataset",
            variant="ok" if pdata["is_verified"] else "warn",
        )
    with s2:
        render_metric_card("Teams", str(pdata["teams_count"] or "—"), sub="Qualified nations")
    with s3:
        render_metric_card("Fixtures", str(pdata["fixtures_count"] or "—"), sub="Scheduled matches")
    with s4:
        render_metric_card("Players", str(pdata["players_count"] or "—"), sub="Official squad pool")
    with s5:
        mc_label = "Available" if mc_ready and num_sims >= _DEMO_SIM_THRESHOLD else ("Sample" if mc_ready else "Unavailable")
        render_metric_card("Forecast", mc_label, sub="Monte Carlo", variant="ok" if mc_ready else "")
    with s6:
        render_metric_card("Awards", "Available" if awards else "Unavailable", sub="Player & team honors", variant="ok" if awards else "")

    render_section_header("Forecast snapshot")
    left, right = st.columns([3, 2], gap="large")
    with left:
        with st.container(border=True):
            if mc_ready:
                if num_sims < _DEMO_SIM_THRESHOLD:
                    render_warning_panel(
                        "Forecast sample is small. Run more simulations on the Tournament Forecast page "
                        "for stronger estimates."
                    )
                    st.button(
                        "Refresh forecast",
                        type="primary",
                        key="home_refresh_mc",
                        on_click=navigate_to,
                        kwargs={"page": "Tournament Forecast"},
                    )
                render_champion_spotlight(top_champion, top_champ_prob)
            else:
                st.info("Run a tournament forecast to see champion probabilities.")
                st.button(
                    "Open Tournament Forecast",
                    use_container_width=True,
                    key="home_open_forecast",
                    on_click=navigate_to,
                    kwargs={"page": "Tournament Forecast"},
                )

    with right:
        with st.container(border=True):
            gb = _award_leader(_GOLDEN_BALL_FILE)
            gbt = _award_leader(_GOLDEN_BOOT_FILE)
            a1, a2 = st.columns(2)
            with a1:
                render_metric_card("Golden Ball", gb or "—", sub="Top player", variant="accent" if gb else "")
            with a2:
                render_metric_card("Golden Boot", gbt or "—", sub="Top scorer", variant="accent" if gbt else "")

    render_section_header("Start here")
    render_action_grid([
        {"title": "Predict a Match", "hint": "Win, draw, and loss probabilities.", "button": "Launch Predictor", "page": "Match Predictor"},
        {"title": "Forecast Tournament", "hint": "Champion and stage progression estimates.", "button": "Open Forecast", "page": "Tournament Forecast"},
        {"title": "Explore Awards", "hint": "Golden Ball, Boot, Glove, and more.", "button": "View Awards", "page": "World Cup Awards"},
        {"title": "Download Reports", "hint": "Summaries, charts, and exports.", "button": "View Reports", "page": "Reports"},
    ])

    if pdata["is_verified"]:
        render_success_panel("Official tournament data is verified. All main features are available.")
    st.caption("Analytics estimates only. Not official FIFA predictions.")


render_app_shell(home_renderer=render_home_page)
