"""Streamlit page: Official Squads Health.

Displays official World Cup squad data, player priors, and award candidates.
Provides controls to prepare/refresh squad data and download outputs.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import json

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
app_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(app_dir))

try:
    from app.components.ui import inject_page_theme, render_hero, render_section_header
except ModuleNotFoundError:
    from components.ui import inject_page_theme, render_hero, render_section_header

from src.utils.constants import (
    PROJECT_ROOT,
    OFFICIAL_PROCESSED_DIR,
    PROCESSED_DATA_DIR,
)
from src.official.prepare_squads import prepare_step17b_official_squads_and_priors


def format_bytes(num_bytes: int) -> str:
    """Format bytes to human-readable size."""
    for unit in ["B", "KB", "MB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} GB"


st.set_page_config(page_title="Official Squads Health", layout="wide", initial_sidebar_state="expanded")
inject_page_theme()
render_hero(
    "Official Squads & Player Priors",
    "Squad validation layer — official players gate award predictions in official mode.",
    eyebrow="Step 17B",
)

render_section_header("Controls")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Prepare/Refresh Squads", use_container_width=True):
        with st.spinner("Preparing official squads..."):
            result = prepare_step17b_official_squads_and_priors()
            st.session_state.last_prep_result = result
            st.success("✓ Squads prepared!")
            st.rerun()

with col2:
    if st.button("🔄 Strict Validation", use_container_width=True, help="Error on incomplete squads"):
        with st.spinner("Validating with strict squad sizes..."):
            result = prepare_step17b_official_squads_and_priors(strict_squad_size=True)
            st.session_state.last_prep_result = result
            st.success("✓ Validation complete!")
            st.rerun()

with col3:
    if st.button("🔄 Regenerate Priors", use_container_width=True, help="Regenerate priors template"):
        with st.spinner("Regenerating player priors..."):
            result = prepare_step17b_official_squads_and_priors(overwrite_priors=True)
            st.session_state.last_prep_result = result
            st.success("✓ Priors regenerated!")
            st.rerun()

st.divider()

# Load squad summary
summary_path = PROJECT_ROOT / OFFICIAL_PROCESSED_DIR / "official_squad_summary.json"

if not summary_path.exists():
    st.warning("Squad data not found. Click 'Prepare/Refresh Squads' above to generate.")
    st.stop()

with open(summary_path) as f:
    summary = json.load(f)

# Summary cards
st.header("Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Official Players", summary.get("official_players_count", 0))

with col2:
    st.metric("Teams", summary.get("official_teams_with_players", 0))

with col3:
    teams_with_26 = summary.get("teams_with_26_players", 0)
    st.metric("Teams with 26 Players", f"{teams_with_26}/48")

with col4:
    st.metric("Award Candidates", summary.get("official_award_candidates_count", 0))

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Unmatched Priors", summary.get("unmatched_priors_count", 0))

with col2:
    st.metric("Errors", summary.get("errors_count", 0))

with col3:
    st.metric("Warnings", summary.get("warnings_count", 0))

with col4:
    st.metric("Sample/Template Rows", summary.get("sample_to_be_verified_count", 0))

col1, col2 = st.columns(2)

with col1:
    status = summary.get("status", "unknown")
    if status == "ok":
        st.success(f"Status: {status.upper()}")
    elif status == "needs_verification":
        st.warning(f"Status: {status.upper()}")
    else:
        st.error(f"Status: {status.upper()}")

with col2:
    val_passed = "✓ PASSED" if summary.get("validation_passed") else "✗ FAILED"
    if summary.get("validation_passed"):
        st.success(f"Validation: {val_passed}")
    else:
        st.error(f"Validation: {val_passed}")

if summary.get("notes"):
    st.info("**Notes:**\n" + "\n".join(f"• {n}" for n in summary["notes"]))

st.divider()

# Official players table
st.header("Official Players")

try:
    players_path = PROJECT_ROOT / OFFICIAL_PROCESSED_DIR / "official_players.csv"
    players = pd.read_csv(players_path)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Players", len(players))
    with col2:
        sample_count = len(players[players["source"] == "sample_to_be_verified"])
        st.metric("Sample/Template", sample_count)
    
    # Filterable view
    st.subheader("Player List")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_teams = st.multiselect(
            "Filter by team:",
            sorted(players["team"].unique()),
            default=sorted(players["team"].unique())[:5]
        )
    with col2:
        selected_positions = st.multiselect(
            "Filter by position:",
            sorted(players["position"].unique()),
            default=sorted(players["position"].unique())
        )
    with col3:
        show_sample_only = st.checkbox("Sample/template only?")
    
    filtered_players = players[
        (players["team"].isin(selected_teams)) &
        (players["position"].isin(selected_positions))
    ]
    
    if show_sample_only:
        filtered_players = filtered_players[filtered_players["source"] == "sample_to_be_verified"]
    
    display_cols = ["player_name", "team", "position_code", "position", "shirt_number", 
                    "club", "age_at_tournament_start", "source"]
    st.dataframe(filtered_players[display_cols].sort_values("team"), use_container_width=True)
    
except Exception as e:
    st.error(f"Error loading players: {e}")

st.divider()

# Squad summary
st.header("Squad Summary by Team")

try:
    squads_path = PROJECT_ROOT / OFFICIAL_PROCESSED_DIR / "official_squads.csv"
    squads = pd.read_csv(squads_path)
    
    st.dataframe(squads.sort_values("team"), use_container_width=True)
    
except Exception as e:
    st.error(f"Error loading squad summary: {e}")

st.divider()

# Award candidates
st.header("Official Award Candidates Preview")

try:
    candidates_path = PROJECT_ROOT / PROCESSED_DATA_DIR / "official_award_candidates.csv"
    candidates = pd.read_csv(candidates_path)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Candidates", len(candidates))
    with col2:
        with_priors = len(candidates[candidates["has_player_prior"] == True])
        st.metric("With User Priors", with_priors)
    
    display_cols = ["player_name", "team", "position", "base_player_rating", 
                    "expected_minutes_share", "has_player_prior", "source"]
    st.dataframe(candidates[display_cols].head(50), use_container_width=True)
    
except Exception as e:
    st.error(f"Error loading award candidates: {e}")

st.divider()

# Validation report
st.header("Validation Report")

try:
    report_path = PROJECT_ROOT / OFFICIAL_PROCESSED_DIR / "official_squad_validation_report.csv"
    if report_path.exists():
        report = pd.read_csv(report_path)
        
        if len(report) == 0:
            st.success("No validation issues found!")
        else:
            errors = report[report["severity"] == "error"]
            warnings = report[report["severity"] == "warning"]
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Errors", len(errors))
            with col2:
                st.metric("Warnings", len(warnings))
            
            if len(errors) > 0:
                with st.expander("🔴 Errors"):
                    st.dataframe(errors, use_container_width=True)
            
            if len(warnings) > 0:
                with st.expander("🟡 Warnings"):
                    st.dataframe(warnings.head(20), use_container_width=True)
    else:
        st.info("No validation report found")
        
except Exception as e:
    st.error(f"Error loading validation report: {e}")

st.divider()

# Unmatched priors
st.header("Unmatched Priors Report")

try:
    merge_path = PROJECT_ROOT / OFFICIAL_PROCESSED_DIR / "official_player_prior_merge_report.csv"
    if merge_path.exists():
        unmatched = pd.read_csv(merge_path)
        
        if len(unmatched) > 0:
            st.warning(f"Found {len(unmatched)} priors for players not in official squads (excluded from award candidates)")
            st.dataframe(unmatched.head(20), use_container_width=True)
        else:
            st.success("No unmatched priors!")
    else:
        st.info("No merge report found")
        
except Exception as e:
    st.error(f"Error loading merge report: {e}")

st.divider()

# Download section
st.header("Downloads")

col1, col2, col3, col4 = st.columns(4)

try:
    with col1:
        players = pd.read_csv(PROJECT_ROOT / OFFICIAL_PROCESSED_DIR / "official_players.csv")
        st.download_button(
            "📥 Official Players",
            players.to_csv(index=False),
            "official_players.csv",
            "text/csv"
        )
    
    with col2:
        squads = pd.read_csv(PROJECT_ROOT / OFFICIAL_PROCESSED_DIR / "official_squads.csv")
        st.download_button(
            "📥 Squad Summary",
            squads.to_csv(index=False),
            "official_squads.csv",
            "text/csv"
        )
    
    with col3:
        team_map = pd.read_csv(PROJECT_ROOT / OFFICIAL_PROCESSED_DIR / "official_team_player_map.csv")
        st.download_button(
            "📥 Team-Player Map",
            team_map.to_csv(index=False),
            "official_team_player_map.csv",
            "text/csv"
        )
    
    with col4:
        candidates = pd.read_csv(PROJECT_ROOT / PROCESSED_DATA_DIR / "official_award_candidates.csv")
        st.download_button(
            "📥 Award Candidates",
            candidates.to_csv(index=False),
            "official_award_candidates.csv",
            "text/csv"
        )

except Exception as e:
    st.error(f"Error preparing downloads: {e}")

st.divider()

st.markdown("""
### About This Page

- **Official Players**: All players from official World Cup squads
- **Squad Summary**: Player counts and position breakdown by team
- **Award Candidates**: Official players enriched with editable player priors
- **Validation**: Checks squad integrity and data consistency
- **Unmatched Priors**: Priors for non-official players (excluded from awards)

**Important**: In official mode, only players in `official_award_candidates.csv` can be considered for awards.
""")
