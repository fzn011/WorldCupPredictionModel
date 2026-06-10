"""Streamlit page: Official Data Population (Step 17D)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from src.utils.constants import (
    PROJECT_ROOT,
    OFFICIAL_POPULATION_DIR,
    OFFICIAL_POPULATION_GUIDE_FILE,
    OFFICIAL_POPULATION_STATUS_FILE,
    OFFICIAL_POPULATION_MISSING_DATA_REPORT_FILE,
    OFFICIAL_POPULATION_REPORTS_DIR,
    OFFICIAL_POPULATION_WORKBOOK_DIR,
    OFFICIAL_MASTER_IMPORT_WORKBOOK_FILE,
    OFFICIAL_MASTER_IMPORT_README_FILE,
    OFFICIAL_IMPORT_TEMPLATES_DIR,
    OFFICIAL_POPULATION_TEMPLATE_FILES,
    OFFICIAL_POPULATION_REQUIRED_STEPS,
    OFFICIAL_FINAL_MODE_FLAG_FILE,
    OFFICIAL_PROCESSED_DIR,
)
from src.official.final_readiness import evaluate_official_final_readiness
from src.official.missing_data import build_official_missing_data_report, save_missing_data_report
from src.official.population_status import load_population_status, summarize_population_status
from src.official.prepare_population_pack import prepare_step17d_official_data_population_pack
from src.official.promotion import can_promote_to_official_final, load_official_final_mode, promote_to_official_final

st.set_page_config(page_title="Official Data Population", layout="wide")

st.title("📋 Official Data Population - Step 17D")

st.markdown("""
### Manual FIFA Data Population Workflow

This page helps you fill, validate, preview, and apply verified World Cup 2026 data.

**Important:** The app does **not** scrape websites, use OCR, or auto-fetch FIFA data.
You must manually copy data from official FIFA sources into the import templates.
""")

POPULATION_DIR = PROJECT_ROOT / OFFICIAL_POPULATION_DIR
TEMPLATES_DIR = PROJECT_ROOT / OFFICIAL_IMPORT_TEMPLATES_DIR
WORKBOOK_DIR = PROJECT_ROOT / OFFICIAL_POPULATION_WORKBOOK_DIR
REPORTS_DIR = PROJECT_ROOT / OFFICIAL_POPULATION_REPORTS_DIR

# ===== OVERVIEW =====
st.header("1. Overview")

col1, col2 = st.columns(2)
with col1:
    st.info("**sample mode** — bundled fallback data for development")
    st.info("**official_draft** — official structure, partially filled")
with col2:
    st.warning("**official_final** — blocked until all readiness checks pass")

# ===== GENERATE PACK =====
st.header("2. Generate Population Pack")

if st.button("🚀 Generate Population Pack", use_container_width=True):
    with st.spinner("Generating population pack..."):
        result = prepare_step17d_official_data_population_pack()
        st.session_state.population_pack = result
    st.success(f"Population pack ready: {result.get('status')}")
    st.rerun()

if "population_pack" in st.session_state:
    pack = st.session_state.population_pack
    st.json({k: pack[k] for k in ("status", "final_ready", "teams_count", "fixtures_count", "players_count") if k in pack})

# ===== STATUS CARDS =====
st.header("3. Population Status")

status = load_population_status()
summary = summarize_population_status(status)
final_mode = load_official_final_mode()
readiness = evaluate_official_final_readiness()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Overall Status", summary.get("overall_status", "unknown"))
c2.metric("Steps Completed", f"{summary.get('completed_steps', 0)}/{summary.get('total_steps', 0)}")
c3.metric("Final Ready", "Yes" if readiness.get("is_official_final_ready") else "No")
c4.metric("official_final Enabled", "Yes" if final_mode.get("official_final_enabled") else "No")

# ===== CHECKLIST =====
st.header("4. Required Data Checklist")

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

# ===== DOWNLOADS =====
st.header("5. Download Templates & Guides")

guide_path = POPULATION_DIR / OFFICIAL_POPULATION_GUIDE_FILE
workbook_path = WORKBOOK_DIR / OFFICIAL_MASTER_IMPORT_WORKBOOK_FILE
readme_path = WORKBOOK_DIR / OFFICIAL_MASTER_IMPORT_README_FILE

col1, col2, col3 = st.columns(3)
with col1:
    if guide_path.is_file():
        st.download_button("📄 Population Guide", guide_path.read_text(encoding="utf-8"),
                           file_name=OFFICIAL_POPULATION_GUIDE_FILE, mime="text/markdown")
    else:
        st.caption("Generate pack to create guide")

with col2:
    if workbook_path.is_file():
        st.download_button("📊 Master Workbook", workbook_path.read_bytes(),
                           file_name=OFFICIAL_MASTER_IMPORT_WORKBOOK_FILE,
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    elif readme_path.is_file():
        st.download_button("📄 Workbook README (fallback)", readme_path.read_text(encoding="utf-8"),
                           file_name=OFFICIAL_MASTER_IMPORT_README_FILE, mime="text/markdown")
    else:
        st.caption("Generate pack to create workbook")

with col3:
    if TEMPLATES_DIR.is_dir():
        templates = list(TEMPLATES_DIR.glob("*.csv"))
        st.caption(f"{len(templates)} CSV templates in {TEMPLATES_DIR.name}/")
        for tpl in templates[:3]:
            st.caption(f"  • {tpl.name}")

st.subheader("CSV Templates")
if TEMPLATES_DIR.is_dir():
    for name, filename in OFFICIAL_POPULATION_TEMPLATE_FILES.items():
        tpl_path = TEMPLATES_DIR / filename
        if tpl_path.is_file():
            st.download_button(
                f"Download {filename}",
                tpl_path.read_bytes(),
                file_name=filename,
                mime="text/csv",
                key=f"dl_{name}",
            )

# ===== MISSING DATA =====
st.header("6. Missing-Data Report")

missing_path = REPORTS_DIR / OFFICIAL_POPULATION_MISSING_DATA_REPORT_FILE
if st.button("🔄 Refresh Missing-Data Report"):
    missing_df = build_official_missing_data_report()
    save_missing_data_report(missing_df)
    st.rerun()

if missing_path.is_file():
    missing_df = pd.read_csv(missing_path)
    st.metric("Total issues", len(missing_df))
    if not missing_df.empty:
        severity_counts = missing_df["severity"].value_counts().to_dict()
        st.write(f"Errors: {severity_counts.get('error', 0)} | Warnings: {severity_counts.get('warning', 0)}")
        st.dataframe(missing_df.head(50), use_container_width=True)
else:
    st.info("Generate population pack or refresh to create missing-data report.")

# ===== IMPORT INSTRUCTIONS =====
st.header("7. Import Preview & Apply Instructions")

st.code("""
# Preview before applying
python scripts/preview_official_import.py --target players --file data/official/import_templates/official_players_import_template.csv

