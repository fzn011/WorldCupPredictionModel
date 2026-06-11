"""Streamlit page: FIFA World Cup 2026 Awards Predictor."""

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
    from app.streamlit_paths import OFFICIAL_PROCESSED_DIR, PROCESSED_DATA_DIR, PROJECT_ROOT, REPORTS_DIR
except ModuleNotFoundError:
    from streamlit_paths import OFFICIAL_PROCESSED_DIR, PROCESSED_DATA_DIR, PROJECT_ROOT, REPORTS_DIR

try:
    from app.components.ui import (
        inject_page_theme,
        render_data_table,
        render_download_card,
        render_formation_diagram,
        render_hero,
        render_info_panel,
        render_metric_card,
        render_podium_cards,
        render_section_header,
        render_status_card,
        render_success_panel,
        render_warning_panel,
    )
except ModuleNotFoundError:
    from components.ui import (
        inject_page_theme,
        render_data_table,
        render_download_card,
        render_formation_diagram,
        render_hero,
        render_info_panel,
        render_metric_card,
        render_podium_cards,
        render_section_header,
        render_status_card,
        render_success_panel,
        render_warning_panel,
    )

from src.awards.award_data import resolve_player_sort_column  # noqa: E402
from src.awards.manual_priors import resolve_manual_prior_file  # noqa: E402
from src.awards.prior_enrichment import create_enriched_player_priors, merge_enriched_priors_into_award_candidates  # noqa: E402
from src.awards.prepare_awards import prepare_step18_world_cup_awards  # noqa: E402
from src.official.final_readiness import evaluate_official_final_readiness  # noqa: E402
from src.official.promotion import load_official_final_mode  # noqa: E402
import src.utils.constants as C  # noqa: E402

AWARDS_ANALYTICS_DISCLAIMER = str(getattr(C, "AWARDS_ANALYTICS_DISCLAIMER", "Analytics estimate only."))
MANUAL_PRIOR_DISCLAIMER = str(getattr(C, "MANUAL_PRIOR_DISCLAIMER", "Manual priors are optional user-provided adjustments."))

MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE = getattr(
    C, "MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE", "monte_carlo_team_stage_probabilities.csv"
)
WORLD_CUP_AWARDS_PREDICTIONS_FILE = getattr(C, "WORLD_CUP_AWARDS_PREDICTIONS_FILE", "world_cup_awards_predictions.csv")
GOLDEN_BALL_PREDICTIONS_FILE = getattr(C, "GOLDEN_BALL_PREDICTIONS_FILE", "golden_ball_predictions.csv")
GOLDEN_BOOT_PREDICTIONS_FILE = getattr(C, "GOLDEN_BOOT_PREDICTIONS_FILE", "golden_boot_predictions.csv")
GOLDEN_GLOVE_PREDICTIONS_FILE = getattr(C, "GOLDEN_GLOVE_PREDICTIONS_FILE", "golden_glove_predictions.csv")
YOUNG_PLAYER_PREDICTIONS_FILE = getattr(C, "YOUNG_PLAYER_PREDICTIONS_FILE", "young_player_predictions.csv")
FAIR_PLAY_PREDICTIONS_FILE = getattr(C, "FAIR_PLAY_PREDICTIONS_FILE", "fair_play_predictions.csv")
MOST_ENTERTAINING_TEAM_PREDICTIONS_FILE = getattr(
    C, "MOST_ENTERTAINING_TEAM_PREDICTIONS_FILE", "most_entertaining_team_predictions.csv"
)
TEAM_OF_THE_TOURNAMENT_FILE = getattr(C, "TEAM_OF_THE_TOURNAMENT_FILE", "team_of_the_tournament.csv")
PLAYER_OF_THE_MATCH_PROXY_FILE = getattr(C, "PLAYER_OF_THE_MATCH_PROXY_FILE", "player_of_the_match_proxy.csv")
GOAL_OF_THE_TOURNAMENT_PROXY_FILE = getattr(
    C, "GOAL_OF_THE_TOURNAMENT_PROXY_FILE", "goal_of_the_tournament_proxy.csv"
)
WORLD_CUP_AWARDS_SUMMARY_FILE = getattr(C, "WORLD_CUP_AWARDS_SUMMARY_FILE", "world_cup_awards_summary.json")
WORLD_CUP_AWARDS_VALIDATION_REPORT_FILE = getattr(
    C, "WORLD_CUP_AWARDS_VALIDATION_REPORT_FILE", "world_cup_awards_validation_report.csv"
)
WORLD_CUP_AWARDS_REPORT_FILE = getattr(C, "WORLD_CUP_AWARDS_REPORT_FILE", "world_cup_awards_report.md")


