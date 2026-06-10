"""Streamlit page: Official Final Readiness.

Displays the final readiness evaluation for official_final mode,
including checklist status, blockers, and import workflow controls.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st
import pandas as pd

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
app_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(app_dir))

try:
    from app.components.ui import (  # noqa: E402
        inject_page_theme,
        render_data_quality_card,
        render_hero,
        render_section_header,
        render_success_panel,
        render_warning_panel,
    )
except ModuleNotFoundError:  # pragma: no cover
    from components.ui import inject_page_theme, render_data_quality_card, render_hero, render_section_header  # noqa: E402

from src.utils.constants import (
    PROJECT_ROOT,
    OFFICIAL_PROCESSED_DIR,
    OFFICIAL_READINESS_READY,
    OFFICIAL_READINESS_WARNING,
    OFFICIAL_READINESS_BLOCKED,
    FINAL_READINESS_CHECKLIST,
)
from src.official.final_readiness import (
    evaluate_official_final_readiness,
    save_final_readiness_report,
    is_official_final_mode_allowed,
)
from src.official.import_templates import generate_all_import_templates, create_import_manifest
from src.official.apply_imports import apply_official_import_file, apply_all_imports
from src.official.prepare_population_pack import prepare_step17d_official_data_population_pack
from src.official.promotion import load_official_final_mode, can_promote_to_official_final, promote_to_official_final
from src.utils.constants import OFFICIAL_POPULATION_DIR, OFFICIAL_POPULATION_GUIDE_FILE, OFFICIAL_IMPORT_TEMPLATES_DIR


st.set_page_config(page_title="Official Final Readiness", layout="wide", initial_sidebar_state="expanded")
inject_page_theme()
render_hero(
    "Official Data Readiness",
    "Verify official World Cup 2026 datasets, resolve blockers, and promote official_final mode.",
    eyebrow="Data gate",
)

st.markdown(
    """
