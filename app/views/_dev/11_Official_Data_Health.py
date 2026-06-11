"""Streamlit page: Official World Cup data health."""

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
    from app.components.ui import inject_page_theme, render_data_table, render_hero, render_metric_card, render_section_header
except ModuleNotFoundError:
    from components.ui import inject_page_theme, render_data_table, render_hero, render_metric_card, render_section_header

from src.official.loaders import (  # noqa: E402
    load_official_fixtures,
    load_official_groups,
    load_official_match_calendar,
    load_official_teams,
    load_official_venues,
    load_source_manifest,
    official_path,
)
from src.official.prepare_official_data import prepare_step17a_official_worldcup_data  # noqa: E402
import src.utils.constants as C  # noqa: E402

OFFICIAL_DATA_SUMMARY_FILE = getattr(C, "OFFICIAL_DATA_SUMMARY_FILE", "official_data_summary.json")
OFFICIAL_DATA_VALIDATION_REPORT_FILE = getattr(C, "OFFICIAL_DATA_VALIDATION_REPORT_FILE", "official_data_validation_report.csv")
OFFICIAL_TEAMS_FILE = getattr(C, "OFFICIAL_TEAMS_FILE", "official_teams.csv")
OFFICIAL_GROUPS_FILE = getattr(C, "OFFICIAL_GROUPS_FILE", "official_groups.csv")
OFFICIAL_FIXTURES_FILE = getattr(C, "OFFICIAL_FIXTURES_FILE", "official_fixtures.csv")
OFFICIAL_VENUES_FILE = getattr(C, "OFFICIAL_VENUES_FILE", "official_venues.csv")
OFFICIAL_SOURCE_MANIFEST_FILE = getattr(C, "OFFICIAL_SOURCE_MANIFEST_FILE", "source_manifest.json")


def _load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)



def render_page() -> None:
    render_hero(
        "Official Data Health",
        "Official-mode data lock, validation reports, and sample vs official visibility.",
        eyebrow="Official data",
    )

    render_section_header("Overview")
    st.markdown(
        "- Tracks official teams, groups, fixtures, venues, and match calendar\n"
        "- Distinguishes official mode from sample mode\n"
        "- Flags placeholder or unverified data honestly\n"
        "- Helps prevent non-official teams/fixtures from silently entering official-mode flows"
    )

    if st.button("Prepare / refresh official data"):
        summary = prepare_step17a_official_worldcup_data()
        st.success("Official-style data bundle prepared.")
        st.json(summary)

    summary = _load_json(official_path(OFFICIAL_DATA_SUMMARY_FILE))
    validation_df = pd.read_csv(official_path(OFFICIAL_DATA_VALIDATION_REPORT_FILE)) if official_path(OFFICIAL_DATA_VALIDATION_REPORT_FILE).is_file() else pd.DataFrame()
    teams_df = load_official_teams() if official_path(OFFICIAL_TEAMS_FILE).is_file() else pd.DataFrame()
    groups_df = load_official_groups() if official_path(OFFICIAL_GROUPS_FILE).is_file() else pd.DataFrame()
    fixtures_df = load_official_fixtures() if official_path(OFFICIAL_FIXTURES_FILE).is_file() else pd.DataFrame()
    venues_df = load_official_venues() if official_path(OFFICIAL_VENUES_FILE).is_file() else pd.DataFrame()
    manifest = load_source_manifest() if official_path(OFFICIAL_SOURCE_MANIFEST_FILE).is_file() else {}
    calendar_df = load_official_match_calendar() if official_path(getattr(C, "OFFICIAL_MATCH_CALENDAR_FILE", "official_match_calendar.csv")).is_file() else pd.DataFrame()

    st.subheader("Summary cards")
    if summary:
        c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
        with c1:
            render_metric_card("Teams", str(summary.get("teams_count", 0)))
        with c2:
            render_metric_card("Groups", str(summary.get("groups_count", 0)))
        with c3:
            render_metric_card("Fixtures", str(summary.get("fixtures_count", 0)))
        with c4:
            render_metric_card("Venues", str(summary.get("venues_count", 0)))
        with c5:
            render_metric_card("Validation", "passed" if summary.get("validation_passed") else "review")
        with c6:
            render_metric_card("Errors", str(summary.get("errors_count", 0)))
        with c7:
            render_metric_card("Warnings", str(summary.get("warnings_count", 0)))
    else:
        st.info("No official-data summary found yet.")

    if summary.get("status") == "needs_verification":
        st.warning("This data structure is official-style but still needs manual FIFA verification.")

    render_section_header("Teams by group")
    if not groups_df.empty:
        render_data_table(groups_df.sort_values(["group", "slot"]), use_container_width=True)
    else:
        st.info("No official groups found.")

    st.subheader("Fixture preview")
    if not fixtures_df.empty:
        render_data_table(fixtures_df.head(30), use_container_width=True)
    else:
        st.info("No official fixtures found.")

    st.subheader("Venue table")
    if not venues_df.empty:
        render_data_table(venues_df, use_container_width=True)
    else:
        st.info("No official venues found.")

    st.subheader("Validation report")
    if not validation_df.empty:
        render_data_table(validation_df, use_container_width=True)
    else:
        st.info("No validation report found.")

    st.subheader("Source manifest")
    if manifest:
        st.json(manifest)
    else:
        st.info("No source manifest found.")

    st.subheader("Official match calendar")
    if not calendar_df.empty:
        render_data_table(calendar_df.head(30), use_container_width=True)
    else:
        st.info("No official match calendar found.")

    st.subheader("Downloads")
    for file_name in [OFFICIAL_TEAMS_FILE, OFFICIAL_GROUPS_FILE, OFFICIAL_FIXTURES_FILE, OFFICIAL_DATA_VALIDATION_REPORT_FILE]:
        path = official_path(file_name)
        if path.is_file():
            st.download_button(label=f"Download {file_name}", data=path.read_bytes(), file_name=file_name, mime="text/csv")