def _load_csv(file_name: str) -> pd.DataFrame:
    path = PROCESSED_DATA_DIR / file_name
    return pd.read_csv(path) if path.is_file() else pd.DataFrame()


def _load_json(file_name: str) -> dict:
    path = PROCESSED_DATA_DIR / file_name
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _player_col(df: pd.DataFrame) -> str:
    if df.empty:
        return "player_name"
    try:
        return resolve_player_sort_column(df)
    except KeyError:
        return "player_name"


def _formation_lines(team_df: pd.DataFrame, name_col: str) -> list[list[str]]:
    """Build 4-3-3 display rows (forwards at top, GK at bottom)."""
    if team_df.empty or "formation_slot" not in team_df.columns:
        return []
    slot_map = {
        row["formation_slot"]: str(row.get(name_col, "—"))
        for _, row in team_df.iterrows()
    }

    def _line(prefix: str, count: int) -> list[str]:
        return [slot_map.get(f"{prefix}{i}", "—") for i in range(1, count + 1)]

    return [
        _line("FWD", 3),
        _line("MID", 3),
        _line("DEF", 4),
        _line("GK", 1),
    ]


inject_page_theme()
render_hero(
    "World Cup Awards Forecast",
    "Analytics-based estimates using official squads and tournament simulations.",
    eyebrow="Awards analytics",
)

render_info_panel(AWARDS_ANALYTICS_DISCLAIMER)

final_mode = load_official_final_mode()
readiness = evaluate_official_final_readiness()
official_final_enabled = bool(final_mode.get("official_final_enabled", False))
final_ready = bool(readiness.get("is_official_final_ready", False))
awards_allowed = official_final_enabled and final_ready
summary = readiness.get("summary", {})

if final_ready and official_final_enabled:
    render_success_panel("Official data verified. Awards forecasts are enabled.")
else:
    render_info_panel("Awards require verified official data. Review the Data Quality page for status.")

render_section_header("Dataset status")
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_status_card(
        "Official Data",
        "Ready" if official_final_enabled else "Pending",
        badge="ok" if official_final_enabled else "warn",
    )
with c2:
    render_status_card(
        "Verification",
        "Complete" if final_ready else "In progress",
        badge="ok" if final_ready else "warn",
    )
with c3:
    render_metric_card("Players", str(summary.get("players_count", "—")))
with c4:
    render_metric_card("Full squads", str(summary.get("teams_with_26_players", "—")))

if not awards_allowed:
    with st.expander("Technical requirements (admin)"):
        st.markdown(
            "Awards generation requires verified official data. "
            "Enable technical tools in the sidebar for admin workflows."
        )
    st.stop()

enriched_path = PROCESSED_DATA_DIR / getattr(C, "ENRICHED_OFFICIAL_AWARD_CANDIDATES_FILE", "enriched_official_award_candidates.csv")
quality_path = PROCESSED_DATA_DIR / getattr(C, "PLAYER_PRIOR_QUALITY_REPORT_FILE", "player_prior_quality_report.csv")
summary_pre = _load_json(WORLD_CUP_AWARDS_SUMMARY_FILE)
candidate_source = summary_pre.get("candidate_source") or (
    getattr(C, "ENRICHED_OFFICIAL_AWARD_CANDIDATES_FILE", "enriched_official_award_candidates.csv")
    if enriched_path.is_file()
    else getattr(C, "OFFICIAL_AWARD_CANDIDATES_FILE", "official_award_candidates.csv")
)