This dashboard evaluates completeness, placeholders, and cross-dataset consistency before awards
and Monte Carlo outputs can use production official data.
    """
)

# Load or compute readiness report
def get_readiness_report():
    """Get readiness report, using cache."""
    if "readiness_report" not in st.session_state:
        st.session_state.readiness_report = evaluate_official_final_readiness()
    return st.session_state.readiness_report


# ===== CONTROLS =====
render_section_header("Controls")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔄 Refresh Evaluation", use_container_width=True):
        st.session_state.readiness_report = evaluate_official_final_readiness()
        st.rerun()

with col2:
    if st.button("📝 Generate Import Templates", use_container_width=True):
        with st.spinner("Generating import templates..."):
            output_dir = PROJECT_ROOT / OFFICIAL_PROCESSED_DIR
            templates = generate_all_import_templates(output_dir=output_dir)
            manifest_path = create_import_manifest(templates, output_dir)
            st.session_state.templates_generated = True
            st.session_state.template_count = len(templates)
        st.success(f"✓ Generated {len(templates)} templates!")
        st.rerun()

with col3:
    if st.button("💾 Save Report", use_container_width=True):
        report = get_readiness_report()
        report_path = save_final_readiness_report(report)
        st.success(f"✓ Report saved to {report_path}")

with col4:
    allowed, blockers = is_official_final_mode_allowed()
    if allowed:
        render_success_panel("Official final mode is ALLOWED")
    else:
        render_warning_panel(f"Official final mode is BLOCKED ({len(blockers)} blockers)")

st.divider()

# ===== READINESS REPORT =====
report = get_readiness_report()
status = report["status"]
summary = report["summary"]

# Summary cards
render_section_header("Summary dashboard")
col1, col2, col3, col4 = st.columns(4)
with col1:
    render_data_quality_card(
        "Checks passed",
        summary["blocker_count"] == 0,
        detail=f"{summary['passed_checks']}/{summary['total_checks']} checks",
        progress=summary["passed_checks"] / max(summary["total_checks"], 1),
    )
with col2:
    render_data_quality_card("Teams", summary["teams_count"] >= 48, detail=f"{summary['teams_count']}/48")
with col3:
    render_data_quality_card("Players", summary["players_count"] >= 1248, detail=f"{summary['players_count']}/1248")
with col4:
    render_data_quality_card(
        "Squads complete",
        summary["teams_with_26_players"] >= 48,
        detail=f"{summary['teams_with_26_players']}/48 teams × 26",
    )

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Blockers", summary["blocker_count"], delta_color="inverse")
with col2:
    st.metric("Warnings", summary["warning_count"], delta_color="inverse")
with col3:
    if status == OFFICIAL_READINESS_READY:
        render_success_panel("Status: READY")
    elif status == OFFICIAL_READINESS_WARNING:
        render_warning_panel("Status: WARNING — review before demo")
    else:
        render_warning_panel("Status: BLOCKED — resolve blockers")

st.divider()

# ===== CHECKLIST =====
st.header("Readiness Checklist")

# Group checks by category
categories = {}
for check in report["checklist"]:
    # Determine category from check id
    check_id = check["id"]
    if "team" in check_id:
        category = "Teams"
    elif "group" in check_id:
        category = "Groups"
    elif "venue" in check_id:
        category = "Venues"
    elif "fixture" in check_id:
        category = "Fixtures"
    elif "squad" in check_id or "player" in check_id:
        category = "Squads & Players"
    elif "award" in check_id:
        category = "Awards"
    elif "sample" in check_id or "consistency" in check_id:
        category = "Data Quality"
    else:
        category = "Other"

    if category not in categories:
        categories[category] = []
    categories[category].append(check)

# Display checklist by category
for category, checks in categories.items():
    with st.expander(f"**{category}** ({sum(1 for c in checks if c['passed'])}/{len(checks)} passed)", expanded=True):
        for check in checks:
            icon = "✓" if check["passed"] else "✗"
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{icon} **{check['id']}**")
            with col2:
                if check["passed"]:
                    st.success("Pass")
                else:
                    st.error("Fail")

            # Show details for failed checks
            if not check["passed"] and check.get("details"):
                details = check["details"]
                if isinstance(details, dict):
                    for key, value in details.items():
                        st.caption(f"  • {key}: {value}")

st.divider()

# ===== BLOCKERS =====
if report["blockers"]:
    st.header("🚫 Blockers")
    st.error(f"Found {len(report['blockers'])} blockers preventing official_final mode")

    for i, blocker in enumerate(report["blockers"], 1):
        with st.container():
            st.write(f"**{i}. {blocker.get('id', 'unknown')}**")
            details = blocker.get("details", {})
            if isinstance(details, dict):
                for key, value in details.items():
                    st.caption(f"  • {key}: {value}")
            st.divider()

# ===== WARNINGS =====
if report["warnings"]:
    st.header("⚠️ Warnings")
    st.warning(f"Found {len(report['warnings'])} warnings")

    for i, warning in enumerate(report["warnings"], 1):
        with st.container():
            st.write(f"**{i}. {warning.get('id', 'unknown')}**")
            details = warning.get("details", {})
            if isinstance(details, dict):
                for key, value in details.items():
                    st.caption(f"  • {key}: {value}")

st.divider()

# ===== IMPORT WORKFLOW =====
st.header("Manual Import Workflow")

st.markdown("""
If data is incomplete or contains placeholders, use the import workflow:

