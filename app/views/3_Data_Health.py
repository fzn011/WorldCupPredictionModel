"""Streamlit page: Unified Official Data Health & Readiness dashboard."""

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
    from app.streamlit_paths import OFFICIAL_PROCESSED_DIR, PROCESSED_DATA_DIR, PROJECT_ROOT
except ModuleNotFoundError:
    from streamlit_paths import OFFICIAL_PROCESSED_DIR, PROCESSED_DATA_DIR, PROJECT_ROOT

try:
    from app.components.ui import (
        inject_page_theme,
        render_data_quality_card,
        render_data_table,
        render_download_card,
        render_hero,
        render_info_panel,
        render_metric_card,
        render_progress_bar,
        render_readiness_item,
        render_section_header,
        render_status_badge,
        render_success_panel,
        render_warning_panel,
    )
except ModuleNotFoundError:
    from components.ui import (
        inject_page_theme,
        render_data_quality_card,
        render_data_table,
        render_download_card,
        render_hero,
        render_info_panel,
        render_metric_card,
        render_progress_bar,
        render_readiness_item,
        render_section_header,
        render_status_badge,
        render_success_panel,
        render_warning_panel,
    )

from src.official.loaders import (
    load_official_fixtures,
    load_official_groups,
    load_official_teams,
    load_official_venues,
    official_path,
)
from src.official.final_readiness import (
    evaluate_official_final_readiness,
    is_official_final_mode_allowed,
    save_final_readiness_report,
)
from src.official.import_templates import generate_all_import_templates, create_import_manifest
from src.official.apply_imports import apply_official_import_file
from src.official.promotion import (
    can_promote_to_official_final,
    load_official_final_mode,
    promote_to_official_final,
)
from src.official.prepare_population_pack import prepare_step17d_official_data_population_pack
import src.utils.constants as C

try:
    from app.product_status import load_product_data_status
except ModuleNotFoundError:
    from product_status import load_product_data_status

OFFICIAL_TEAMS_FILE = getattr(C, "OFFICIAL_TEAMS_FILE", "official_teams.csv")
OFFICIAL_GROUPS_FILE = getattr(C, "OFFICIAL_GROUPS_FILE", "official_groups.csv")
OFFICIAL_FIXTURES_FILE = getattr(C, "OFFICIAL_FIXTURES_FILE", "official_fixtures.csv")
OFFICIAL_VENUES_FILE = getattr(C, "OFFICIAL_VENUES_FILE", "official_venues.csv")
OFFICIAL_DATA_SUMMARY_FILE = getattr(C, "OFFICIAL_DATA_SUMMARY_FILE", "official_data_summary.json")
OFFICIAL_DATA_VALIDATION_REPORT_FILE = getattr(
    C, "OFFICIAL_DATA_VALIDATION_REPORT_FILE", "official_data_validation_report.csv"
)
OFFICIAL_POPULATION_DIR = getattr(C, "OFFICIAL_POPULATION_DIR", "data/official/population")
OFFICIAL_POPULATION_GUIDE_FILE = getattr(
    C, "OFFICIAL_POPULATION_GUIDE_FILE", "OFFICIAL_POPULATION_GUIDE.md"
)
OFFICIAL_IMPORT_TEMPLATES_DIR = getattr(
    C, "OFFICIAL_IMPORT_TEMPLATES_DIR", "data/official/import_templates"
)

# ─────────────────────────────────────────────────────────────────────────────