tab_overview, tab_awards, tab_tools, tab_downloads = st.tabs(
    ["Overview", "Award categories", "Priors & generation", "Downloads"]
)

monte_carlo_path = PROCESSED_DATA_DIR / MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE

with tab_tools:
    render_section_header("Prior enrichment")
    st.caption(
        "Player priors are heuristic position/role estimates unless you manually edit "
        "`player_award_priors.csv`. Enrichment improves differentiation for demo outputs."
    )
    p1, p2 = st.columns(2)
    with p1:
        render_metric_card("Candidate source", str(candidate_source))
    with p2:
        if quality_path.is_file():
            qdf = pd.read_csv(quality_path)
            flat_row = qdf[qdf["metric"] == "flatness_score"]
            flat_val = flat_row.iloc[0]["value"] if not flat_row.empty else "—"
            render_metric_card("Prior flatness score", str(flat_val))
        else:
            render_metric_card("Prior flatness score", "—")

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        if st.button("Enrich player priors", use_container_width=True):
            try:
                enrich_summary = create_enriched_player_priors()
                merge_enriched_priors_into_award_candidates(update_official=False)
                render_success_panel(f"Enriched {enrich_summary.get('candidate_count')} candidates.")
                st.json(enrich_summary)
            except Exception as exc:
                st.error(str(exc))
    with col_e2:
        if st.button("Regenerate awards (enriched priors)", use_container_width=True):
            try:
                if not enriched_path.is_file():
                    create_enriched_player_priors()
                    merge_enriched_priors_into_award_candidates(update_official=False)
                result = prepare_step18_world_cup_awards(use_enriched_candidates=True)
                render_success_panel("Awards regenerated with enriched candidates.")
                st.json(result)
            except Exception as exc:
                st.error(str(exc))

    render_section_header("Manual star-player priors")
    st.caption(MANUAL_PRIOR_DISCLAIMER)
    prior_mode = "official candidates only"
    if enriched_path.is_file() and "manual" in str(summary_pre.get("candidate_source", "")).lower():
        prior_mode = "enriched + manual priors"
    elif enriched_path.is_file():
        prior_mode = "enriched priors"
    elif summary_pre.get("use_manual_priors"):
        prior_mode = "official + manual priors"
    render_metric_card("Prior mode", prior_mode)

    manual_summary_path = PROCESSED_DATA_DIR / getattr(C, "MANUAL_PRIOR_SUMMARY_FILE", "manual_prior_summary.json")
    manual_report_path = PROCESSED_DATA_DIR / getattr(C, "MANUAL_PRIOR_VALIDATION_REPORT_FILE", "manual_prior_validation_report.csv")
    if manual_summary_path.is_file():
        manual_summary = _load_json(getattr(C, "MANUAL_PRIOR_SUMMARY_FILE", "manual_prior_summary.json"))
        st.caption(
            f"Manual overrides applied: {manual_summary.get('overrides_applied', 0)} | "
            f"Unmatched ignored: {manual_summary.get('unmatched_manual_rows_ignored', 0)}"
        )
    if manual_report_path.is_file():
        manual_report_df = pd.read_csv(manual_report_path)
        boost_rows = manual_report_df[manual_report_df.get("section", pd.Series(dtype=str)) == "applied_boost"]
        movement_rows = manual_report_df[manual_report_df.get("section", pd.Series(dtype=str)) == "rank_movement"]
        with st.expander("Manual boosts applied (sample)", expanded=False):
            if not boost_rows.empty:
                render_data_table(boost_rows[["player_name", "team", "boost_column", "boost_value"]].head(20))
            else:
                st.info("No manual boosts recorded.")
        with st.expander("Ranking movement (manual overrides)", expanded=False):
            if not movement_rows.empty:
                render_data_table(
                    movement_rows[
                        ["award", "player_name", "team", "rank_before", "rank_after", "rank_movement"]
                    ].head(20)
                )
            else:
                st.info("No rank movement recorded.")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        if st.button("Generate awards (enriched + manual demo priors)", use_container_width=True):
            try:
                demo_path = resolve_manual_prior_file(None)
                if not enriched_path.is_file():
                    create_enriched_player_priors()
                    merge_enriched_priors_into_award_candidates(update_official=False)
                result = prepare_step18_world_cup_awards(
                    use_enriched_candidates=True,
                    use_manual_priors=True,
                    manual_prior_file=demo_path,
                )
                render_success_panel("Awards regenerated with enriched + manual demo priors.")
                st.json(result)
            except Exception as exc:
                st.error(str(exc))
    with col_m2:
        st.caption(
            "Edit `data/templates/player_award_manual_priors_demo.csv` or export a full template via "
            "`python scripts/export_player_award_prior_template.py`."
        )

    render_section_header("Generate predictions")
    if not monte_carlo_path.is_file():
        st.info("Monte Carlo team stage probabilities are required before generating awards outputs.")
        st.code("python scripts/run_monte_carlo.py --simulations 10 --seed 42")
    col_gen, col_refresh = st.columns(2)
    with col_gen:
        generate_clicked = st.button("Generate awards predictions", type="primary", use_container_width=True)
    with col_refresh:
        refresh_clicked = st.button("Refresh outputs", use_container_width=True)

    if generate_clicked:
        try:
            result = prepare_step18_world_cup_awards()
            render_success_panel("World Cup awards artifacts generated successfully.")
            st.json(result)
        except (RuntimeError, FileNotFoundError, ValueError) as exc:
            st.error(str(exc))

    if refresh_clicked:
        st.rerun()

