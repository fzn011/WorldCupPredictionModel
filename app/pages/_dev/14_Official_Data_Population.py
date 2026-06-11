"""Streamlit page: Official Data Population."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

project_root = Path(__file__).resolve().parents[2]
app_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(app_dir))

try:
    from app.components.ui import (
        inject_page_theme,
        render_download_card,
        render_hero,
        render_metric_card,
        render_section_header,
        render_status_card,
        render_warning_panel,
    )
except ModuleNotFoundError:
    from components.ui import (
        inject_page_theme,
        render_download_card,
        render_hero,
        render_metric_card,
        render_section_header,
        render_status_card,
        render_warning_panel,
    )

from src.utils.constants import (
    PROJECT_ROOT,
    OFFICIAL_POPULATION_DIR,
    OFFICIAL_POPULATION_GUIDE_FILE,
    OFFICIAL_POPULATION_MISSING_DATA_REPORT_FILE,
    OFFICIAL_POPULATION_REPORTS_DIR,
    OFFICIAL_POPULATION_WORKBOOK_DIR,
    OFFICIAL_MASTER_IMPORT_WORKBOOK_FILE,
    OFFICIAL_MASTER_IMPORT_README_FILE,
    OFFICIAL_IMPORT_TEMPLATES_DIR,
    OFFICIAL_POPULATION_TEMPLATE_FILES,
    OFFICIAL_POPULATION_REQUIRED_STEPS,
    OFFICIAL_PROCESSED_DIR,
)
from src.official.final_readiness import evaluate_official_final_readiness
from src.official.missing_data import build_official_missing_data_report, save_missing_data_report
from src.official.population_status import load_population_status, summarize_population_status
from src.official.prepare_population_pack import prepare_step17d_official_data_population_pack
from src.official.promotion import can_promote_to_official_final, load_official_final_mode, promote_to_official_final


inject_page_theme()
render_hero(
    "Official Data Population",
    "Fill, validate, preview, and apply verified World Cup 2026 data. Manual FIFA verification only — no scraping.",
    eyebrow="Data population",
)

render_warning_panel(
    "The app does <strong>not</strong> scrape websites or auto-fetch FIFA data. "
    "Copy verified official sources into import templates before applying."
)

POPULATION_DIR = PROJECT_ROOT / OFFICIAL_POPULATION_DIR
TEMPLATES_DIR = PROJECT_ROOT / OFFICIAL_IMPORT_TEMPLATES_DIR
WORKBOOK_DIR = PROJECT_ROOT / OFFICIAL_POPULATION_WORKBOOK_DIR
REPORTS_DIR = PROJECT_ROOT / OFFICIAL_POPULATION_REPORTS_DIR

status = load_population_status()
summary = summarize_population_status(status)
final_mode = load_official_final_mode()
readiness = evaluate_official_final_readiness()
final_ready, promo_summary = can_promote_to_official_final()

tab_overview, tab_status, tab_downloads, tab_readiness = st.tabs(
    ["Overview", "Status & checklist", "Downloads", "Readiness & promotion"]
)

with tab_overview:
    render_section_header("Data modes")
    col1, col2 = st.columns(2)
    with col1:
        render_metric_card("sample mode", "Development", sub="Bundled fallback data")
        render_metric_card("official_draft", "Partial", sub="Official structure, partially filled")
    with col2:
        render_status_card("official_final", "Gated", sub="Blocked until readiness passes", badge="warn")

    render_section_header("Generate population pack")
    if st.button("Generate population pack", use_container_width=True, key="gen_pack_17d"):
        with st.spinner("Generating population pack..."):
            result = prepare_step17d_official_data_population_pack()
            st.session_state.population_pack = result
        st.success(f"Population pack ready: {result.get('status')}")
        st.rerun()

    if "population_pack" in st.session_state:
        pack = st.session_state.population_pack
        st.json({k: pack[k] for k in ("status", "final_ready", "teams_count", "fixtures_count", "players_count") if k in pack})

    st.page_link(
        "pages/_dev/15_Source_Assisted_Population.py",
        label="Source-Assisted Population",
        icon="⚽",
    )

with tab_status:
    render_section_header("Population status")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Overall status", str(summary.get("overall_status", "unknown")))
    with c2:
        render_metric_card("Steps completed", f"{summary.get('completed_steps', 0)}/{summary.get('total_steps', 0)}")
    with c3:
        render_status_card(
            "Final ready",
            "Yes" if readiness.get("is_official_final_ready") else "No",
            badge="ok" if readiness.get("is_official_final_ready") else "danger",
        )
    with c4:
        render_status_card(
            "official_final",
            "Enabled" if final_mode.get("official_final_enabled") else "Disabled",
            badge="ok" if final_mode.get("official_final_enabled") else "muted",
        )

    render_section_header("Required data checklist")
    checklist_data = [
        {"Item": "48 official teams", "Target": 48, "Current": readiness.get("summary", {}).get("teams_count", 0)},
        {"Item": "12 groups × 4 teams", "Target": 48, "Current": readiness.get("summary", {}).get("teams_count", 0)},
        {"Item": "104 fixtures", "Target": 104, "Current": 0},
        {"Item": "1,248 players (48×26)", "Target": 1248, "Current": readiness.get("summary", {}).get("players_count", 0)},
        {"Item": "Teams with 26 players", "Target": 48, "Current": readiness.get("summary", {}).get("teams_with_26_players", 0)},
        {"Item": "Zero sample_to_be_verified", "Target": 0, "Current": "Check report"},
        {"Item": "Zero blocking placeholders", "Target": 0, "Current": "Check report"},
    ]
    fixtures_path = PROJECT_ROOT / OFFICIAL_PROCESSED_DIR / "official_fixtures.csv"
    if fixtures_path.is_file():
        checklist_data[2]["Current"] = len(pd.read_csv(fixtures_path))

    st.dataframe(pd.DataFrame(checklist_data), use_container_width=True)

    for step in OFFICIAL_POPULATION_REQUIRED_STEPS:
        step_info = status.get("steps", {}).get(step, {})
        icon = "✅" if step_info.get("status") in ("imported", "final_ready") else "⏳"
        st.caption(f"{icon} **{step}**: {step_info.get('status', 'unknown')}")

    render_section_header("Missing-data report")
    missing_path = REPORTS_DIR / OFFICIAL_POPULATION_MISSING_DATA_REPORT_FILE
    if st.button("Refresh missing-data report", key="refresh_missing_17d"):
        missing_df = build_official_missing_data_report()
        save_missing_data_report(missing_df)
        st.rerun()

    if missing_path.is_file():
        missing_df = pd.read_csv(missing_path)
        render_metric_card("Total issues", str(len(missing_df)))
        if not missing_df.empty:
            severity_counts = missing_df["severity"].value_counts().to_dict()
            st.caption(f"Errors: {severity_counts.get('error', 0)} | Warnings: {severity_counts.get('warning', 0)}")
            with st.expander("Missing-data table"):
                st.dataframe(missing_df.head(50), use_container_width=True)
    else:
        st.info("Generate population pack or refresh to create missing-data report.")

with tab_downloads:
    render_section_header("Templates & guides")
    guide_path = POPULATION_DIR / OFFICIAL_POPULATION_GUIDE_FILE
    workbook_path = WORKBOOK_DIR / OFFICIAL_MASTER_IMPORT_WORKBOOK_FILE
    readme_path = WORKBOOK_DIR / OFFICIAL_MASTER_IMPORT_README_FILE

    d1, d2 = st.columns(2)
    with d1:
        render_download_card("Population guide", OFFICIAL_POPULATION_GUIDE_FILE, guide_path, mime="text/markdown")
    with d2:
        if workbook_path.is_file():
            render_download_card(
                "Master workbook",
                OFFICIAL_MASTER_IMPORT_WORKBOOK_FILE,
                workbook_path,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        elif readme_path.is_file():
            render_download_card("Workbook README", OFFICIAL_MASTER_IMPORT_README_FILE, readme_path, mime="text/markdown")

    if TEMPLATES_DIR.is_dir():
        render_section_header("CSV templates")
        for name, filename in OFFICIAL_POPULATION_TEMPLATE_FILES.items():
            tpl_path = TEMPLATES_DIR / filename
            if tpl_path.is_file():
                render_download_card(filename, f"Import template — {name}", tpl_path)

with tab_readiness:
    render_section_header("Final readiness")
    if final_ready:
        st.success("All readiness checks passed. Promotion is available with confirmation.")
    else:
        st.error(f"Promotion blocked. Blockers: {promo_summary.get('blocker_count', 0)}")

    if promo_summary.get("blockers"):
        for b in promo_summary["blockers"]:
            st.caption(f"• {b}")

    render_section_header("Promotion to official_final")
    render_warning_panel(
        "Promotion requires explicit confirmation and full readiness. Do not promote with incomplete data."
    )

    if st.button("Check promotion status", key="check_promo_17d"):
        result = promote_to_official_final(confirmed=False)
        st.write(result.get("message", ""))
        st.json(result.get("readiness_summary", {}))

    if final_ready:
        if st.checkbox("I confirm all data is verified against official FIFA sources"):
            if st.button("Promote to official_final", key="promote_17d"):
                result = promote_to_official_final(confirmed=True)
                if result.get("status") == "promoted":
                    st.success("Promoted to official_final!")
                else:
                    st.error(result.get("message", "Promotion failed"))
    else:
        st.info("Promotion remains blocked until final readiness passes.")

    with st.expander("Import preview & apply commands"):
        st.code("""
python scripts/preview_official_import.py --target players --file data/official/import_templates/official_players_import_template.csv
python scripts/apply_official_import.py --target players --file data/official/import_templates/official_players_import_template.csv --preview
python scripts/apply_official_import.py --target players --file data/official/import_templates/official_players_import_template.csv
python scripts/evaluate_official_final_readiness.py
        """, language="bash")
