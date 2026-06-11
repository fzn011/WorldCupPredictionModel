"""Streamlit page: Knockout simulation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

for _path in (Path(__file__).resolve().parents[2], Path(__file__).resolve().parents[1]):
    _entry = str(_path)
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

from app.page_bootstrap import begin_themed_page, setup_streamlit_paths
from app.components.ui import render_hero, render_metric_card, render_section_header

ROOT, _ = setup_streamlit_paths(__file__)

from src.simulation.prepare_knockout import prepare_step13_knockout_simulation  # noqa: E402
import src.utils.constants as C  # noqa: E402

PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")
KNOCKOUT_BRACKET_FILLED_FILE = getattr(C, "KNOCKOUT_BRACKET_FILLED_FILE", "knockout_bracket_filled.csv")
KNOCKOUT_SIMULATED_MATCHES_FILE = getattr(C, "KNOCKOUT_SIMULATED_MATCHES_FILE", "knockout_simulated_matches.csv")
SINGLE_TOURNAMENT_RESULT_FILE = getattr(C, "SINGLE_TOURNAMENT_RESULT_FILE", "single_tournament_result.json")
KNOCKOUT_SIMULATION_SUMMARY_FILE = getattr(C, "KNOCKOUT_SIMULATION_SUMMARY_FILE", "knockout_simulation_summary.json")
KNOCKOUT_SIMULATION_VALIDATION_REPORT_FILE = getattr(
    C,
    "KNOCKOUT_SIMULATION_VALIDATION_REPORT_FILE",
    "knockout_simulation_validation_report.csv",
)

def render_page() -> None:
    render_hero(
        "Knockout Simulation",
        "Simulate one full knockout bracket from Round of 32 through the final.",
        eyebrow="Knockout stage",
    )

    render_section_header("Overview")
    st.markdown(
        "- Consumes the 32 Round-of-32 qualifiers from group stage\n"
        "- Fills a deterministic simulation seed-order bracket\n"
        "- Simulates Round of 32 through the Final\n"
        "- Uses no-draw adjusted probabilities for winner selection\n"
        "- Produces champion, runner-up, third place, and fourth place for one run"
    )

    seed = int(st.number_input("Simulation seed", min_value=0, max_value=1_000_000, value=42, step=1))

    if st.button("Run knockout simulation", type="primary"):
        summary = prepare_step13_knockout_simulation(random_seed=seed)
        if summary.get("validation_passed"):
            st.success("Knockout simulation completed successfully.")
        else:
            st.warning("Knockout simulation finished with validation issues.")
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


    summary = _load_json(KNOCKOUT_SIMULATION_SUMMARY_FILE)
    if summary:
        render_section_header("Latest summary")
        st.json(summary)
        render_metric_card("Champion", str(summary.get("champion", "—")), variant="accent")
        cols = st.columns(3)
        with cols[0]:
            render_metric_card("Runner-up", str(summary.get("runner_up", "—")))
        with cols[1]:
            render_metric_card("Third place", str(summary.get("third_place", "—")))
        with cols[2]:
            render_metric_card("Fourth place", str(summary.get("fourth_place", "—")))

    bracket_df = _load_csv(KNOCKOUT_BRACKET_FILLED_FILE)
    matches_df = _load_csv(KNOCKOUT_SIMULATED_MATCHES_FILE)
    validation_df = _load_csv(KNOCKOUT_SIMULATION_VALIDATION_REPORT_FILE)
    single_result = _load_json(SINGLE_TOURNAMENT_RESULT_FILE)

    if not bracket_df.empty:
        render_section_header("Filled bracket")
        st.dataframe(bracket_df, use_container_width=True)

    if not matches_df.empty:
        render_section_header("Round-by-round results")
        for round_name in ["round_of_32", "round_of_16", "quarter_final", "semi_final", "third_place", "final"]:
            round_df = matches_df.loc[matches_df["round"] == round_name].copy()
            if round_df.empty:
                continue
            with st.expander(f"{round_name.replace('_', ' ').title()} ({len(round_df)} matches)", expanded=round_name in {"final", "semi_final"}):
                display_df = round_df[
                    [
                        col
                        for col in [
                            "match_id",
                            "team_a",
                            "team_b",
                            "simulated_team_a_score",
                            "simulated_team_b_score",
                            "outcome_method",
                            "winner",
                            "loser",
                        ]
                        if col in round_df.columns
                    ]
                ]
                st.dataframe(display_df, use_container_width=True)

    if not validation_df.empty:
        render_section_header("Validation report")
        st.dataframe(validation_df, use_container_width=True)

    if single_result:
        render_section_header("Single tournament result")
        st.json(single_result)

    render_section_header("Downloads")
    for file_name, label in [
        (KNOCKOUT_BRACKET_FILLED_FILE, "Download filled bracket CSV"),
        (KNOCKOUT_SIMULATED_MATCHES_FILE, "Download simulated matches CSV"),
        (SINGLE_TOURNAMENT_RESULT_FILE, "Download single tournament JSON"),
        (KNOCKOUT_SIMULATION_SUMMARY_FILE, "Download summary JSON"),
        (KNOCKOUT_SIMULATION_VALIDATION_REPORT_FILE, "Download validation report CSV"),
    ]:
        path = PROCESSED_DATA_DIR / file_name
        if path.is_file():
            data = path.read_bytes()
            st.download_button(label, data=data, file_name=file_name)

    st.caption("One simulated knockout path only — use Tournament Forecast for champion probabilities.")
