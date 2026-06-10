"""Streamlit page for Step 18 FIFA World Cup Awards Predictor."""

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

from src.awards.prior_enrichment import create_enriched_player_priors, merge_enriched_priors_into_award_candidates  # noqa: E402
from src.awards.prepare_awards import prepare_step18_world_cup_awards  # noqa: E402
from src.official.final_readiness import evaluate_official_final_readiness  # noqa: E402
from src.official.promotion import load_official_final_mode  # noqa: E402
import src.utils.constants as C  # noqa: E402
AWARDS_ANALYTICS_DISCLAIMER = str(getattr(C, "AWARDS_ANALYTICS_DISCLAIMER", "Analytics estimate only."))

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
    if "player_name" in df.columns:
        return "player_name"
    if "player" in df.columns:
        return "player"
    return ""


st.title("FIFA World Cup Awards Predictor")
st.caption("Step 18: explainable analytics estimates using official squads and Monte Carlo progression.")

st.warning(AWARDS_ANALYTICS_DISCLAIMER)

final_mode = load_official_final_mode()
readiness = evaluate_official_final_readiness()
official_final_enabled = bool(final_mode.get("official_final_enabled", False))
final_ready = bool(readiness.get("is_official_final_ready", False))
awards_allowed = official_final_enabled and final_ready

st.subheader("Official final data status")
c1, c2, c3, c4 = st.columns(4)
c1.metric("official_final_enabled", "Yes" if official_final_enabled else "No")
c2.metric("final_ready", "Yes" if final_ready else "No")
summary = readiness.get("summary", {})
c3.metric("Official players", summary.get("players_count", "—"))
c4.metric("Teams (26 players)", summary.get("teams_with_26_players", "—"))

