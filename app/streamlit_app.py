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

try:
    from app.styles.worldcup_theme import inject_worldcup_css
except ModuleNotFoundError:
    from styles.worldcup_theme import inject_worldcup_css

inject_worldcup_css()

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
    from app.components.ui import (
        inject_page_theme,
        load_json_if_exists,
        render_champion_spotlight,
        render_hero,
        render_metric_card,
        render_progress_bar,
        render_section_header,
        render_status_badge,
        render_warning_panel,
        render_success_panel,
    )
except ModuleNotFoundError:
    from components.ui import (
        inject_page_theme,
        load_json_if_exists,
        render_champion_spotlight,
        render_hero,
        render_metric_card,
        render_progress_bar,
        render_section_header,
        render_status_badge,
        render_warning_panel,
        render_success_panel,
    )

try:
    from app.styles.worldcup_theme import COLORS
except ModuleNotFoundError:
    from styles.worldcup_theme import COLORS

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


# ─── Homepage ──────────────────────────────────────────────────────────────────
def _homepage() -> None:
    inject_page_theme()

    d = _load_status()
    mc, awards, official = d["mc"], d["awards"], d["official"]
    rs, readiness = d["rs"], d["readiness"]
    official_final = bool(d["mode"].get("official_final_enabled"))

    teams_count = rs.get("teams_count") or official.get("teams_count", 0)
    fixtures_count = rs.get("fixtures_count") or official.get("fixtures_count", 0)
    players_count = rs.get("players_count", 0)
    checks_passed = rs.get("passed_checks", 0)
    checks_total = rs.get("total_checks", 15)
    is_final_ready = bool(readiness.get("is_official_final_ready", False))

    top_champion = mc.get("top_champion", "")
    top_champ_prob = float(mc.get("top_champion_probability", 0.0))
    num_sims = int(mc.get("num_simulations", 0))
    mc_ready = bool(mc)
    awards_ready = bool(awards)

    # Hero
    render_hero(
        "World Cup 2026 AI Predictor",
        "Predict, simulate, and explore FIFA World Cup 2026 outcomes using ML models, "
        "Monte Carlo simulation, and official team data.",
        eyebrow="FIFA World Cup 2026 Analytics",
    )

    # Status row
    render_section_header("Live status")
    s1, s2, s3, s4 = st.columns(4)

    with s1:
        data_mode = (
            "official_final" if official_final
            else ("official_draft" if teams_count > 0 else "sample")
        )
        mode_badge = "ok" if official_final else ("warn" if teams_count > 0 else "muted")
        st.markdown(
            f"""
<div class="wc-card">
  <div class="wc-card-label">Data mode</div>
  <div style="margin:0.4rem 0;">{render_status_badge(data_mode, mode_badge)}</div>
  <div class="wc-card-sub">{checks_passed}/{checks_total} readiness checks</div>
</div>
            """,
            unsafe_allow_html=True,
        )

    with s2:
        if mc_ready and top_champion:
            st.markdown(
                f"""
<div class="wc-card wc-card-gold">
  <div class="wc-card-label">Monte Carlo forecast</div>
  <div class="wc-card-value">{top_champion}</div>
  <div class="wc-card-sub">{top_champ_prob:.1%} champion · {num_sims:,} simulations</div>
</div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
<div class="wc-card">
  <div class="wc-card-label">Monte Carlo forecast</div>
  <div style="margin:0.4rem 0;">{render_status_badge("Not run yet", "muted")}</div>
  <div class="wc-card-sub">Run simulation to generate champion probabilities</div>
</div>
                """,
                unsafe_allow_html=True,
            )

    with s3:
        awards_badge = "ok" if awards_ready else "muted"
        awards_label = "Available" if awards_ready else "Not generated"
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
        sub = f"Golden Ball: {gb_winner}" if gb_winner else "Generate awards to see top picks"
        st.markdown(
            f"""
<div class="wc-card">
  <div class="wc-card-label">Awards analytics</div>
  <div style="margin:0.4rem 0;">{render_status_badge(awards_label, awards_badge)}</div>
  <div class="wc-card-sub">{sub}</div>
</div>
            """,
            unsafe_allow_html=True,
        )

    with s4:
        ready_badge = (
            "ok" if is_final_ready
            else ("warn" if checks_passed >= checks_total // 2 else "danger")
        )
        ready_label = (
            "Ready" if is_final_ready
            else ("In progress" if checks_passed > 0 else "Blocked")
        )
        st.markdown(
            f"""
<div class="wc-card">
  <div class="wc-card-label">Official final gate</div>
  <div style="margin:0.4rem 0;">{render_status_badge(ready_label, ready_badge)}</div>
  <div class="wc-card-sub">{checks_passed} of {checks_total} checks passing</div>
</div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Key metrics
    render_section_header("Tournament data")
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        render_metric_card("Teams", str(teams_count) if teams_count else "—", sub="48 total in WC 2026")
    with m2:
        render_metric_card("Fixtures", str(fixtures_count) if fixtures_count else "—", sub="104 total matches")
    with m3:
        render_metric_card("Players", str(players_count) if players_count else "—", sub="26 per squad")
    with m4:
        render_metric_card(
            "Simulations",
            f"{num_sims:,}" if num_sims else "—",
            sub="Monte Carlo runs",
        )
    with m5:
        prog_variant = "ok" if is_final_ready else ("warn" if checks_passed >= 8 else "danger")
        render_metric_card(
            "Readiness",
            f"{checks_passed}/{checks_total}",
            sub="Official data checks",
            variant=prog_variant,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick actions
    render_section_header("Navigate")
    a1, a2, a3, a4, a5, a6 = st.columns(6)
    _nav = [
        (a1, "⚽", "Match Predictor", "Win/draw/loss probabilities", "pages/1_Match_Predictor.py"),
        (a2, "📊", "Monte Carlo", "Champion & stage reach forecast", "pages/9_Monte_Carlo_Simulator.py"),
        (a3, "🥇", "Awards", "Golden Ball, Boot, Glove & more", "pages/17_World_Cup_Awards.py"),
        (a4, "🏆", "Tournament", "Quick bracket simulation", "pages/2_Tournament_Simulator.py"),
        (a5, "✅", "Data Health", "Official data completeness gate", "pages/3_Data_Health.py"),
        (a6, "📥", "Reports", "Download all analytics artifacts", "pages/4_Reports_Downloads.py"),
    ]
    for col, icon, title, hint, page in _nav:
        with col:
            st.markdown(
                f"""
<div class="wc-action-card">
  <div class="wc-action-icon">{icon}</div>
  <div class="wc-action-title">{title}</div>
  <div class="wc-action-hint">{hint}</div>
</div>
                """,
                unsafe_allow_html=True,
            )
            st.page_link(page, label=f"Open {title}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Monte Carlo spotlight
    if mc_ready and top_champion:
        render_section_header("Champion forecast")
        try:
            import pandas as pd
            champ_path = PROCESSED_DATA_DIR / _MC_CHAMP
            if champ_path.is_file():
                champ_df = pd.read_csv(champ_path)
                prob_col = next(
                    (c for c in ["champion_probability", "probability", "win_probability"]
                     if c in champ_df.columns),
                    None,
                )
                name_col = next(
                    (c for c in ["team", "team_name", "name"] if c in champ_df.columns),
                    None,
                )
                if prob_col and name_col:
                    champ_df = (
                        champ_df[[name_col, prob_col]]
                        .rename(columns={name_col: "Team", prob_col: "Probability"})
                        .sort_values("Probability", ascending=False)
                        .head(10)
                    )
                    champ_df["Probability"] = champ_df["Probability"].apply(
                        lambda x: f"{float(x):.1%}"
                    )
                    cx1, cx2 = st.columns([2, 3])
                    with cx1:
                        render_champion_spotlight(top_champion, top_champ_prob)
                    with cx2:
                        st.dataframe(champ_df, use_container_width=True, hide_index=True)
        except Exception:
            render_champion_spotlight(top_champion, top_champ_prob)

        st.markdown("<br>", unsafe_allow_html=True)

    # Readiness progress
    render_section_header("Data readiness")
    progress_ratio = checks_passed / max(checks_total, 1)
    prog_kind = "ok" if is_final_ready else ("warn" if progress_ratio >= 0.5 else "danger")
    render_progress_bar(
        progress_ratio,
        label=f"Official data completeness — {checks_passed}/{checks_total} checks",
        kind=prog_kind,
    )
    if is_final_ready:
        render_success_panel(
            "All readiness checks passed. Official final mode is enabled for production analytics."
        )
    else:
        blockers = len(readiness.get("blockers", []))
        warnings_count = len(readiness.get("warnings", []))
        parts = []
        if blockers:
            parts.append(f"{blockers} blocker{'s' if blockers > 1 else ''}")
        if warnings_count:
            parts.append(f"{warnings_count} warning{'s' if warnings_count > 1 else ''}")
        msg = ", ".join(parts) or "data incomplete"
        render_warning_panel(
            f"Official final mode is blocked — {msg}. "
            "Use the <strong>Data Health</strong> page to resolve issues."
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # About
    render_section_header("About")
    st.markdown(
        f"""
<div class="wc-card" style="padding:1.25rem 1.5rem;">
  <div class="wc-card-value" style="font-size:1rem;font-weight:600;margin-bottom:0.5rem;">
    FIFA World Cup 2026 AI Predictor
  </div>
  <div class="wc-card-sub" style="font-size:0.9rem;line-height:1.65;">
    This dashboard uses machine learning models trained on historical international match data,
    FIFA and Elo rankings, and official World Cup 2026 squad information to produce
    probabilistic forecasts for match outcomes, tournament progression, and player awards.<br><br>
    All outputs are <strong style="color:{COLORS['warning']}">analytics estimates</strong>
    — not official FIFA predictions. Probabilities reflect model uncertainty across
    many simulated scenarios.
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Analytics estimates only. Not affiliated with or endorsed by FIFA.")


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
