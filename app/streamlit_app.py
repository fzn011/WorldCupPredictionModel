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
    from app.streamlit_paths import OFFICIAL_DATA_DIR, OFFICIAL_PROCESSED_DIR, PROCESSED_DATA_DIR, PROJECT_ROOT
except ModuleNotFoundError:
    from streamlit_paths import OFFICIAL_DATA_DIR, OFFICIAL_PROCESSED_DIR, PROCESSED_DATA_DIR, PROJECT_ROOT

try:
    from app.components.branding import render_branded_hero, render_sidebar_brand
except ModuleNotFoundError:
    from components.branding import render_branded_hero, render_sidebar_brand

try:
    from app.components.ui import (
        inject_page_theme,
        load_json_if_exists,
        render_action_grid,
        render_champion_spotlight,
        render_metric_card,
        render_section_header,
        render_success_panel,
        render_info_panel,
    )
except ImportError:
    from app.components.ui import (
        inject_page_theme,
        load_json_if_exists,
        render_champion_spotlight,
        render_metric_card,
        render_quick_nav_cards,
        render_section_header,
        render_success_panel,
        render_info_panel,
    )

    render_action_grid = render_quick_nav_cards
except ModuleNotFoundError:
    from components.ui import (
        inject_page_theme,
        load_json_if_exists,
        render_action_grid,
        render_champion_spotlight,
        render_metric_card,
        render_section_header,
        render_success_panel,
        render_info_panel,
    )

import src.utils.constants as C

_MC_SUMMARY = getattr(C, "MONTE_CARLO_SUMMARY_FILE", "monte_carlo_summary.json")
_MC_CHAMP = getattr(C, "MONTE_CARLO_CHAMPION_PROBABILITIES_FILE", "monte_carlo_champion_probabilities.csv")
_AWARDS_SUMMARY = getattr(C, "WORLD_CUP_AWARDS_SUMMARY_FILE", "world_cup_awards_summary.json")
_GOLDEN_BALL_FILE = getattr(C, "GOLDEN_BALL_PREDICTIONS_FILE", "golden_ball_predictions.csv")
_GOLDEN_BOOT_FILE = getattr(C, "GOLDEN_BOOT_PREDICTIONS_FILE", "golden_boot_predictions.csv")

_DEMO_SIM_THRESHOLD = 100


@st.cache_data(show_spinner=False, ttl=30)
def _load_status() -> dict:
    mc = load_json_if_exists(PROCESSED_DATA_DIR / _MC_SUMMARY)
    awards = load_json_if_exists(PROCESSED_DATA_DIR / _AWARDS_SUMMARY)
    official = load_json_if_exists(OFFICIAL_PROCESSED_DIR / getattr(C, "OFFICIAL_DATA_SUMMARY_FILE", "official_data_summary.json"))
    try:
        from src.official.promotion import load_official_final_mode
        from src.official.final_readiness import evaluate_official_final_readiness

        mode = load_official_final_mode()
        readiness = evaluate_official_final_readiness()
        rs = readiness.get("summary", {})
    except Exception:
        mode, readiness, rs = {}, {}, {}
    return dict(mc=mc, awards=awards, official=official, mode=mode, readiness=readiness, rs=rs)


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


