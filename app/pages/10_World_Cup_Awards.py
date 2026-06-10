"""Streamlit page for Step 17 FIFA World Cup Awards Predictor."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.awards.prepare_awards import prepare_step17_world_cup_awards  # noqa: E402
import src.utils.constants as C  # noqa: E402

PROJECT_ROOT = getattr(C, "PROJECT_ROOT", ROOT)
PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", PROJECT_ROOT / "data" / "processed")
REPORTS_DIR = PROJECT_ROOT / "reports"
AWARDS_ANALYTICS_DISCLAIMER = str(getattr(C, "AWARDS_ANALYTICS_DISCLAIMER", "Analytics estimate only."))

MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE = getattr(C, "MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE", "monte_carlo_team_stage_probabilities.csv")
WORLD_CUP_AWARDS_PREDICTIONS_FILE = getattr(C, "WORLD_CUP_AWARDS_PREDICTIONS_FILE", "world_cup_awards_predictions.csv")
GOLDEN_BALL_PREDICTIONS_FILE = getattr(C, "GOLDEN_BALL_PREDICTIONS_FILE", "golden_ball_predictions.csv")
GOLDEN_BOOT_PREDICTIONS_FILE = getattr(C, "GOLDEN_BOOT_PREDICTIONS_FILE", "golden_boot_predictions.csv")
GOLDEN_GLOVE_PREDICTIONS_FILE = getattr(C, "GOLDEN_GLOVE_PREDICTIONS_FILE", "golden_glove_predictions.csv")
YOUNG_PLAYER_PREDICTIONS_FILE = getattr(C, "YOUNG_PLAYER_PREDICTIONS_FILE", "young_player_predictions.csv")
FAIR_PLAY_PREDICTIONS_FILE = getattr(C, "FAIR_PLAY_PREDICTIONS_FILE", "fair_play_predictions.csv")
MOST_ENTERTAINING_TEAM_PREDICTIONS_FILE = getattr(C, "MOST_ENTERTAINING_TEAM_PREDICTIONS_FILE", "most_entertaining_team_predictions.csv")
TEAM_OF_THE_TOURNAMENT_FILE = getattr(C, "TEAM_OF_THE_TOURNAMENT_FILE", "team_of_the_tournament.csv")
PLAYER_OF_THE_MATCH_PROXY_FILE = getattr(C, "PLAYER_OF_THE_MATCH_PROXY_FILE", "player_of_the_match_proxy.csv")
GOAL_OF_THE_TOURNAMENT_PROXY_FILE = getattr(C, "GOAL_OF_THE_TOURNAMENT_PROXY_FILE", "goal_of_the_tournament_proxy.csv")
WORLD_CUP_AWARDS_SUMMARY_FILE = getattr(C, "WORLD_CUP_AWARDS_SUMMARY_FILE", "world_cup_awards_summary.json")
WORLD_CUP_AWARDS_VALIDATION_REPORT_FILE = getattr(C, "WORLD_CUP_AWARDS_VALIDATION_REPORT_FILE", "world_cup_awards_validation_report.csv")
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


st.title("FIFA World Cup Awards Predictor")
st.caption("Step 17: explainable analytics estimates for player and team awards.")

st.warning(AWARDS_ANALYTICS_DISCLAIMER)

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
    "- Goal of the Tournament proxy"
)

monte_carlo_path = PROCESSED_DATA_DIR / MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE
if not monte_carlo_path.is_file():
    st.info("Monte Carlo team stage probabilities are required before generating awards outputs.")
    st.code("python scripts/run_monte_carlo.py --simulations 10 --seed 42")

if st.button("Generate / refresh awards predictions"):
    try:
        summary = prepare_step17_world_cup_awards()
        st.success("World Cup awards artifacts generated successfully.")
        st.json(summary)
    except FileNotFoundError as exc:
        st.error(str(exc))

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

st.subheader("Summary cards")
if summary:
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Golden Ball", summary.get("top_golden_ball_player", "—"))
    c2.metric("Golden Boot", summary.get("top_golden_boot_player", "—"))
    c3.metric("Golden Glove", summary.get("top_golden_glove_player", "—"))
    c4.metric("Young Player", summary.get("top_young_player", "—"))
    c5.metric("Fair Play", summary.get("top_fair_play_team", "—"))
    c6.metric("Entertaining Team", summary.get("top_entertaining_team", "—"))
else:
    st.info("No awards summary found yet.")

st.subheader("Golden Ball podium")
if not golden_ball_df.empty:
    cols = [c for c in ["golden_ball_rank", "player", "team", "position", "golden_ball_probability", "award_podium"] if c in golden_ball_df.columns]
    st.dataframe(golden_ball_df[cols].head(10), use_container_width=True)
else:
    st.info("No Golden Ball output available.")

st.subheader("Golden Boot race")
if not golden_boot_df.empty:
    cols = [c for c in ["golden_boot_rank", "player", "team", "position", "expected_goals_score", "boot_podium"] if c in golden_boot_df.columns]
    st.dataframe(golden_boot_df[cols].head(10), use_container_width=True)
else:
    st.info("No Golden Boot output available.")

st.subheader("Golden Glove ranking")
if not golden_glove_df.empty:
    cols = [c for c in ["golden_glove_rank", "player", "team", "golden_glove_probability", "award"] if c in golden_glove_df.columns]
    st.dataframe(golden_glove_df[cols].head(10), use_container_width=True)
else:
    st.info("No Golden Glove output available.")

st.subheader("Young Player ranking")
if not young_player_df.empty:
    cols = [c for c in ["young_player_rank", "player", "team", "position", "young_player_probability", "award"] if c in young_player_df.columns]
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
    cols = [c for c in ["formation_slot", "player", "team", "position"] if c in team_of_tournament_df.columns]
    st.dataframe(team_of_tournament_df[cols], use_container_width=True)
else:
    st.info("No Team of the Tournament output available.")

st.subheader("Player of the Match proxy")
if not potm_proxy_df.empty:
    cols = [c for c in ["player_of_match_proxy_rank", "player", "team", "estimated_potm_count"] if c in potm_proxy_df.columns]
    st.dataframe(potm_proxy_df[cols].head(10), use_container_width=True)
else:
    st.info("No Player of the Match proxy output available.")

st.subheader("Goal of the Tournament proxy")
if not got_proxy_df.empty:
    cols = [c for c in ["goal_of_tournament_proxy_rank", "player", "team", "goal_of_tournament_proxy_probability"] if c in got_proxy_df.columns]
    st.dataframe(got_proxy_df[cols].head(10), use_container_width=True)
else:
    st.info("No Goal of the Tournament proxy output available.")

st.subheader("Methodology")
st.markdown(
    "- Editable player priors drive player-level award estimates\n"
    "- Editable team profiles drive fair-play and entertainment estimates\n"
    "- Monte Carlo progression probabilities influence late-tournament awards strongly\n"
    "- Team of the Tournament uses a 4-3-3 analytics selection\n"
    "- Player of the Match and Goal of the Tournament are proxy estimates only"
)

st.subheader("Limitations")
st.markdown(
    "- These are explainable analytics estimates, not official FIFA predictions\n"
    "- Sample players are not guaranteed final 2026 squads\n"
    "- No live scraping or player-event simulation is used\n"
    "- Fan-vote style awards are proxy outputs\n"
    "- Not betting advice"
)

st.subheader("Validation report")
if not validation_df.empty:
    st.dataframe(validation_df, use_container_width=True)
else:
    st.info("No validation report available.")

st.subheader("Downloads")
for file_name in [
    WORLD_CUP_AWARDS_PREDICTIONS_FILE,
    GOLDEN_BALL_PREDICTIONS_FILE,
    GOLDEN_BOOT_PREDICTIONS_FILE,
    TEAM_OF_THE_TOURNAMENT_FILE,
]:
    path = PROCESSED_DATA_DIR / file_name
    if path.is_file():
        st.download_button(label=f"Download {file_name}", data=path.read_bytes(), file_name=file_name, mime="text/csv")
if report_path.is_file():
    st.download_button(label="Download world_cup_awards_report.md", data=report_path.read_bytes(), file_name=WORLD_CUP_AWARDS_REPORT_FILE, mime="text/markdown")