# Load outputs (shared across tabs)
summary = _load_json(WORLD_CUP_AWARDS_SUMMARY_FILE)
golden_ball_df = _load_csv(GOLDEN_BALL_PREDICTIONS_FILE)
golden_boot_df = _load_csv(GOLDEN_BOOT_PREDICTIONS_FILE)
golden_glove_df = _load_csv(GOLDEN_GLOVE_PREDICTIONS_FILE)
young_player_df = _load_csv(YOUNG_PLAYER_PREDICTIONS_FILE)
fair_play_df = _load_csv(FAIR_PLAY_PREDICTIONS_FILE)
entertaining_df = _load_csv(MOST_ENTERTAINING_TEAM_PREDICTIONS_FILE)
team_of_tournament_df = _load_csv(TEAM_OF_THE_TOURNAMENT_FILE)
potm_proxy_df = _load_csv(PLAYER_OF_THE_MATCH_PROXY_FILE)
got_proxy_df = _load_csv(GOAL_OF_THE_TOURNAMENT_PROXY_FILE)
validation_df = _load_csv(WORLD_CUP_AWARDS_VALIDATION_REPORT_FILE)
report_path = REPORTS_DIR / WORLD_CUP_AWARDS_REPORT_FILE
player_col = _player_col(golden_ball_df) or "player_name"

