"""Streamlit page: Official Data Population Completion (Step 17F)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from src.utils.constants import (
    PROJECT_ROOT,
    OFFICIAL_POPULATED_DATA_DIR,
    OFFICIAL_POPULATED_REPORTS_DIR,
    OFFICIAL_POPULATED_EXPORTS_DIR,
    POPULATED_OFFICIAL_TEAMS_FILE,
    POPULATED_OFFICIAL_GROUPS_FILE,
    POPULATED_OFFICIAL_FIXTURES_FILE,
    POPULATED_OFFICIAL_VENUES_FILE,
    POPULATED_OFFICIAL_PLAYERS_FILE,
    OFFICIAL_POPULATION_COMPLETENESS_REPORT_FILE,
    OFFICIAL_POPULATION_FINAL_SUMMARY_FILE,
    OFFICIAL_READY_IMPORT_PACK_FILE,
)
from src.official.final_readiness import evaluate_official_final_readiness
from src.official.fifa_schedule_importer import normalize_schedule_to_official_schema, save_populated_schedule_outputs
from src.official.fifa_squad_importer import normalize_squad_to_official_schema, save_populated_squad_outputs
from src.official.prepare_populated_official_data import prepare_step17f_populated_official_data
from src.official.population_completeness import calculate_population_completeness

st.set_page_config(page_title="Official Data Population", layout="wide")

st.title("📋 Official FIFA Data Population Completion — Step 17F")

st.markdown("""
Build **populated official import files** from FIFA schedule/squad uploads, staged data, and verified sources.