# Apply verified import (preview first, then apply for real)
python scripts/apply_official_import.py --target players --file data/official/import_templates/official_players_import_template.csv --preview
python scripts/apply_official_import.py --target players --file data/official/import_templates/official_players_import_template.csv

# Re-check readiness
python scripts/evaluate_official_final_readiness.py
""", language="bash")

st.markdown("""
1. Fill templates from verified FIFA sources
2. Preview diffs before applying
3. Apply imports (automatic backups created)
4. Re-run readiness evaluation
5. Promote only when all checks pass
""")

# ===== FINAL READINESS =====
st.header("8. Final Readiness Status")

final_ready, promo_summary = can_promote_to_official_final()
if final_ready:
    st.success("All readiness checks passed. Promotion is available with confirmation.")
else:
    st.error(f"Promotion blocked. Blockers: {promo_summary.get('blocker_count', 0)}")

if promo_summary.get("blockers"):
    for b in promo_summary["blockers"]:
        st.caption(f"  • {b}")

# ===== PROMOTION =====
st.header("9. Promotion to official_final")

st.warning("Promotion requires explicit confirmation and full readiness. Do not promote with incomplete data.")

if st.button("Check Promotion Status"):
    result = promote_to_official_final(confirmed=False)
    st.write(result.get("message", ""))
    st.json(result.get("readiness_summary", {}))

if final_ready:
    if st.checkbox("I confirm all data is verified against official FIFA sources"):
        if st.button("Promote to official_final"):
            result = promote_to_official_final(confirmed=True)
            if result.get("status") == "promoted":
                st.success("Promoted to official_final!")
            else:
                st.error(result.get("message", "Promotion failed"))
else:
    st.info("Promotion remains blocked until final readiness passes.")

# ===== NEXT STEPS =====
st.header("10. What To Do Next")

if not final_ready:
    st.markdown("""
    1. Generate the population pack if not done yet
    2. Download and fill templates from FIFA sources
    3. Preview and apply imports one dataset at a time
    4. Refresh missing-data and readiness reports
    5. Repeat until all blockers are resolved
    6. **Step 18 (Awards)** must wait until official players are complete
    """)
else:
    st.markdown("""
    All checks passed. You may promote to official_final with confirmation.
    Step 18 (Awards Predictor) can proceed after promotion.
    """)

st.divider()
st.caption("Step 17D: Manual verification workflow. For Step 17E source-assisted FIFA ingestion, see **Source-Assisted Population** page.")

# ===== STEP 17E =====
st.header("11. Step 17E — Source-Assisted FIFA Population")

st.markdown("""
Use official FIFA source snapshots + manual fallback to stage data **before** applying imports.
This does **not** auto-promote `official_final`.
""")

st.code("""
python scripts/prepare_source_population.py
python scripts/prepare_source_population.py --download
python scripts/export_official_import_pack.py
python scripts/apply_staged_official_data.py --target all --preview
""", language="bash")

if st.button("Run Step 17E pack (no download)"):
    from src.official.prepare_source_population import prepare_step17e_source_assisted_population
    with st.spinner("Step 17E..."):
        r = prepare_step17e_source_assisted_population(download_sources=False)
    st.json({k: r[k] for k in ("status", "staged_teams_count", "staged_fixtures_count", "final_ready") if k in r})