with tab_overview:
    render_section_header("Summary")
    if summary:
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        with m1:
            render_metric_card("Golden Ball", str(summary.get("top_golden_ball_player", "—")))
        with m2:
            render_metric_card("Golden Boot", str(summary.get("top_golden_boot_player", "—")))
        with m3:
            render_metric_card("Golden Glove", str(summary.get("top_golden_glove_player", "—")))
        with m4:
            render_metric_card("Young Player", str(summary.get("top_young_player", "—")))
        with m5:
            render_metric_card("Fair Play", str(summary.get("top_fair_play_team", "—")))
        with m6:
            render_metric_card("Entertaining Team", str(summary.get("top_entertaining_team", "—")))
        badge = "ok" if summary.get("validation_passed") else "danger"
        render_status_card(
            "Validation",
            "Passed" if summary.get("validation_passed") else "Failed",
            sub=f"Team of Tournament: {summary.get('team_of_tournament_count', '—')} players",
            badge=badge,
        )
    else:
        st.info("No awards summary found yet. Generate awards predictions on the Priors & generation tab.")

    render_section_header("Award coverage")
    st.markdown(
        "- Golden Ball / Silver Ball / Bronze Ball\n"
        "- Golden Boot / Silver Boot / Bronze Boot\n"
        "- Golden Glove · Young Player · Fair Play · Most Entertaining Team\n"
        "- Predicted Team of the Tournament (4-3-3 analytics XI)\n"
        "- Player of the Match and Goal of the Tournament proxies\n\n"
        "Uses **official_award_candidates.csv** only — no sample players."
    )

    with st.expander("Methodology & limitations", expanded=False):
        st.markdown(
            "**Methodology**\n"
            "- Official squads from `official_award_candidates.csv` with editable player priors\n"
            "- Monte Carlo team progression from `monte_carlo_team_stage_probabilities.csv`\n"
            "- Team profiles for fair-play and entertainment estimates\n"
            "- Team of the Tournament uses a 4-3-3 analytics selection\n\n"
            "**Limitations**\n"
            "- Explainable analytics estimates, not official FIFA predictions\n"
            "- Depends on Monte Carlo sample size and editable player priors\n"
            "- Fan-voted awards are proxy estimates only\n"
            "- No match-level player event simulation · Not betting advice"
        )

    with st.expander("Validation report", expanded=False):
        render_data_table(validation_df)

