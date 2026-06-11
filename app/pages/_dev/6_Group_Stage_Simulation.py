"""Streamlit page: Group-stage simulation."""

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

from app.page_bootstrap import begin_themed_page, safe_sort_dataframe, setup_streamlit_paths
from app.components.ui import render_section_header

ROOT, _ = setup_streamlit_paths(__file__)

from src.simulation.prepare_group_stage import prepare_step12_group_stage_simulation  # noqa: E402
import src.utils.constants as C  # noqa: E402

PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")
GROUP_STAGE_SIMULATED_MATCHES_FILE = getattr(C, "GROUP_STAGE_SIMULATED_MATCHES_FILE", "group_stage_simulated_matches.csv")
GROUP_STAGE_RANKINGS_FILE = getattr(C, "GROUP_STAGE_RANKINGS_FILE", "group_stage_rankings.csv")
BEST_THIRD_PLACED_TEAMS_FILE = getattr(C, "BEST_THIRD_PLACED_TEAMS_FILE", "best_third_placed_teams.csv")
ROUND_OF_32_QUALIFIERS_FILE = getattr(C, "ROUND_OF_32_QUALIFIERS_FILE", "round_of_32_qualifiers.csv")
GROUP_STAGE_SIMULATION_VALIDATION_REPORT_FILE = getattr(
    C, "GROUP_STAGE_SIMULATION_VALIDATION_REPORT_FILE", "group_stage_simulation_validation_report.csv"
)
GROUP_STAGE_SIMULATION_SUMMARY_FILE = getattr(C, "GROUP_STAGE_SIMULATION_SUMMARY_FILE", "group_stage_simulation_summary.json")

begin_themed_page(
    __file__,
    "Group Stage Simulation",
    "Simulates all 72 group-stage fixtures, builds tables, and selects Round-of-32 qualifiers.",
    eyebrow="Group stage",
)

render_section_header("Overview")
st.markdown(
    "- Uses existing match prediction engine per fixture\n"
    "- Samples outcomes from predicted probabilities\n"
    "- Applies transparent approximate scoreline templates\n"
    "- Builds group tables and selects Round-of-32 qualifiers\n"
    "- Does **not** simulate knockout rounds yet"
)

seed = int(st.number_input("Simulation seed", min_value=0, max_value=1_000_000, value=42, step=1))

if st.button("Run group-stage simulation", type="primary"):
    summary = prepare_step12_group_stage_simulation(random_seed=seed)
    if summary.get("status") == "ok":
        st.success("Group-stage simulation completed successfully.")
    else:
        st.warning("Group-stage simulation finished with validation issues.")
    st.json(summary)


def _load_csv(file_name: str) -> pd.DataFrame:
    path = PROCESSED_DATA_DIR / file_name
    if not path.is_file():
        return pd.DataFrame()
    return pd.read_csv(path)


def _load_summary() -> dict:
    path = PROCESSED_DATA_DIR / GROUP_STAGE_SIMULATION_SUMMARY_FILE
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


summary = _load_summary()
if summary:
    render_section_header("Validation summary")
    st.json(summary)

rankings_df = _load_csv(GROUP_STAGE_RANKINGS_FILE)
best_third_df = _load_csv(BEST_THIRD_PLACED_TEAMS_FILE)
qualifiers_df = _load_csv(ROUND_OF_32_QUALIFIERS_FILE)
simulated_df = _load_csv(GROUP_STAGE_SIMULATED_MATCHES_FILE)
validation_df = _load_csv(GROUP_STAGE_SIMULATION_VALIDATION_REPORT_FILE)

render_section_header("Group tables")
if rankings_df.empty:
    st.info("No group rankings found. Run simulation first.")
else:
    st.dataframe(safe_sort_dataframe(rankings_df, ["group", "group_rank"]), use_container_width=True)

render_section_header("Best third-placed teams")
if best_third_df.empty:
    st.info("No best-third table found yet.")
else:
    st.dataframe(best_third_df, use_container_width=True)

render_section_header("Round-of-32 qualifiers")
if qualifiers_df.empty:
    st.info("No qualifiers file found yet.")
else:
    st.dataframe(
        safe_sort_dataframe(qualifiers_df, ["qualification_type", "group", "group_rank", "team"]),
        use_container_width=True,
    )

render_section_header("Simulated match results")
if simulated_df.empty:
    st.info("No simulated match file found yet.")
else:
    st.dataframe(simulated_df, use_container_width=True)

render_section_header("Validation report")
if validation_df.empty:
    st.info("No validation report found yet.")
else:
    st.dataframe(validation_df, use_container_width=True)

render_section_header("Downloads")
for file_name, label in [
    (GROUP_STAGE_SIMULATED_MATCHES_FILE, "Download simulated matches CSV"),
    (GROUP_STAGE_RANKINGS_FILE, "Download group rankings CSV"),
    (BEST_THIRD_PLACED_TEAMS_FILE, "Download best third-placed teams CSV"),
    (ROUND_OF_32_QUALIFIERS_FILE, "Download Round-of-32 qualifiers CSV"),
]:
    path = PROCESSED_DATA_DIR / file_name
    if path.is_file():
        st.download_button(
            label=label,
            data=path.read_bytes(),
            file_name=file_name,
            mime="text/csv",
        )