def _homepage() -> None:
    inject_page_theme()
    d = _load_status()
    mc, awards, official = d["mc"], d["awards"], d["official"]
    rs, readiness = d["rs"], d["readiness"]
    official_final = bool(d["mode"].get("official_final_enabled"))
    is_data_ready = bool(readiness.get("is_official_final_ready", False)) or official_final

    teams_count = rs.get("teams_count") or official.get("teams_count", 0)
    fixtures_count = rs.get("fixtures_count") or official.get("fixtures_count", 0)
    players_count = rs.get("players_count") or official.get("players_count", 0)

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
        st.page_link("pages/1_Match_Predictor.py", label="Predict a Match", use_container_width=True)
    with cta2:
        st.page_link("pages/9_Monte_Carlo_Simulator.py", label="View Tournament Forecast", use_container_width=True)
    with cta3:
        st.page_link("pages/17_World_Cup_Awards.py", label="Explore Awards", use_container_width=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    render_section_header("System status")

    data_status = "Ready" if is_data_ready else "In progress"
    data_variant = "ok" if is_data_ready else "warn"
    mc_status = "Available" if mc_ready else "Run forecast"
    mc_variant = "ok" if mc_ready and num_sims >= _DEMO_SIM_THRESHOLD else ("warn" if mc_ready else "")
    awards_status = "Available" if awards else "Generate forecast"

    s1, s2, s3, s4, s5, s6 = st.columns(6)
    with s1:
        render_metric_card("Official Data", data_status, sub="Verified tournament dataset", variant=data_variant)
    with s2:
        render_metric_card("Teams", str(teams_count or "—"), sub="Qualified nations")
    with s3:
        render_metric_card("Fixtures", str(fixtures_count or "—"), sub="Scheduled matches")
    with s4:
        render_metric_card("Players", str(players_count or "—"), sub="Official squad pool")
    with s5:
        render_metric_card("Monte Carlo", mc_status, sub="Tournament forecast", variant=mc_variant)
    with s6:
        render_metric_card("Awards", awards_status, sub="Player & team awards", variant="ok" if awards else "")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    render_section_header("Forecast snapshot")

    left, right = st.columns([3, 2], gap="large")
    with left:
        with st.container(border=True):
            if mc_ready:
                if num_sims < _DEMO_SIM_THRESHOLD:
                    render_info_panel(
                        "Demo sample only. Run more simulations on the Tournament Forecast page for stronger estimates."
                    )
                render_champion_spotlight(
                    top_champion,
                    top_champ_prob,
                    sub="" if num_sims >= _DEMO_SIM_THRESHOLD else "Preview from limited sample",
                )
            else:
                render_info_panel("Run a tournament forecast to see champion probabilities here.")

    with right:
        with st.container(border=True):
            gb = _award_leader(_GOLDEN_BALL_FILE)
            gbt = _award_leader(_GOLDEN_BOOT_FILE)
            a1, a2 = st.columns(2)
            with a1:
                render_metric_card("Golden Ball", gb or "—", sub="Top player estimate", variant="accent" if gb else "")
            with a2:
                render_metric_card("Golden Boot", gbt or "—", sub="Top scorer estimate", variant="accent" if gbt else "")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    render_section_header("Start here")
    render_action_grid([
        {
            "title": "Predict a Match",
            "hint": "Win, draw, and loss probabilities for any fixture.",
            "button": "Launch Predictor",
            "page": "pages/1_Match_Predictor.py",
        },
        {
            "title": "Forecast Tournament",
            "hint": "Monte Carlo champion and stage progression estimates.",
            "button": "Open Forecast",
            "page": "pages/9_Monte_Carlo_Simulator.py",
        },
        {
            "title": "Explore Awards",
            "hint": "Golden Ball, Boot, Glove, and team honors.",
            "button": "View Awards",
            "page": "pages/17_World_Cup_Awards.py",
        },
        {
            "title": "Download Reports",
            "hint": "CSV summaries, charts, and portfolio documents.",
            "button": "View Reports",
            "page": "pages/4_Reports_Downloads.py",
        },
    ])

    if is_data_ready:
        render_success_panel("Official data verified. All main features are available.")
    else:
        render_info_panel("Data verification in progress. Core features remain available while datasets are finalized.")

    st.caption("Analytics estimates only. Not official FIFA predictions.")


def _user_navigation() -> dict:
    return {
        "": [
            st.Page(_homepage, title="Home", default=True),
            st.Page("pages/1_Match_Predictor.py", title="Match Predictor"),
            st.Page("pages/2_Tournament_Simulator.py", title="Tournament Forecast"),
            st.Page("pages/9_Monte_Carlo_Simulator.py", title="Monte Carlo Forecast"),
            st.Page("pages/17_World_Cup_Awards.py", title="World Cup Awards"),
            st.Page("pages/4_Reports_Downloads.py", title="Reports"),
            st.Page("pages/3_Data_Health.py", title="Data Quality"),
        ],
    }


def _admin_navigation() -> dict:
    return {
        "Admin Tools": [
            st.Page("pages/_dev/11_Official_Data_Health.py", title="Official Data Health"),
            st.Page("pages/_dev/12_Official_Squads_Health.py", title="Squads Health"),
            st.Page("pages/_dev/14_Official_Data_Population.py", title="Data Import Tools"),
            st.Page("pages/_dev/15_Source_Assisted_Population.py", title="Source Import Tools"),
            st.Page("pages/_dev/16_Official_Data_Population_Completion.py", title="Import Completion"),
            st.Page("pages/_dev/5_Tournament_Setup.py", title="Tournament Setup"),
            st.Page("pages/_dev/6_Group_Stage_Simulation.py", title="Group Stage Simulation"),
            st.Page("pages/_dev/7_Knockout_Simulation.py", title="Knockout Simulation"),
            st.Page("pages/_dev/8_Full_Tournament_Run.py", title="Full Tournament Run"),
            st.Page("pages/_dev/4_Model_Explanation.py", title="Model Explanation"),
        ],
    }


inject_page_theme()
with st.sidebar:
    render_sidebar_brand()
    show_technical = st.checkbox("Show technical tools", value=False, help="Reveal admin and diagnostic pages.")

nav = _user_navigation()
if show_technical:
    nav.update(_admin_navigation())

st.navigation(nav).run()
