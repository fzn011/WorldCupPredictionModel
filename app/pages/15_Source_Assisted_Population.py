"""Streamlit page: Source-Assisted Official FIFA Data Population (Step 17E)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from src.utils.constants import (
    PROJECT_ROOT,
    OFFICIAL_SOURCE_DATA_DIR,
    OFFICIAL_SOURCE_STAGING_DIR,
    OFFICIAL_SOURCE_REPORTS_DIR,
    OFFICIAL_SOURCE_EXPORTS_DIR,
    OFFICIAL_DOWNLOADABLE_IMPORT_PACK_FILE,
    OFFICIAL_FIFA_SOURCE_URLS,
    STAGED_OFFICIAL_TEAMS_FILE,
    STAGED_OFFICIAL_FIXTURES_FILE,
    STAGED_OFFICIAL_VENUES_FILE,
    STAGED_OFFICIAL_PLAYERS_FILE,
)
from src.official.final_readiness import evaluate_official_final_readiness
from src.official.import_pack import create_import_pack_zip
from src.official.prepare_source_population import prepare_step17e_source_assisted_population
from src.official.source_registry import load_official_source_registry
from src.official.staging_validation import load_staged_data, validate_all_staged_data

st.set_page_config(page_title="Source-Assisted Population", layout="wide")

st.title("🌐 Source-Assisted Official FIFA Data Population — Step 17E")

st.markdown("""
Populate official World Cup 2026 data using **official FIFA sources first**, with manual CSV/XLSX fallback.

**Policy:** No whole-internet scraping. Only `fifa.com` / `fdp.fifa.org` URLs or user-provided files.
**Important:** This page does **not** auto-promote `official_final`. Inspect staged data before applying.
""")

SOURCE_DIR = PROJECT_ROOT / OFFICIAL_SOURCE_DATA_DIR
STAGING_DIR = PROJECT_ROOT / OFFICIAL_SOURCE_STAGING_DIR
REPORTS_DIR = PROJECT_ROOT / OFFICIAL_SOURCE_REPORTS_DIR
EXPORTS_DIR = PROJECT_ROOT / OFFICIAL_SOURCE_EXPORTS_DIR

# 1 Overview
st.header("1. Overview")
readiness = evaluate_official_final_readiness()
st.metric("Readiness checks passed", f"{readiness.get('passed_checks', 0)}/{readiness.get('total_checks', 15)}")
st.metric("official_final ready", "Yes" if readiness.get("is_official_final_ready") else "No — expected until data complete")

# 2 Source registry
st.header("2. Official Source Registry")
registry = load_official_source_registry()
sources_df = pd.DataFrame(
    [
        {
            "source": name,
            "url": info.get("url", ""),
            "status": info.get("source_status", ""),
            "last_checked": info.get("last_checked_at", ""),
        }
        for name, info in registry.get("sources", {}).items()
    ]
)
st.dataframe(sources_df, use_container_width=True)
with st.expander("Configured FIFA URLs"):
    for k, v in OFFICIAL_FIFA_SOURCE_URLS.items():
        st.caption(f"**{k}:** {v}")

# 3 Generate pack
st.header("3. Generate Source Population Pack")
dl = st.checkbox("Download official FIFA source snapshots", value=False)
force = st.checkbox("Force re-download", value=False)
if st.button("Generate source population pack", use_container_width=True):
    with st.spinner("Running Step 17E orchestrator..."):
        result = prepare_step17e_source_assisted_population(
            download_sources=dl,
            parse_sources=True,
            create_pack=True,
            force_download=force,
        )
        st.session_state["step17e_result"] = result
    st.success(f"Status: {result.get('status')}")
    st.rerun()

if "step17e_result" in st.session_state:
    st.json({k: st.session_state["step17e_result"][k] for k in (
        "status", "staged_teams_count", "staged_fixtures_count",
        "staged_venues_count", "staged_players_count", "parse_warnings_count",
        "final_ready", "import_pack_path",
    ) if k in st.session_state["step17e_result"]})

# 4 Manual ingestion
st.header("4. Manual Workbook / CSV Fallback")
st.code("""
python scripts/ingest_manual_official_file.py --target workbook \\
  --file data/official/population/workbooks/official_worldcup_2026_master_import.xlsx
python scripts/ingest_manual_official_file.py --target players \\
  --file data/official/import_templates/official_players_import_template.csv
""", language="bash")

# 5 Staged preview
st.header("5. Staged Data Preview")
staged = load_staged_data()
if not staged:
    st.warning("No staged files yet. Run pack generation or manual ingestion.")
else:
    for name, df in staged.items():
        st.subheader(name.title())
        st.dataframe(df.head(25), use_container_width=True)
        st.caption(f"{len(df)} rows")

# 6 Validation
st.header("6. Staging Validation")
passed, val_report = validate_all_staged_data()
if val_report.empty:
    st.info("No validation report yet.")
else:
    st.metric("Staging validation passed", passed)
    st.dataframe(val_report.head(40), use_container_width=True)

# 7 Export pack
st.header("7. Export Import Pack")
pack_path = EXPORTS_DIR / OFFICIAL_DOWNLOADABLE_IMPORT_PACK_FILE
if st.button("Build / refresh import pack ZIP"):
    path = create_import_pack_zip()
    st.success(f"Pack written: {path}")
    st.rerun()
if pack_path.is_file():
    st.download_button(
        "Download import pack",
        pack_path.read_bytes(),
        file_name=OFFICIAL_DOWNLOADABLE_IMPORT_PACK_FILE,
        mime="application/zip",
    )

# 8 Apply instructions
st.header("8. Apply Staged Data (manual confirmation required)")
st.code("""
python scripts/apply_staged_official_data.py --target all --preview
python scripts/apply_staged_official_data.py --target all --apply
python scripts/evaluate_official_final_readiness.py
""", language="bash")
st.warning("Do not apply until staged data is reviewed against official FIFA sources.")

# 9 Final readiness
st.header("9. Final Readiness Summary")
if not readiness.get("is_official_final_ready"):
    st.error("official_final is correctly BLOCKED while data is incomplete.")
    for b in readiness.get("blockers", [])[:8]:
        st.caption(f"• {b.get('id', b)}")
else:
    st.success("All checks passed — promotion available via Official Data Population page.")

st.divider()
st.caption("Step 17E: Source-assisted ingestion only. Step 18 Awards remains blocked until official_final.")
