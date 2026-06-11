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

# ─── Page config (must be the very first st.* call) ────────────────────────────
st.set_page_config(
    page_title="World Cup 2026 AI Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Path / import bootstrapping ───────────────────────────────────────────────
try:
    from app.streamlit_paths import (
        FIGURES_DIR,
        OFFICIAL_DATA_DIR,
        OFFICIAL_PROCESSED_DIR,
        PROCESSED_DATA_DIR,
        PROJECT_ROOT,
        REPORTS_DIR,
    )
except ModuleNotFoundError:
    from streamlit_paths import (
        FIGURES_DIR,
        OFFICIAL_DATA_DIR,
        OFFICIAL_PROCESSED_DIR,
        PROCESSED_DATA_DIR,
        PROJECT_ROOT,
        REPORTS_DIR,
    )

try:
    from app.components.branding import render_branded_hero, render_sidebar_brand
except ModuleNotFoundError:
    from components.branding import render_branded_hero, render_sidebar_brand

try:
    from app.components.ui import (
        inject_page_theme,
        load_json_if_exists,
        render_champion_spotlight,
        render_metric_card,
        render_progress_bar,
        render_quick_nav_grid,
        render_section_header,
        render_warning_panel,
        render_success_panel,
    )
except ImportError:
    from app.components.ui import (
        inject_page_theme,
        load_json_if_exists,
        render_champion_spotlight,
        render_metric_card,
        render_progress_bar,
        render_quick_nav_cards,
        render_section_header,
        render_warning_panel,
        render_success_panel,
    )

    render_quick_nav_grid = render_quick_nav_cards  # older ui.py without nav grid helper
except ModuleNotFoundError:
    try:
        from components.ui import (
            inject_page_theme,
            load_json_if_exists,
            render_champion_spotlight,
            render_metric_card,
            render_progress_bar,
            render_quick_nav_grid,
            render_section_header,
            render_warning_panel,
            render_success_panel,
        )
    except ImportError:
        from components.ui import (
            inject_page_theme,
            load_json_if_exists,
            render_champion_spotlight,
            render_metric_card,
            render_progress_bar,
            render_quick_nav_cards,
            render_section_header,
            render_warning_panel,
            render_success_panel,
        )

        render_quick_nav_grid = render_quick_nav_cards


import src.utils.constants as C

# ─── File name constants ───────────────────────────────────────────────────────
_MC_SUMMARY = getattr(C, "MONTE_CARLO_SUMMARY_FILE", "monte_carlo_summary.json")
_MC_CHAMP = getattr(C, "MONTE_CARLO_CHAMPION_PROBABILITIES_FILE", "monte_carlo_champion_probabilities.csv")
_AWARDS_SUMMARY = getattr(C, "WORLD_CUP_AWARDS_SUMMARY_FILE", "world_cup_awards_summary.json")
_OFFICIAL_SUMMARY = getattr(C, "OFFICIAL_DATA_SUMMARY_FILE", "official_data_summary.json")
_GOLDEN_BALL_FILE = getattr(C, "GOLDEN_BALL_PREDICTIONS_FILE", "golden_ball_predictions.csv")


# ─── Data loader ───────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False, ttl=60)
def _load_status() -> dict:
    mc = load_json_if_exists(PROCESSED_DATA_DIR / _MC_SUMMARY)
    awards = load_json_if_exists(PROCESSED_DATA_DIR / _AWARDS_SUMMARY)
    official = load_json_if_exists(OFFICIAL_PROCESSED_DIR / _OFFICIAL_SUMMARY)
    try:
        from src.official.promotion import load_official_final_mode
        from src.official.final_readiness import evaluate_official_final_readiness
        mode = load_official_final_mode()
        readiness = evaluate_official_final_readiness()
        rs = readiness.get("summary", {})
    except Exception:
        mode, readiness, rs = {}, {}, {}
    return dict(mc=mc, awards=awards, official=official, mode=mode, readiness=readiness, rs=rs)


# ─── Homepage ──────────────────────────────────────────────────
def _homepage() -> None:
    inject_page_theme()

    d = _load_status()
    mc, awards, official = d["mc"], d["awards"], d["official"]
    rs, readiness = d["rs"], d["readiness"]
    official_final = bool(d["mode"].get("official_final_enabled"))

    teams_count = rs.get("teams_count") or official.get("teams_count", 0)
    fixtures_count = rs.get("fixtures_count") or official.get("fixtures_count", 0)
    checks_passed = rs.get("passed_checks", 0)
    checks_total = rs.get("total_checks", 15)
    is_final_ready = bool(readiness.get("is_official_final_ready", False))

    top_champion = mc.get("top_champion", "")
    top_champ_prob = float(mc.get("top_champion_probability", 0.0))
    num_sims = int(mc.get("num_simulations", 0))
    mc_ready = bool(mc)
    awards_ready = bool(awards)

    render_branded_hero(
        "World Cup 2026 AI Predictor",
        "Probabilistic forecasts for matches, the full tournament, and player awards — "
        "powered by ML models and official squad data.",
        eyebrow="Command Center",
    )

    s1, s2, s3, s4 = st.columns(4)
    data_mode = (
        "Official final" if official_final
        else ("Official draft" if teams_count > 0 else "Sample data")
    )
    mode_variant = "ok" if official_final else ("warn" if teams_count > 0 else "")

    with s1:
        render_metric_card("Data mode", data_mode, sub=f"{checks_passed}/{checks_total} checks", variant=mode_variant)
    with s2:
        if mc_ready and top_champion:
            render_metric_card(top_champion, f"{top_champ_prob:.1%}", sub=f"{num_sims:,} Monte Carlo runs", variant="accent")
        else:
            render_metric_card("Monte Carlo", "Not run", sub="Run simulation for forecasts", variant="warn")
    with s3:
        gb_winner = ""
        if awards_ready:
            try:
                import pandas as pd
                _gb = PROCESSED_DATA_DIR / _GOLDEN_BALL_FILE
                if _gb.is_file():
                    _gdf = pd.read_csv(_gb)
                    if not _gdf.empty and "player_name" in _gdf.columns:
                        gb_winner = str(_gdf.iloc[0]["player_name"])
            except Exception:
                pass
        awards_sub = f"Golden Ball: {gb_winner}" if gb_winner else "Generate on Awards page"
        render_metric_card("Awards", "Ready" if awards_ready else "Pending", sub=awards_sub, variant="ok" if awards_ready else "")
    with s4:
        ready_variant = "ok" if is_final_ready else ("warn" if checks_passed >= checks_total // 2 else "danger")
        ready_label = "Ready" if is_final_ready else ("In progress" if checks_passed > 0 else "Blocked")
        render_metric_card("Official gate", ready_label, sub=f"{checks_passed} of {checks_total} checks", variant=ready_variant)

    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

    render_section_header("Go to")
    render_quick_nav_grid([
        {"icon": "⚽", "title": "Match Predictor", "hint": "Win / draw / loss probabilities", "page": "pages/1_Match_Predictor.py"},
        {"icon": "📊", "title": "Monte Carlo", "hint": "Champion & stage probabilities", "page": "pages/9_Monte_Carlo_Simulator.py"},
        {"icon": "🥇", "title": "World Cup Awards", "hint": "Golden Ball, Boot, Glove & more", "page": "pages/17_World_Cup_Awards.py"},
        {"icon": "🏆", "title": "Tournament Sim", "hint": "Quick bracket simulation", "page": "pages/2_Tournament_Simulator.py"},
        {"icon": "✅", "title": "Data Health", "hint": "Official data readiness", "page": "pages/3_Data_Health.py"},
        {"icon": "📥", "title": "Reports", "hint": "Download all artifacts", "page": "pages/4_Reports_Downloads.py"},
    ])

    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown('<div class="wc-dash-panel">', unsafe_allow_html=True)
        st.markdown('<div class="wc-dash-panel-title">Champion forecast</div>', unsafe_allow_html=True)
        if mc_ready and top_champion:
            try:
                import pandas as pd
                champ_path = PROCESSED_DATA_DIR / _MC_CHAMP
                cx1, cx2 = st.columns([2, 3])
                with cx1:
                    render_champion_spotlight(top_champion, top_champ_prob)
                with cx2:
                    if champ_path.is_file():
                        champ_df = pd.read_csv(champ_path)
                        prob_col = next(
                            (c for c in ["champion_probability", "probability", "win_probability"] if c in champ_df.columns),
                            None,
                        )
                        name_col = next((c for c in ["team", "team_name", "name"] if c in champ_df.columns), None)
                        if prob_col and name_col:
                            top_df = (
                                champ_df[[name_col, prob_col]]
                                .rename(columns={name_col: "Team", prob_col: "Prob."})
                                .sort_values("Prob.", ascending=False)
                                .head(8)
                            )
                            top_df["Prob."] = top_df["Prob."].apply(lambda x: f"{float(x):.1%}")
                            st.dataframe(top_df, use_container_width=True, hide_index=True)
            except Exception:
                render_champion_spotlight(top_champion, top_champ_prob)
        else:
            st.info("Run **Monte Carlo Forecast** from the sidebar to populate champion probabilities.")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="wc-dash-panel">', unsafe_allow_html=True)
        st.markdown('<div class="wc-dash-panel-title">Data readiness</div>', unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        with m1:
            render_metric_card("Teams", str(teams_count) if teams_count else "—", sub="WC 2026 squads")
        with m2:
            render_metric_card("Fixtures", str(fixtures_count) if fixtures_count else "—", sub="Scheduled matches")
        progress_ratio = checks_passed / max(checks_total, 1)
        prog_kind = "ok" if is_final_ready else ("warn" if progress_ratio >= 0.5 else "danger")
        render_progress_bar(
            progress_ratio,
            label=f"Completeness — {checks_passed}/{checks_total}",
            kind=prog_kind,
        )
        if is_final_ready:
            render_success_panel("Official final mode enabled.")
        else:
            render_warning_panel("Complete checks on <strong>Data Health</strong> to unlock official final mode.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.caption("Analytics estimates only · Not affiliated with or endorsed by FIFA.")


# ─── Sidebar brand (logo upper-left, all pages) ────────────────────────────────
inject_page_theme()
with st.sidebar:
    render_sidebar_brand()

# ─── Navigation definition ─────────────────────────────────────────────────────
_pg = st.navigation(
    {
        "": [
            st.Page(_homepage, title="Command Center", icon="⚽", default=True),
        ],
        "Predictions": [
            st.Page("pages/1_Match_Predictor.py", title="Match Predictor", icon="⚽"),
            st.Page("pages/9_Monte_Carlo_Simulator.py", title="Monte Carlo Forecast", icon="📊"),
            st.Page("pages/2_Tournament_Simulator.py", title="Tournament Simulator", icon="🏆"),
        ],
        "Analytics": [
            st.Page("pages/17_World_Cup_Awards.py", title="World Cup Awards", icon="🥇"),
            st.Page("pages/3_Data_Health.py", title="Data Health", icon="✅"),
            st.Page("pages/4_Reports_Downloads.py", title="Reports & Downloads", icon="📥"),
        ],
        "Advanced": [
            st.Page("pages/_dev/4_Model_Explanation.py", title="Model Explanation", icon="🔬"),
            st.Page("pages/_dev/5_Tournament_Setup.py", title="Tournament Setup", icon="⚙️"),
            st.Page("pages/_dev/6_Group_Stage_Simulation.py", title="Group Stage", icon="📋"),
            st.Page("pages/_dev/7_Knockout_Simulation.py", title="Knockout", icon="⚡"),
            st.Page("pages/_dev/8_Full_Tournament_Run.py", title="Full Tournament Run", icon="🎯"),
            st.Page("pages/_dev/11_Official_Data_Health.py", title="Official Data", icon="📂"),
            st.Page("pages/_dev/12_Official_Squads_Health.py", title="Squads Health", icon="👥"),
            st.Page("pages/_dev/14_Official_Data_Population.py", title="Data Population", icon="📝"),
            st.Page(
                "pages/_dev/15_Source_Assisted_Population.py",
                title="Source Population",
                icon="🔗",
            ),
            st.Page(
                "pages/_dev/16_Official_Data_Population_Completion.py",
                title="Population Completion",
                icon="✔️",
            ),
        ],
    }
)

_pg.run()
