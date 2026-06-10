"""Streamlit page: Reports & Downloads — central artifact hub."""

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
    from app.streamlit_paths import (
        OFFICIAL_PROCESSED_DIR,
        PROCESSED_DATA_DIR,
        PROJECT_ROOT,
        REPORTS_DIR,
    )
except ModuleNotFoundError:
    from streamlit_paths import (
        OFFICIAL_PROCESSED_DIR,
        PROCESSED_DATA_DIR,
        PROJECT_ROOT,
        REPORTS_DIR,
    )

try:
    from app.components.ui import (
        inject_page_theme,
        render_download_card,
        render_hero,
        render_section_header,
    )
except ModuleNotFoundError:
    from components.ui import (
        inject_page_theme,
        render_download_card,
        render_hero,
        render_section_header,
    )

import src.utils.constants as C

FIGURES_DIR = REPORTS_DIR / "figures"
PORTFOLIO_DIR = PROJECT_ROOT / str(getattr(C, "PORTFOLIO_DIR", "portfolio"))

_MC_CHAMP = getattr(C, "MONTE_CARLO_CHAMPION_PROBABILITIES_FILE", "monte_carlo_champion_probabilities.csv")
_MC_STAGE = getattr(C, "MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE", "monte_carlo_team_stage_probabilities.csv")
_MC_SIM = getattr(C, "MONTE_CARLO_SIMULATION_RESULTS_FILE", "monte_carlo_simulation_results.csv")
_MC_FIN = getattr(C, "MONTE_CARLO_FINALISTS_FILE", "monte_carlo_finalists.csv")
_MC_SEMI = getattr(C, "MONTE_CARLO_SEMIFINALISTS_FILE", "monte_carlo_semifinalists.csv")
_MC_SUMMARY = getattr(C, "MONTE_CARLO_SUMMARY_FILE", "monte_carlo_summary.json")
_MC_REPORT = getattr(C, "MONTE_CARLO_REPORT_MD_FILE", "monte_carlo_report.md")
_MC_CHART = getattr(C, "MONTE_CARLO_CHAMPION_CHART_FILE", "monte_carlo_champion_probabilities.png")
_MC_HEATMAP = getattr(C, "MONTE_CARLO_STAGE_HEATMAP_FILE", "monte_carlo_stage_heatmap.png")

_AW_ALL = getattr(C, "WORLD_CUP_AWARDS_PREDICTIONS_FILE", "world_cup_awards_predictions.csv")
_AW_GB = getattr(C, "GOLDEN_BALL_PREDICTIONS_FILE", "golden_ball_predictions.csv")
_AW_GBT = getattr(C, "GOLDEN_BOOT_PREDICTIONS_FILE", "golden_boot_predictions.csv")
_AW_GG = getattr(C, "GOLDEN_GLOVE_PREDICTIONS_FILE", "golden_glove_predictions.csv")
_AW_YP = getattr(C, "YOUNG_PLAYER_PREDICTIONS_FILE", "young_player_predictions.csv")
_AW_FP = getattr(C, "FAIR_PLAY_PREDICTIONS_FILE", "fair_play_predictions.csv")
_AW_TOT = getattr(C, "TEAM_OF_THE_TOURNAMENT_FILE", "team_of_the_tournament.csv")
_AW_SUMMARY = getattr(C, "WORLD_CUP_AWARDS_SUMMARY_FILE", "world_cup_awards_summary.json")
_AW_REPORT = getattr(C, "WORLD_CUP_AWARDS_REPORT_FILE", "world_cup_awards_report.md")

_OFF_TEAMS = getattr(C, "OFFICIAL_TEAMS_FILE", "official_teams.csv")
_OFF_GROUPS = getattr(C, "OFFICIAL_GROUPS_FILE", "official_groups.csv")
_OFF_FIXTURES = getattr(C, "OFFICIAL_FIXTURES_FILE", "official_fixtures.csv")
_OFF_VENUES = getattr(C, "OFFICIAL_VENUES_FILE", "official_venues.csv")
_OFF_SUMMARY = getattr(C, "OFFICIAL_DATA_SUMMARY_FILE", "official_data_summary.json")

# ─────────────────────────────────────────────────────────────────────────────

inject_page_theme()
render_hero(
    "Reports & Downloads",
    "Download all analytics artifacts — Monte Carlo forecasts, awards predictions, "
    "official data, and portfolio files.",
    eyebrow="Analytics output hub",
)


def _count_available(paths: list[Path]) -> int:
    return sum(1 for p in paths if p.is_file())