with tab_awards:
    render_section_header("Golden Ball podium")
    if not golden_ball_df.empty and "golden_ball_rank" in golden_ball_df.columns:
        render_podium_cards(
            golden_ball_df,
            rank_col="golden_ball_rank",
            name_col=player_col,
            score_col="golden_ball_probability" if "golden_ball_probability" in golden_ball_df.columns else None,
            award_labels={1: "Golden Ball", 2: "Silver Ball", 3: "Bronze Ball"},
        )
        with st.expander("Full Golden Ball table"):
            cols = [
                c
                for c in ["golden_ball_rank", player_col, "team", "position", "golden_ball_probability", "award"]
                if c in golden_ball_df.columns
            ]
            render_data_table(golden_ball_df[cols].head(15))
    else:
        st.info("No Golden Ball output available.")

    render_section_header("Golden Boot race")
    if not golden_boot_df.empty:
        render_podium_cards(
            golden_boot_df,
            rank_col="golden_boot_rank",
            name_col=player_col,
            score_col="golden_boot_probability" if "golden_boot_probability" in golden_boot_df.columns else "expected_goals",
            award_labels={1: "Golden Boot", 2: "Silver Boot", 3: "Bronze Boot"},
        )
        with st.expander("Full Golden Boot table"):
            cols = [
                c
                for c in ["golden_boot_rank", player_col, "team", "position", "expected_goals", "golden_boot_probability", "award"]
                if c in golden_boot_df.columns
            ]
            render_data_table(golden_boot_df[cols].head(15))
    else:
        st.info("No Golden Boot output available.")

    g1, g2 = st.columns(2)
    with g1:
        render_section_header("Golden Glove")
        if not golden_glove_df.empty:
            top = golden_glove_df.sort_values("golden_glove_rank").head(1).iloc[0]
            render_metric_card(
                "Leader",
                str(top.get(player_col, "—")),
                sub=f"{top.get('team', '')} · {float(top.get('golden_glove_probability', 0)):.1%}"
                if "golden_glove_probability" in top
                else str(top.get("team", "")),
            )
            with st.expander("Golden Glove table"):
                cols = [c for c in ["golden_glove_rank", player_col, "team", "golden_glove_probability", "award"] if c in golden_glove_df.columns]
                render_data_table(golden_glove_df[cols].head(10))
        else:
            st.info("No Golden Glove output available.")
    with g2:
        render_section_header("Young Player")
        if not young_player_df.empty:
            top = young_player_df.sort_values("young_player_rank").head(1).iloc[0]
            render_metric_card(
                "Leader",
                str(top.get(player_col, "—")),
                sub=f"{top.get('team', '')} · {float(top.get('young_player_probability', 0)):.1%}"
                if "young_player_probability" in top
                else str(top.get("team", "")),
            )
            with st.expander("Young Player table"):
                cols = [
                    c
                    for c in ["young_player_rank", player_col, "team", "position", "young_player_probability", "award"]
                    if c in young_player_df.columns
                ]
                render_data_table(young_player_df[cols].head(10))
        else:
            st.info("No Young Player output available.")

    t1, t2 = st.columns(2)
    with t1:
        render_section_header("Fair Play Trophy")
        if not fair_play_df.empty:
            top = fair_play_df.sort_values("fair_play_rank").head(1).iloc[0]
            render_metric_card("Leader", str(top.get("team", "—")))
            with st.expander("Fair Play table"):
                cols = [c for c in ["fair_play_rank", "team", "fair_play_probability", "award"] if c in fair_play_df.columns]
                render_data_table(fair_play_df[cols].head(10))
        else:
            st.info("No Fair Play output available.")
    with t2:
        render_section_header("Most Entertaining Team")
        if not entertaining_df.empty:
            top = entertaining_df.sort_values("most_entertaining_rank").head(1).iloc[0]
            render_metric_card("Leader", str(top.get("team", "—")))
            with st.expander("Entertaining team table"):
                cols = [
                    c
                    for c in ["most_entertaining_rank", "team", "most_entertaining_probability", "award"]
                    if c in entertaining_df.columns
                ]
                render_data_table(entertaining_df[cols].head(10))
        else:
            st.info("No Most Entertaining Team output available.")

    render_section_header("Team of the Tournament — 4-3-3")
    if not team_of_tournament_df.empty:
        lines = _formation_lines(team_of_tournament_df, player_col)
        if lines:
            render_formation_diagram(lines)
        with st.expander("Team of the Tournament table"):
            cols = [
                c
                for c in ["formation_slot", player_col, "team", "position", "final_golden_ball_score"]
                if c in team_of_tournament_df.columns
            ]
            render_data_table(team_of_tournament_df[cols])
    else:
        st.info("No Team of the Tournament output available.")

    render_section_header("Proxy awards")
    p1, p2 = st.columns(2)
    with p1:
        st.caption("Player of the Match proxy")
        if not potm_proxy_df.empty:
            cols = [c for c in ["player_of_match_proxy_rank", player_col, "team", "estimated_potm_count"] if c in potm_proxy_df.columns]
            render_data_table(potm_proxy_df[cols].head(8))
        else:
            st.info("No Player of the Match proxy available.")
    with p2:
        st.caption("Goal of the Tournament proxy")
        if not got_proxy_df.empty:
            cols = [
                c
                for c in ["goal_of_tournament_proxy_rank", player_col, "team", "goal_of_tournament_proxy_probability"]
                if c in got_proxy_df.columns
            ]
            render_data_table(got_proxy_df[cols].head(8))
        else:
            st.info("No Goal of the Tournament proxy available.")

with tab_downloads:
    render_section_header("Export artifacts")
    d1, d2 = st.columns(2)
    download_files = [
        (WORLD_CUP_AWARDS_PREDICTIONS_FILE, "Combined awards predictions"),
        (GOLDEN_BALL_PREDICTIONS_FILE, "Golden Ball rankings"),
        (GOLDEN_BOOT_PREDICTIONS_FILE, "Golden Boot rankings"),
        (GOLDEN_GLOVE_PREDICTIONS_FILE, "Golden Glove rankings"),
        (TEAM_OF_THE_TOURNAMENT_FILE, "Team of the Tournament XI"),
    ]
    for idx, (file_name, desc) in enumerate(download_files):
        col = d1 if idx % 2 == 0 else d2
        with col:
            render_download_card(desc, file_name, PROCESSED_DATA_DIR / file_name)
    render_download_card(
        "Awards narrative report",
        WORLD_CUP_AWARDS_REPORT_FILE,
        report_path,
        mime="text/markdown",
    )
