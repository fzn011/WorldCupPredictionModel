"""Streamlit page for Step 14 full tournament single-run orchestration."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.simulation.prepare_full_tournament import prepare_step14_full_tournament_single_run  # noqa: E402
import src.utils.constants as C  # noqa: E402

PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")
FULL_TOURNAMENT_SIMULATED_MATCHES_FILE = getattr(C, "FULL_TOURNAMENT_SIMULATED_MATCHES_FILE", "full_tournament_simulated_matches.csv")
FULL_TOURNAMENT_GROUP_TABLES_FILE = getattr(C, "FULL_TOURNAMENT_GROUP_TABLES_FILE", "full_tournament_group_tables.csv")
FULL_TOURNAMENT_KNOCKOUT_MATCHES_FILE = getattr(C, "FULL_TOURNAMENT_KNOCKOUT_MATCHES_FILE", "full_tournament_knockout_matches.csv")
FULL_TOURNAMENT_STAGE_RESULTS_FILE = getattr(C, "FULL_TOURNAMENT_STAGE_RESULTS_FILE", "full_tournament_stage_results.csv")
FULL_TOURNAMENT_PATH_REPORT_FILE = getattr(C, "FULL_TOURNAMENT_PATH_REPORT_FILE", "full_tournament_path_report.csv")
FULL_TOURNAMENT_RESULT_FILE = getattr(C, "FULL_TOURNAMENT_RESULT_FILE", "single_world_cup_result.json")
FULL_TOURNAMENT_SUMMARY_FILE = getattr(C, "FULL_TOURNAMENT_SUMMARY_FILE", "full_tournament_summary.json")
FULL_TOURNAMENT_VALIDATION_REPORT_FILE = getattr(C, "FULL_TOURNAMENT_VALIDATION_REPORT_FILE", "full_tournament_validation_report.csv")

st.title("Full Tournament Single-Run")
st.caption("Step 14 runs one full sampled tournament path from group stage through final. This is not Monte Carlo.")

st.subheader("Overview")
st.markdown(
    "- Runs group-stage simulation and builds group tables\n"
    "- Selects Round-of-32 qualifiers and simulates knockout rounds\n"
    "- Produces champion, runner-up, third place, and fourth place\n"
    "- Saves full match log, stage results, team path report, and validation report\n"
    "- Does **not** produce champion probabilities yet"
)

seed = int(st.number_input("Simulation seed", min_value=0, max_value=1_000_000, value=42, step=1))
if st.button("Run full tournament single-run"):
    summary = prepare_step14_full_tournament_single_run(random_seed=seed)
    if summary.get("validation_passed"):
        st.success("Full tournament simulation completed successfully.")
    else:
        st.warning("Full tournament simulation finished with validation issues.")
    st.json(summary)


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


summary = _load_json(FULL_TOURNAMENT_SUMMARY_FILE)
st.subheader("Latest summary")
if summary:
    st.json(summary)
    st.metric("Champion", summary.get("champion", "—"))
    cols = st.columns(3)
    cols[0].metric("Runner-up", summary.get("runner_up", "—"))
    cols[1].metric("Third place", summary.get("third_place", "—"))
    cols[2].metric("Fourth place", summary.get("fourth_place", "—"))
else:
    st.info("No full tournament summary found yet.")

stage_results_df = _load_csv(FULL_TOURNAMENT_STAGE_RESULTS_FILE)
if not stage_results_df.empty:
    st.subheader("Stage results")
    st.dataframe(stage_results_df, use_container_width=True)

full_group_tables_df = _load_csv(FULL_TOURNAMENT_GROUP_TABLES_FILE)
if not full_group_tables_df.empty:
    st.subheader("Group tables")
    st.dataframe(full_group_tables_df, use_container_width=True)

knockout_matches_df = _load_csv(FULL_TOURNAMENT_KNOCKOUT_MATCHES_FILE)
if not knockout_matches_df.empty:
    st.subheader("Knockout matches")
    st.dataframe(knockout_matches_df, use_container_width=True)

path_report_df = _load_csv(FULL_TOURNAMENT_PATH_REPORT_FILE)
if not path_report_df.empty:
    st.subheader("Tournament path report")
    st.dataframe(path_report_df, use_container_width=True)

validation_df = _load_csv(FULL_TOURNAMENT_VALIDATION_REPORT_FILE)
if not validation_df.empty:
    st.subheader("Validation report")
    st.dataframe(validation_df, use_container_width=True)

single_result = _load_json(FULL_TOURNAMENT_RESULT_FILE)
if single_result:
    st.subheader("Single World Cup result")
    st.json(single_result)

full_match_log_df = _load_csv(FULL_TOURNAMENT_SIMULATED_MATCHES_FILE)
if not full_match_log_df.empty:
    st.subheader("Full match log")
    st.dataframe(full_match_log_df, use_container_width=True)

st.subheader("Downloads")
for file_name, label, mime in [
    (FULL_TOURNAMENT_SIMULATED_MATCHES_FILE, "Download full tournament match log CSV", "text/csv"),
    (FULL_TOURNAMENT_GROUP_TABLES_FILE, "Download full tournament group tables CSV", "text/csv"),
    (FULL_TOURNAMENT_KNOCKOUT_MATCHES_FILE, "Download full tournament knockout matches CSV", "text/csv"),
    (FULL_TOURNAMENT_STAGE_RESULTS_FILE, "Download stage results CSV", "text/csv"),
    (FULL_TOURNAMENT_PATH_REPORT_FILE, "Download tournament path report CSV", "text/csv"),
    (FULL_TOURNAMENT_RESULT_FILE, "Download single world cup result JSON", "application/json"),
    (FULL_TOURNAMENT_SUMMARY_FILE, "Download full tournament summary JSON", "application/json"),
    (FULL_TOURNAMENT_VALIDATION_REPORT_FILE, "Download full tournament validation CSV", "text/csv"),
]:
    path = PROCESSED_DATA_DIR / file_name
    if path.is_file():
        st.download_button(label=label, data=path.read_bytes(), file_name=file_name, mime=mime)

st.caption("This output is one sampled path only. Monte Carlo and probability dashboards are planned for Step 15.")