**Policy:** No auto-apply. `official_final` stays blocked until all readiness checks pass. Step 18 Awards must wait.
""")

POP_DIR = PROJECT_ROOT / OFFICIAL_POPULATED_DATA_DIR
REP_DIR = PROJECT_ROOT / OFFICIAL_POPULATED_REPORTS_DIR
EXP_DIR = PROJECT_ROOT / OFFICIAL_POPULATED_EXPORTS_DIR

# 1 Overview
st.header("1. Overview")
readiness = evaluate_official_final_readiness()
st.metric("Readiness checks passed", f"{readiness.get('passed_checks', 0)}/{readiness.get('total_checks', 15)}")
st.metric("official_final ready", "Yes" if readiness.get("is_official_final_ready") else "No — expected until data complete")

summary_path = REP_DIR / OFFICIAL_POPULATION_FINAL_SUMMARY_FILE
if summary_path.is_file():
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    st.json({k: summary[k] for k in ("status", "ready_for_apply", "teams_count", "fixtures_count", "players_count") if k in summary})

# 2 Upload schedule
st.header("2. Upload Official FIFA Schedule File")
schedule_upload = st.file_uploader("FIFA schedule CSV/XLSX", type=["csv", "xlsx", "xls"], key="sched17f")
if schedule_upload and st.button("Import schedule to populated fixtures"):
    tmp = POP_DIR / "_upload_schedule" / schedule_upload.name
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_bytes(schedule_upload.getvalue())
    if tmp.suffix.lower() in {".xlsx", ".xls"}:
        raw = pd.read_excel(tmp)
    else:
        raw = pd.read_csv(tmp)
    fdf, vdf, audit = normalize_schedule_to_official_schema(raw)
    save_populated_schedule_outputs(fdf, vdf, audit)
    st.success(f"Imported {len(fdf)} fixtures, {len(vdf)} venues (staged only — not applied).")

# 3 Upload squad
st.header("3. Upload Official FIFA Squad File")
squad_upload = st.file_uploader("FIFA squad CSV/XLSX", type=["csv", "xlsx", "xls"], key="squad17f")
if squad_upload and st.button("Import squad to populated players"):
    tmp = POP_DIR / "_upload_squad" / squad_upload.name
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_bytes(squad_upload.getvalue())
    if tmp.suffix.lower() in {".xlsx", ".xls"}:
        raw = pd.read_excel(tmp)
    else:
        raw = pd.read_csv(tmp)
    pdf, audit = normalize_squad_to_official_schema(raw)
    save_populated_squad_outputs(pdf, audit)
    st.success(f"Imported {len(pdf)} players (staged only — not applied).")

# 4 Build
st.header("4. Build Populated Official Data")
if st.button("Run populated-data builder", use_container_width=True):
    with st.spinner("Building populated datasets..."):
        result = prepare_step17f_populated_official_data()
        st.session_state["step17f_result"] = result
    st.rerun()

if "step17f_result" in st.session_state:
    st.json(st.session_state["step17f_result"])

# 5 Completeness dashboard
st.header("5. Completeness Dashboard")
metrics, report_df = calculate_population_completeness()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Teams", metrics.get("teams_count", 0), delta=f"target {48}")
c2.metric("Fixtures", metrics.get("fixtures_count", 0), delta=f"target {104}")
c3.metric("Players", metrics.get("players_count", 0), delta=f"target {1248}")
c4.metric("Teams @ 26", metrics.get("teams_with_26_players", 0), delta=f"target {48}")
if not report_df.empty:
    st.dataframe(report_df, use_container_width=True)

# 6 Blockers
st.header("6. Blocker List")
blockers = report_df[report_df["blocking"] == True] if not report_df.empty else pd.DataFrame()  # noqa: E712
if blockers.empty:
    st.success("No blocking completeness issues — review readiness before apply.")
else:
    st.warning("Official final mode must remain blocked. Complete missing data first.")
    for _, row in blockers.iterrows():
        st.caption(f"• **{row['category']}**: {row['actual']} / {row['target']} — {row['notes']}")

# 7 Previews
st.header("7. Populated Data Previews")
for label, fname in (
    ("Teams", POPULATED_OFFICIAL_TEAMS_FILE),
    ("Groups", POPULATED_OFFICIAL_GROUPS_FILE),
    ("Fixtures", POPULATED_OFFICIAL_FIXTURES_FILE),
    ("Venues", POPULATED_OFFICIAL_VENUES_FILE),
    ("Players", POPULATED_OFFICIAL_PLAYERS_FILE),
):
    path = POP_DIR / fname
    if path.is_file():
        st.subheader(label)
        st.dataframe(pd.read_csv(path).head(20), use_container_width=True)

# 8 Export pack
st.header("8. Export Import Pack")
pack = EXP_DIR / OFFICIAL_READY_IMPORT_PACK_FILE
if pack.is_file():
    st.download_button(
        "Download official-ready import pack",
        pack.read_bytes(),
        file_name=OFFICIAL_READY_IMPORT_PACK_FILE,
        mime="application/zip",
    )
else:
    st.info("Run the builder to create the import pack.")

# 9 Apply instructions
st.header("9. Apply Preview Instructions")
st.code("""
python scripts/apply_populated_official_data.py --preview
python scripts/apply_populated_official_data.py --apply
python scripts/evaluate_official_final_readiness.py
""", language="bash")
st.warning("Do not apply until populated data is complete and verified against FIFA sources.")

# 10 Final readiness
st.header("10. Final Readiness Status")
if readiness.get("is_official_final_ready"):
    st.success("All readiness checks passed.")
else:
    st.error("official_final is BLOCKED.")
    for b in readiness.get("blockers", [])[:10]:
        st.caption(f"• {b.get('name', b.get('id', b))}")

# 11 Next action
st.header("11. Next Action Recommendation")
ready = metrics.get("teams_count", 0) >= 48 and metrics.get("players_count", 0) >= 1248
if ready and not readiness.get("is_official_final_ready"):
    st.info("Data counts look complete — verify sources, run apply preview, then apply if diffs look correct.")
elif metrics.get("players_count", 0) < 1248:
    st.info("Upload official FIFA squad file(s) or fill squad import template, then rebuild.")
elif metrics.get("fixtures_count", 0) < 104:
    st.info("Upload official FIFA schedule file, then rebuild.")
else:
    st.info("Continue filling verified official data from FIFA sources.")

st.divider()
st.caption(f"Completeness report: {REP_DIR / OFFICIAL_POPULATION_COMPLETENESS_REPORT_FILE}")

# Step 17G: Import execution
st.header("Step 17G: Run Official Import Execution")
st.markdown("""
Stage official schedule/squad/workbook files, preview diffs, and optionally apply when completeness checks pass.
**Does not force official_final.**
""")

from src.official.prepare_import_execution import prepare_step17g_official_import_execution

exec_schedule = st.file_uploader("Schedule file (17G)", type=["csv", "xlsx", "xls"], key="exec_sched")
exec_squad = st.file_uploader("Squad file (17G)", type=["csv", "xlsx", "xls"], key="exec_squad")
exec_workbook = st.file_uploader("Master workbook (17G)", type=["xlsx", "xls"], key="exec_wb")
do_apply = st.checkbox("Apply if ready (17G)", value=False)

if st.button("Stage and preview import (17G)", use_container_width=True):
    sched_path = squad_path = wb_path = None
    if exec_schedule:
        p = POP_DIR / "_upload_exec" / exec_schedule.name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(exec_schedule.getvalue())
        sched_path = str(p)
    if exec_squad:
        p = POP_DIR / "_upload_exec" / exec_squad.name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(exec_squad.getvalue())
        squad_path = str(p)
    if exec_workbook:
        p = POP_DIR / "_upload_exec" / exec_workbook.name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(exec_workbook.getvalue())
        wb_path = str(p)
    with st.spinner("Running Step 17G import execution..."):
        result = prepare_step17g_official_import_execution(
            schedule_file=sched_path,
            squad_file=squad_path,
            workbook_file=wb_path,
            apply=do_apply,
        )
        st.session_state["step17g_result"] = result
    st.rerun()

if "step17g_result" in st.session_state:
    r = st.session_state["step17g_result"]
    st.json({k: r[k] for k in (
        "status", "staged_fixtures_count", "staged_players_count",
        "populated_fixtures_count", "populated_players_count",
        "teams_with_26_players", "ready_for_apply", "applied",
        "final_ready", "official_final_enabled", "next_action",
    ) if k in r})
    if r.get("ready_for_apply") is False:
        st.warning("Official final mode must remain blocked. Complete missing data first.")