# Status summary row
_all_paths = [
    PROCESSED_DATA_DIR / _MC_CHAMP,
    PROCESSED_DATA_DIR / _AW_ALL,
    OFFICIAL_PROCESSED_DIR / _OFF_TEAMS,
    REPORTS_DIR / _MC_REPORT,
    PORTFOLIO_DIR / "PORTFOLIO_README.md",
]
n_avail = _count_available(_all_paths)

c1, c2, c3 = st.columns(3)
with c1:
    mc_files = [PROCESSED_DATA_DIR / f for f in [_MC_CHAMP, _MC_STAGE, _MC_SUMMARY, _MC_REPORT]]
    n = _count_available(mc_files)
    st.markdown(
        f"""<div class="wc-card">
  <div class="wc-card-label">Monte Carlo</div>
  <div class="wc-card-value">{n}/{len(mc_files)}</div>
  <div class="wc-card-sub">files available</div>
</div>""",
        unsafe_allow_html=True,
    )
with c2:
    aw_files = [PROCESSED_DATA_DIR / f for f in [_AW_ALL, _AW_GB, _AW_GBT, _AW_GG, _AW_SUMMARY]]
    n = _count_available(aw_files)
    st.markdown(
        f"""<div class="wc-card">
  <div class="wc-card-label">Awards</div>
  <div class="wc-card-value">{n}/{len(aw_files)}</div>
  <div class="wc-card-sub">files available</div>
</div>""",
        unsafe_allow_html=True,
    )