1. **Generate Templates**: Click "Generate Import Templates" above to create CSV templates
2. **Fill Data**: Open templates and fill in verified data from official FIFA sources
3. **Apply Imports**: Use the controls below to apply completed import files
4. **Re-evaluate**: Click "Refresh Evaluation" to check readiness again
""")

# Import file uploader
st.subheader("Apply Import Files")

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader(
        "Upload a single import file",
        type=["csv"],
        help="Upload a completed import CSV file (e.g., import_teams_template.csv)"
    )

    if uploaded_file:
        import_type = st.selectbox(
            "Import type",
            ["auto-detect", "teams", "groups", "fixtures", "venues", "players", "squads"],
            help="Select the type of import or use auto-detect"
        )

        if st.button("Apply Single Import"):
            # Save uploaded file temporarily
            temp_path = PROJECT_ROOT / OFFICIAL_PROCESSED_DIR / f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            with st.spinner("Applying import..."):
                template_type = None if import_type == "auto-detect" else import_type
                result = apply_official_import_file(
                    import_file=temp_path,
                    template_type=template_type,
                    create_backup=True,
                    re_prepare=True,
                )

                if result.get("success"):
                    st.success(f"✓ Import successful! {result.get('rows_imported', 0)} rows imported.")
                    # Clear the readiness report cache
                    st.session_state.readiness_report = evaluate_official_final_readiness()
                else:
                    st.error(f"✗ Import failed: {result.get('errors', ['Unknown error'])}")

                # Clean up temp file
                if temp_path.exists():
                    temp_path.unlink()

with col2:
    st.markdown("""
    ### Import File Format

    Each import file should be a CSV with the following structure:

    - **teams**: 48 rows, columns: team, team_code, confederation, group, group_slot, is_host, qualified, source
    - **groups**: 48 rows (12×4), columns: group, slot, team, team_code, confederation, is_host, source
    - **fixtures**: 104 rows, columns: match_id, match_number, stage, group, date, kickoff_local, kickoff_utc, timezone, venue, stadium, city, country, team_a, team_b, team_a_code, team_b_code, team_a_group_slot, team_b_group_slot, status, source
    - **venues**: 16 rows, columns: venue_id, stadium, venue, city, country, timezone, capacity, latitude, longitude, source
    - **players**: 1248 rows (48×26), columns: player_id, team, team_code, shirt_number, position_code, position, player_name, first_names, last_names, name_on_shirt, date_of_birth, age_at_tournament_start, club, club_country, height_cm, source
    """)

st.divider()

# ===== STEP 17D POPULATION WORKFLOW =====
st.header("Step 17D: Population Workflow")

pop_col1, pop_col2, pop_col3 = st.columns(3)

with pop_col1:
    if st.button("📦 Prepare Population Pack", use_container_width=True):
        with st.spinner("Generating population pack..."):
            pack = prepare_step17d_official_data_population_pack()
            st.session_state.population_pack = pack
        st.success("Population pack generated!")
        st.rerun()

with pop_col2:
    guide_path = PROJECT_ROOT / OFFICIAL_POPULATION_DIR / OFFICIAL_POPULATION_GUIDE_FILE
    if guide_path.is_file():
        st.download_button(
            "📄 Download Population Guide",
            guide_path.read_text(encoding="utf-8"),
            file_name=OFFICIAL_POPULATION_GUIDE_FILE,
            mime="text/markdown",
            use_container_width=True,
        )
    else:
        st.caption("Generate pack first")

with pop_col3:
    templates_dir = PROJECT_ROOT / OFFICIAL_IMPORT_TEMPLATES_DIR
    if templates_dir.is_dir() and any(templates_dir.glob("*.csv")):
        st.success(f"Templates in {OFFICIAL_IMPORT_TEMPLATES_DIR}/")
    else:
        st.caption("Templates not generated yet")

final_mode = load_official_final_mode()
final_ready_check, promo_summary = can_promote_to_official_final()

st.subheader("Promotion Status")
pc1, pc2, pc3 = st.columns(3)
pc1.metric("official_final_enabled", "Yes" if final_mode.get("official_final_enabled") else "No")
pc2.metric("final_ready", "Yes" if final_ready_check else "No")
pc3.metric("Blockers", promo_summary.get("blocker_count", 0))

st.markdown("""
**Population workflow:** Generate pack → fill templates from FIFA → preview → apply → re-evaluate readiness.
See the **Official Data Population** page (Step 17D) for the full workflow.

Promotion to `official_final` requires confirmation and full readiness. It cannot be one-click promoted while blockers remain.
""")

if final_ready_check:
    confirm = st.checkbox("I confirm all official data is verified against FIFA sources")
    if confirm and st.button("Promote to official_final (requires confirmation)"):
        promo_result = promote_to_official_final(confirmed=True)
        if promo_result.get("status") == "promoted":
            st.success("Promoted to official_final!")
        else:
            st.error(promo_result.get("message", "Promotion blocked"))

st.divider()

# ===== FINAL VERDICT =====
st.header("Final Verdict")

if report["is_official_final_ready"]:
    st.success("""
    ## ✓ Official Final Mode is READY

    All readiness checks have passed. The system is ready for production use
    with official FIFA World Cup 2026 data.
    """)
else:
    st.error(f"""
    ## ✗ Official Final Mode is BLOCKED

    The system is not ready for official_final mode. Please resolve the {len(report['blockers'])} blocker(s)
    listed above before enabling official_final mode.

    Use the import workflow to update incomplete data, or wait for official FIFA data releases.
    """)

st.divider()

# ===== ABOUT =====
st.markdown("""
### About This Page

This page provides the final readiness evaluation for Step 17C of the FIFA World Cup 2026 AI Predictor.

**Readiness Checks:**
- **Teams**: All 48 teams verified with no placeholder values
- **Groups**: All 12 groups with 4 teams each, no placeholders
- **Venues**: All venues verified with complete information
- **Fixtures**: All 104 matches scheduled with venues and teams
- **Squads**: All 48 teams with 26 players each (1248 total)
- **Players**: All players registered with no placeholder values
- **Awards**: Award candidates generated with player priors merged
- **Data Quality**: No sample_to_be_verified rows, cross-dataset consistency verified

**Blocking Conditions:**
- Incomplete teams, groups, venues, fixtures, squads, or players
- Placeholder values detected (TBD, Unknown, Sample, etc.)
- Sample rows that haven't been verified
- Data inconsistency between datasets
""")