if not awards_allowed:
    st.error(
        "World Cup awards require official_final mode. Run official final readiness and promotion first:\n\n"
        "```\npython scripts/evaluate_official_final_readiness.py\n"
        "python scripts/promote_official_final.py --confirm\n```"
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

st.subheader("Prior enrichment (Step 19)")
st.info(
    "Player priors are **heuristic position/role estimates** unless you manually edit "
    "`player_award_priors.csv`. Enrichment improves differentiation for demo/portfolio outputs."
)
st.metric("Candidate source", candidate_source)
if quality_path.is_file():
    qdf = pd.read_csv(quality_path)
    flat_row = qdf[qdf["metric"] == "flatness_score"]
    if not flat_row.empty:
        st.metric("Prior flatness score", flat_row.iloc[0]["value"])

col_e1, col_e2 = st.columns(2)
with col_e1:
    if st.button("Enrich player priors"):
        try:
            enrich_summary = create_enriched_player_priors()
            merge_enriched_priors_into_award_candidates(update_official=False)
            st.success(f"Enriched {enrich_summary.get('candidate_count')} candidates.")
            st.json(enrich_summary)
        except Exception as exc:
            st.error(str(exc))
with col_e2:
    if st.button("Regenerate awards (enriched priors)"):
        try:
            if not enriched_path.is_file():
                create_enriched_player_priors()
                merge_enriched_priors_into_award_candidates(update_official=False)
            result = prepare_step18_world_cup_awards(use_enriched_candidates=True)
            st.success("Awards regenerated with enriched candidates.")
            st.json(result)
        except Exception as exc:
            st.error(str(exc))

st.subheader("Overview")
st.markdown(
    "- Golden Ball / Silver Ball / Bronze Ball\n"
    "- Golden Boot / Silver Boot / Bronze Boot\n"
    "- Golden Glove\n"
    "- Young Player Award\n"
    "- Fair Play Trophy\n"
    "- Most Entertaining Team\n"
    "- Predicted Team of the Tournament\n"
    "- Player of the Match proxy\n"
    "- Goal of the Tournament proxy\n\n"
    "Uses **official_award_candidates.csv** only — no sample players."
)

monte_carlo_path = PROCESSED_DATA_DIR / MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE
if not monte_carlo_path.is_file():
    st.info("Monte Carlo team stage probabilities are required before generating awards outputs.")
    st.code("python scripts/run_monte_carlo.py --simulations 10 --seed 42")

col_gen, col_refresh = st.columns(2)
with col_gen:
    generate_clicked = st.button("Generate awards predictions", type="primary")
with col_refresh:
    refresh_clicked = st.button("Refresh outputs")

if generate_clicked:
    try:
        result = prepare_step18_world_cup_awards()
        st.success("World Cup awards artifacts generated successfully.")
        st.json(result)
    except (RuntimeError, FileNotFoundError, ValueError) as exc:
        st.error(str(exc))

if refresh_clicked:
    st.rerun()

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
player_col = _player_col(golden_ball_df) or "player"

st.subheader("Summary cards")
if summary:
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Golden Ball", summary.get("top_golden_ball_player", "—"))
    m2.metric("Golden Boot", summary.get("top_golden_boot_player", "—"))
    m3.metric("Golden Glove", summary.get("top_golden_glove_player", "—"))
    m4.metric("Young Player", summary.get("top_young_player", "—"))
    m5.metric("Fair Play", summary.get("top_fair_play_team", "—"))
    m6.metric("Entertaining Team", summary.get("top_entertaining_team", "—"))
    st.caption(
        f"Validation: {'passed' if summary.get('validation_passed') else 'failed'} | "
        f"Team of Tournament: {summary.get('team_of_tournament_count', '—')} players"
    )
else:
    st.info("No awards summary found yet. Generate awards predictions to populate outputs.")

st.subheader("Golden Ball podium")
if not golden_ball_df.empty:
    cols = [c for c in ["golden_ball_rank", player_col, "team", "position", "golden_ball_probability", "award"] if c in golden_ball_df.columns]
    st.dataframe(golden_ball_df[cols].head(10), use_container_width=True)
else:
    st.info("No Golden Ball output available.")

st.subheader("Golden Boot race")
if not golden_boot_df.empty:
    cols = [c for c in ["golden_boot_rank", player_col, "team", "position", "expected_goals", "golden_boot_probability", "award"] if c in golden_boot_df.columns]
    st.dataframe(golden_boot_df[cols].head(10), use_container_width=True)
else:
    st.info("No Golden Boot output available.")

st.subheader("Golden Glove ranking")
if not golden_glove_df.empty:
    cols = [c for c in ["golden_glove_rank", player_col, "team", "golden_glove_probability", "award"] if c in golden_glove_df.columns]
    st.dataframe(golden_glove_df[cols].head(10), use_container_width=True)
else:
    st.info("No Golden Glove output available.")

st.subheader("Young Player ranking")
if not young_player_df.empty:
    cols = [c for c in ["young_player_rank", player_col, "team", "position", "young_player_probability", "award"] if c in young_player_df.columns]
    st.dataframe(young_player_df[cols].head(10), use_container_width=True)
else:
    st.info("No Young Player output available.")

st.subheader("Fair Play Trophy ranking")
if not fair_play_df.empty:
    cols = [c for c in ["fair_play_rank", "team", "fair_play_probability", "award"] if c in fair_play_df.columns]
    st.dataframe(fair_play_df[cols].head(10), use_container_width=True)
else:
    st.info("No Fair Play output available.")

st.subheader("Most Entertaining Team ranking")
if not entertaining_df.empty:
    cols = [c for c in ["most_entertaining_rank", "team", "most_entertaining_probability", "award"] if c in entertaining_df.columns]
    st.dataframe(entertaining_df[cols].head(10), use_container_width=True)
else:
    st.info("No Most Entertaining Team output available.")

st.subheader("Predicted Team of the Tournament")
if not team_of_tournament_df.empty:
    cols = [c for c in ["formation_slot", player_col, "team", "position", "final_golden_ball_score"] if c in team_of_tournament_df.columns]
    st.dataframe(team_of_tournament_df[cols], use_container_width=True)
else:
    st.info("No Team of the Tournament output available.")

st.subheader("Player of the Match proxy")
if not potm_proxy_df.empty:
    cols = [c for c in ["player_of_match_proxy_rank", player_col, "team", "estimated_potm_count"] if c in potm_proxy_df.columns]
    st.dataframe(potm_proxy_df[cols].head(10), use_container_width=True)
else:
    st.info("No Player of the Match proxy output available.")

st.subheader("Goal of the Tournament proxy")
if not got_proxy_df.empty:
    cols = [c for c in ["goal_of_tournament_proxy_rank", player_col, "team", "goal_of_tournament_proxy_probability"] if c in got_proxy_df.columns]
    st.dataframe(got_proxy_df[cols].head(10), use_container_width=True)
else:
    st.info("No Goal of the Tournament proxy output available.")

st.subheader("Methodology")
st.markdown(
    "- Official squads from `official_award_candidates.csv` with editable player priors\n"
    "- Monte Carlo team progression probabilities from `monte_carlo_team_stage_probabilities.csv`\n"
    "- Team profiles for fair-play and entertainment estimates\n"
    "- Team of the Tournament uses a 4-3-3 analytics selection\n"
    "- Player of the Match and Goal of the Tournament are proxy estimates only"
)

st.subheader("Limitations")
st.markdown(
    "- These are explainable analytics estimates, not official FIFA predictions\n"
    "- Depends on Monte Carlo sample size and editable player priors\n"
    "- Fan-voted awards are proxy estimates\n"
    "- No match-level player event simulation\n"
    "- Not betting advice"
)

st.subheader("Validation report")
if not validation_df.empty:
    st.dataframe(validation_df, use_container_width=True)
else:
    st.info("No validation report available.")

st.subheader("Downloads")
download_files = [
    WORLD_CUP_AWARDS_PREDICTIONS_FILE,
    GOLDEN_BALL_PREDICTIONS_FILE,
    GOLDEN_BOOT_PREDICTIONS_FILE,
    GOLDEN_GLOVE_PREDICTIONS_FILE,
    TEAM_OF_THE_TOURNAMENT_FILE,
]
for file_name in download_files:
    path = PROCESSED_DATA_DIR / file_name
    if path.is_file():
        st.download_button(
            label=f"Download {file_name}",
            data=path.read_bytes(),
            file_name=file_name,
            mime="text/csv",
        )
if report_path.is_file():
    st.download_button(
        label="Download world_cup_awards_report.md",
        data=report_path.read_bytes(),
        file_name=WORLD_CUP_AWARDS_REPORT_FILE,
        mime="text/markdown",
    )