def render_page() -> None:
    render_hero(
        "Data Quality",
        "Overview of official World Cup 2026 data completeness and verification status.",
        eyebrow="Data verification",
    )


    def _get_readiness() -> dict:
        if "readiness_report" not in st.session_state:
            st.session_state.readiness_report = evaluate_official_final_readiness()
        return st.session_state.readiness_report


    pdata = load_product_data_status()
    report = _get_readiness()
    summary = report.get("summary", {})
    status = report.get("status", "blocked")

    render_section_header("Data verification summary")

    if pdata["is_verified"]:
        render_success_panel("Official tournament data is ready. Analytics features are fully enabled.")
    else:
        render_warning_panel("Some datasets still need review. Core features remain available.")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_metric_card(
            "Official Data",
            pdata["data_label"],
            variant="ok" if pdata["is_verified"] else "warn",
        )
    with c2:
        render_metric_card("Teams", str(pdata["teams_count"]), sub="Target 48", variant="ok" if pdata["teams_count"] >= 48 else "warn")
    with c3:
        render_metric_card("Fixtures", str(pdata["fixtures_count"]), sub="Target 104", variant="ok" if pdata["fixtures_count"] >= 100 else "warn")
    with c4:
        render_metric_card("Players", f"{pdata['players_count']:,}", sub="Target 1,248", variant="ok" if pdata["players_count"] >= 1248 else "warn")
    with c5:
        render_metric_card("Full Squads", str(pdata["teams_with_26_players"]), sub="Target 48", variant="ok" if pdata["teams_with_26_players"] >= 48 else "warn")

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    render_section_header("Data preview")

    tab_teams, tab_groups, tab_fixtures, tab_venues = st.tabs(["Teams", "Groups", "Fixtures", "Venues"])

    with tab_teams:
        df = load_official_teams() if official_path(OFFICIAL_TEAMS_FILE).is_file() else pd.DataFrame()
        if df.empty:
            st.info("No official teams data.")
        else:
            from src.official.team_name_enrichment import format_official_teams_for_display, is_valid_team_name

            named_count = int(df["team"].map(is_valid_team_name).sum()) if "team" in df.columns else 0
            st.caption(f"{len(df)} teams loaded · {named_count} with resolved names")
            show_technical = st.checkbox(
                "Show technical fields",
                value=False,
                key="dq_teams_show_technical",
            )
            render_data_table(format_official_teams_for_display(df, include_technical=show_technical))

    with tab_groups:
        df = load_official_groups() if official_path(OFFICIAL_GROUPS_FILE).is_file() else pd.DataFrame()
        if df.empty:
            st.info("No official groups data.")
        else:
            if "group" in df.columns and "slot" in df.columns:
                df = df.sort_values(["group", "slot"])
            st.caption(f"{len(df)} group slots loaded")
            render_data_table(df)

    with tab_fixtures:
        df = load_official_fixtures() if official_path(OFFICIAL_FIXTURES_FILE).is_file() else pd.DataFrame()
        if df.empty:
            st.info("No official fixtures data.")
        else:
            st.caption(f"{len(df)} fixtures loaded")
            render_data_table(df.head(50))

    with tab_venues:
        df = load_official_venues() if official_path(OFFICIAL_VENUES_FILE).is_file() else pd.DataFrame()
        if df.empty:
            st.info("No official venues data.")
        else:
            st.caption(f"{len(df)} venues loaded")
            render_data_table(df)

    with st.expander("Technical details", expanded=False):
        render_section_header("Import workflow")
        st.markdown(
            """
    Upload a completed import CSV to update official data.
    Templates are generated from the controls below.
    """
        )

        imp_col1, imp_col2 = st.columns([2, 3])

        with imp_col1:
            uploaded = st.file_uploader("Upload import file", type=["csv"])
            if uploaded:
                import_type = st.selectbox(
                    "Import type",
                    ["auto-detect", "teams", "groups", "fixtures", "venues", "players", "squads"],
                )
                if st.button("Apply Import", type="primary"):
                    temp_path = PROJECT_ROOT / OFFICIAL_PROCESSED_DIR / f"temp_{uploaded.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded.getvalue())
                    with st.spinner("Applying import..."):
                        ttype = None if import_type == "auto-detect" else import_type
                        result = apply_official_import_file(
                            import_file=temp_path,
                            template_type=ttype,
                            create_backup=True,
                            re_prepare=True,
                        )
                    if result.get("success"):
                        st.success(f"{result.get('rows_imported', 0)} rows imported.")
                        st.session_state.readiness_report = evaluate_official_final_readiness()
                    else:
                        st.error(f"Import failed: {result.get('errors', ['Unknown error'])}")
                    if temp_path.exists():
                        temp_path.unlink()

        with imp_col2:
            render_section_header("Expected formats")
            st.markdown(
                """
    | Template | Rows | Key columns |
    |---|---|---|
    | teams | 48 | team, team_code, confederation, group |
    | groups | 48 | group, slot, team, team_code |
    | fixtures | 104 | match_id, stage, date, team_a, team_b |
    | venues | 16 | venue_id, stadium, city, capacity |
    | players | 1248 | player_name, team, position, shirt_number |
                """
            )

        render_section_header("Official final mode")

        final_mode = load_official_final_mode()
        final_ready_check, promo_summary = can_promote_to_official_final()
        final_enabled = bool(final_mode.get("official_final_enabled"))

        p1, p2, p3 = st.columns(3)
        with p1:
            render_metric_card(
                "Official final",
                "Enabled" if final_enabled else "Disabled",
                variant="ok" if final_enabled else "warn",
            )
        with p2:
            render_metric_card(
                "Ready to promote",
                "Yes" if final_ready_check else "No",
                variant="ok" if final_ready_check else "danger",
            )
        with p3:
            render_metric_card(
                "Blockers remaining",
                str(promo_summary.get("blocker_count", 0)),
                variant="ok" if promo_summary.get("blocker_count", 0) == 0 else "danger",
            )

        if final_ready_check:
            st.markdown("<br>", unsafe_allow_html=True)
            confirm = st.checkbox("I confirm all data has been verified against official FIFA sources")
            if confirm and st.button("Promote to Official Final Mode", type="primary"):
                result = promote_to_official_final(confirmed=True)
                if result.get("status") == "promoted":
                    render_success_panel("Promoted to official final mode.")
                    st.session_state.readiness_report = evaluate_official_final_readiness()
                    st.rerun()
                else:
                    render_warning_panel(f"Promotion blocked: {result.get('message', 'unknown')}")
        elif not final_enabled:
            render_warning_panel(
                "Resolve all blockers before enabling official final mode. "
                f"{promo_summary.get('blocker_count', 0)} blocker(s) remaining."
            )

        render_section_header("Downloads")

        dl1, dl2 = st.columns(2)
        with dl1:
            render_download_card(
                "Official teams",
                "48 teams with codes and groups",
                official_path(OFFICIAL_TEAMS_FILE),
                file_name=OFFICIAL_TEAMS_FILE,
            )
            render_download_card(
                "Official groups",
                "Group stage assignments",
                official_path(OFFICIAL_GROUPS_FILE),
                file_name=OFFICIAL_GROUPS_FILE,
            )
        with dl2:
            render_download_card(
                "Official fixtures",
                "All 104 scheduled matches",
                official_path(OFFICIAL_FIXTURES_FILE),
                file_name=OFFICIAL_FIXTURES_FILE,
            )
            render_download_card(
                "Validation report",
                "Data quality and consistency checks",
                official_path(OFFICIAL_DATA_VALIDATION_REPORT_FILE),
                file_name=OFFICIAL_DATA_VALIDATION_REPORT_FILE,
            )

        guide_path = PROJECT_ROOT / OFFICIAL_POPULATION_DIR / OFFICIAL_POPULATION_GUIDE_FILE
        if guide_path.is_file():
            render_download_card(
                "Population guide",
                "Data filling instructions",
                guide_path,
                file_name=OFFICIAL_POPULATION_GUIDE_FILE,
                mime="text/markdown",
            )

        passed = summary.get("passed_checks", 0)
        total = summary.get("total_checks", 15)
        progress = passed / max(total, 1)
        prog_kind = "ok" if status == "ready" else ("warn" if status == "warning" else "danger")
        render_progress_bar(progress, label=f"Internal verification — {passed}/{total}", kind=prog_kind)

        checklist = report.get("checklist", [])
        if checklist:
            for chk in checklist[:20]:
                render_readiness_item(
                    chk.get("id", "unknown"),
                    chk.get("passed", False),
                )

        ctrl1, ctrl2 = st.columns(2)
        with ctrl1:
            if st.button("Refresh evaluation", use_container_width=True):
                st.session_state.readiness_report = evaluate_official_final_readiness()
                st.rerun()
        with ctrl2:
            if st.button("Generate import templates", use_container_width=True):
                with st.spinner("Generating templates..."):
                    out_dir = PROJECT_ROOT / OFFICIAL_PROCESSED_DIR
                    templates = generate_all_import_templates(output_dir=out_dir)
                    create_import_manifest(templates, out_dir)
                st.success(f"{len(templates)} templates generated.")
                st.rerun()

    st.caption("Analytics estimates only. Data completeness required for official final mode.")
