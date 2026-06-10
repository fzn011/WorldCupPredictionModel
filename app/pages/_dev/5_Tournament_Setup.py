"""Streamlit page: Step 11 tournament fixture and group setup."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import src.utils.constants as C  # noqa: E402
from src.tournament.prepare_tournament import prepare_step11_tournament_setup  # noqa: E402

PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")
TOURNAMENT_GROUPS_FILE = getattr(C, "TOURNAMENT_GROUPS_FILE", "tournament_groups.csv")
TOURNAMENT_FIXTURES_FILE = getattr(C, "TOURNAMENT_FIXTURES_FILE", "tournament_fixtures.csv")
TOURNAMENT_VALIDATION_REPORT_FILE = getattr(C, "TOURNAMENT_VALIDATION_REPORT_FILE", "tournament_validation_report.csv")
KNOCKOUT_PLACEHOLDER_FILE = getattr(C, "KNOCKOUT_PLACEHOLDER_FILE", "knockout_placeholders.csv")


st.title("Tournament Setup")
st.caption("Step 11 builds the tournament structure only (groups, fixtures, knockout placeholders).")

st.subheader("Tournament format overview")
st.markdown(
    "- 48 teams\n"
    "- 12 groups of 4 teams\n"
    "- 72 group-stage matches (6 per group)\n"
    "- Top 2 from each group + 8 best third-placed teams advance to Round of 32\n"
    "- No simulation/outcome prediction is performed on this page"
)

if st.button("Run / Refresh tournament setup"):
    summary = prepare_step11_tournament_setup()
    if summary.get("status") == "ok":
        st.success("Tournament setup prepared successfully.")
    else:
        st.warning("Tournament setup prepared with validation issues. Check validation report below.")
    st.json(summary)


def _safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.is_file():
        return pd.DataFrame()
    return pd.read_csv(path)


groups_df = _safe_read_csv(PROCESSED_DATA_DIR / TOURNAMENT_GROUPS_FILE)
fixtures_df = _safe_read_csv(PROCESSED_DATA_DIR / TOURNAMENT_FIXTURES_FILE)
validation_df = _safe_read_csv(PROCESSED_DATA_DIR / TOURNAMENT_VALIDATION_REPORT_FILE)
knockout_df = _safe_read_csv(PROCESSED_DATA_DIR / KNOCKOUT_PLACEHOLDER_FILE)

st.subheader("Groups table")
if groups_df.empty:
    st.info("No processed tournament groups found. Click 'Run / Refresh tournament setup'.")
else:
    st.dataframe(groups_df.sort_values(["group", "slot"]), use_container_width=True)

st.subheader("Group-stage fixtures table")
if fixtures_df.empty:
    st.info("No processed tournament fixtures found. Click 'Run / Refresh tournament setup'.")
else:
    st.dataframe(fixtures_df.sort_values(["group", "matchday", "match_id"]), use_container_width=True)

st.subheader("Validation report")
if validation_df.empty:
    st.info("No validation report found yet.")
else:
    st.dataframe(validation_df, use_container_width=True)

st.subheader("Knockout placeholders")
if knockout_df.empty:
    st.info("No knockout placeholder file found yet.")
else:
    st.dataframe(knockout_df, use_container_width=True)