with c3:
    off_files = [OFFICIAL_PROCESSED_DIR / f for f in [_OFF_TEAMS, _OFF_GROUPS, _OFF_FIXTURES]]
    n = _count_available(off_files)
    st.markdown(
        f"""<div class="wc-card">
  <div class="wc-card-label">Official data</div>
  <div class="wc-card-value">{n}/{len(off_files)}</div>
  <div class="wc-card-sub">files available</div>
</div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ─── Tabbed download sections ─────────────────────────────────────────────────
tab_mc, tab_awards, tab_official, tab_portfolio, tab_charts = st.tabs(
    ["Monte Carlo", "Awards", "Official Data", "Portfolio", "Charts & Visuals"]
)

with tab_mc:
    render_section_header("Monte Carlo simulation outputs")
    col1, col2 = st.columns(2)
    with col1:
        render_download_card(
            "Champion probabilities",
            "Team-level tournament champion estimates",
            PROCESSED_DATA_DIR / _MC_CHAMP,
            file_name=_MC_CHAMP,
        )
        render_download_card(
            "Stage probabilities",
            "Per-team probability of reaching each round",
            PROCESSED_DATA_DIR / _MC_STAGE,
            file_name=_MC_STAGE,
        )
        render_download_card(
            "Simulation results",
            "Raw per-simulation outcome data",
            PROCESSED_DATA_DIR / _MC_SIM,
            file_name=_MC_SIM,
        )
    with col2:
        render_download_card(
            "Finalists",
            "Most frequent finalists across simulations",
            PROCESSED_DATA_DIR / _MC_FIN,
            file_name=_MC_FIN,
        )
        render_download_card(
            "Semi-finalists",
            "Most frequent semi-finalists",
            PROCESSED_DATA_DIR / _MC_SEMI,
            file_name=_MC_SEMI,
        )
        render_download_card(
            "Summary JSON",
            "Top champion, run metadata",
            PROCESSED_DATA_DIR / _MC_SUMMARY,
            file_name=_MC_SUMMARY,
            mime="application/json",
        )
    render_download_card(
        "Narrative report",
        "Markdown report suitable for portfolio or presentation",
        REPORTS_DIR / _MC_REPORT,
        file_name=_MC_REPORT,
        mime="text/markdown",
    )

with tab_awards:
    render_section_header("Awards prediction outputs")
    col1, col2 = st.columns(2)
    with col1:
        render_download_card(
            "All awards combined",
            "Every award category in one CSV",
            PROCESSED_DATA_DIR / _AW_ALL,
            file_name=_AW_ALL,
        )
        render_download_card(
            "Golden Ball",
            "Best player predictions",
            PROCESSED_DATA_DIR / _AW_GB,
            file_name=_AW_GB,
        )
        render_download_card(
            "Golden Boot",
            "Top goal scorer predictions",
            PROCESSED_DATA_DIR / _AW_GBT,
            file_name=_AW_GBT,
        )
        render_download_card(
            "Golden Glove",
            "Best goalkeeper predictions",
            PROCESSED_DATA_DIR / _AW_GG,
            file_name=_AW_GG,
        )
    with col2:
        render_download_card(
            "Best Young Player",
            "Under-21 standout predictions",
            PROCESSED_DATA_DIR / _AW_YP,
            file_name=_AW_YP,
        )
        render_download_card(
            "Fair Play award",
            "Team discipline index predictions",
            PROCESSED_DATA_DIR / _AW_FP,
            file_name=_AW_FP,
        )
        render_download_card(
            "Team of the Tournament",
            "Best XI formation selection",
            PROCESSED_DATA_DIR / _AW_TOT,
            file_name=_AW_TOT,
        )
        render_download_card(
            "Awards summary JSON",
            "Validation + top picks",
            PROCESSED_DATA_DIR / _AW_SUMMARY,
            file_name=_AW_SUMMARY,
            mime="application/json",
        )
    render_download_card(
        "Awards narrative report",
        "Markdown write-up for all award categories",
        REPORTS_DIR / _AW_REPORT,
        file_name=_AW_REPORT,
        mime="text/markdown",
    )

with tab_official:
    render_section_header("Official World Cup data")
    col1, col2 = st.columns(2)
    with col1:
        render_download_card(
            "Teams",
            "48 confirmed teams with codes and groups",
            OFFICIAL_PROCESSED_DIR / _OFF_TEAMS,
            file_name=_OFF_TEAMS,
        )
        render_download_card(
            "Groups",
            "Group-stage assignments for all 12 groups",
            OFFICIAL_PROCESSED_DIR / _OFF_GROUPS,
            file_name=_OFF_GROUPS,
        )
    with col2:
        render_download_card(
            "Fixtures",
            "All 104 scheduled matches",
            OFFICIAL_PROCESSED_DIR / _OFF_FIXTURES,
            file_name=_OFF_FIXTURES,
        )
        render_download_card(
            "Venues",
            "16 stadium details",
            OFFICIAL_PROCESSED_DIR / _OFF_VENUES,
            file_name=_OFF_VENUES,
        )
    render_download_card(
        "Official data summary",
        "Data health snapshot JSON",
        OFFICIAL_PROCESSED_DIR / _OFF_SUMMARY,
        file_name=_OFF_SUMMARY,
        mime="application/json",
    )
    render_download_card(
        "Final readiness report",
        "Gate checklist for official_final mode",
        OFFICIAL_PROCESSED_DIR / "official_final_readiness_report.json",
        file_name="official_final_readiness_report.json",
        mime="application/json",
    )

with tab_portfolio:
    render_section_header("Portfolio & documentation")
    col1, col2 = st.columns(2)
    with col1:
        render_download_card(
            "Portfolio README",
            "Project overview for reviewers",
            PORTFOLIO_DIR / "PORTFOLIO_README.md",
            file_name="PORTFOLIO_README.md",
            mime="text/markdown",
        )
        render_download_card(
            "Demo script",
            "5-7 minute live walkthrough guide",
            PORTFOLIO_DIR / "demo_script.md",
            file_name="demo_script.md",
            mime="text/markdown",
        )
    with col2:
        render_download_card(
            "Final project summary",
            "Latest pipeline status JSON",
            PROCESSED_DATA_DIR / "final_project_summary.json",
            file_name="final_project_summary.json",
            mime="application/json",
        )

with tab_charts:
    render_section_header("Generated charts")
    col1, col2 = st.columns(2)
    with col1:
        champion_chart = FIGURES_DIR / _MC_CHART
        if champion_chart.is_file():
            st.image(str(champion_chart), caption="Champion probability bar chart", use_container_width=True)
            st.download_button(
                "Download champion chart",
                data=champion_chart.read_bytes(),
                file_name=_MC_CHART,
                mime="image/png",
                use_container_width=True,
            )
        else:
            st.info("Champion chart not yet generated. Run Monte Carlo simulation.")
    with col2:
        heatmap = FIGURES_DIR / _MC_HEATMAP
        if heatmap.is_file():
            st.image(str(heatmap), caption="Stage progression heatmap", use_container_width=True)
            st.download_button(
                "Download stage heatmap",
                data=heatmap.read_bytes(),
                file_name=_MC_HEATMAP,
                mime="image/png",
                use_container_width=True,
            )
        else:
            st.info("Stage heatmap not yet generated. Run Monte Carlo simulation.")

st.caption("All files are analytics outputs. Not affiliated with or endorsed by FIFA.")
