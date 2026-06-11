"""Streamlit page: Official Data Population Completion."""

from __future__ import annotations

import json
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
        render_warning_panel,
    )
except ModuleNotFoundError:
    from components.ui import (
        inject_page_theme,
        render_download_card,
        render_hero,
        render_metric_card,
        render_section_header,
        render_warning_panel,
    )

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
    OFFICIAL_POPULATION_FINAL_SUMMARY_FILE,
    OFFICIAL_READY_IMPORT_PACK_FILE,
)
from src.official.final_readiness import evaluate_official_final_readiness
from src.official.fifa_schedule_importer import normalize_schedule_to_official_schema, save_populated_schedule_outputs
from src.official.fifa_squad_importer import normalize_squad_to_official_schema, save_populated_squad_outputs
from src.official.prepare_populated_official_data import prepare_step17f_populated_official_data
from src.official.population_completeness import calculate_population_completeness
from src.official.prepare_import_execution import prepare_step17g_official_import_execution
from src.official.blocker_cleanup import analyze_apply_blockers, apply_safe_blocker_cleanups, save_blocker_cleanup_report
from src.official.loaders import get_official_team_list
from src.official.population_completeness import create_population_completeness_report


inject_page_theme()
render_hero(
    "Population Completion",
    "Build populated official import files from FIFA schedule/squad uploads. No auto-apply — official_final stays gated.",
    eyebrow="Population completion",
)
render_warning_panel(
    "Step 18 Awards must wait until official_final readiness passes. Uploads stage data only until you explicitly apply."
)

POP_DIR = PROJECT_ROOT / OFFICIAL_POPULATED_DATA_DIR
REP_DIR = PROJECT_ROOT / OFFICIAL_POPULATED_REPORTS_DIR
EXP_DIR = PROJECT_ROOT / OFFICIAL_POPULATED_EXPORTS_DIR

readiness = evaluate_official_final_readiness()
_readiness_summary = readiness.get("summary", {})
metrics, report_df = calculate_population_completeness()

tab_build, tab_complete, tab_workflow = st.tabs(["Upload & build", "Completeness", "Import & cleanup"])

with tab_build:
    render_section_header("Overview")
    c1, c2 = st.columns(2)
    with c1:
        render_metric_card(
            "Checks passed",
            f"{_readiness_summary.get('passed_checks', 0)}/{_readiness_summary.get('total_checks', 15)}",
        )
    with c2:
        render_metric_card(
            "official_final ready",
            "Yes" if readiness.get("is_official_final_ready") else "No",
        )

    summary_path = REP_DIR / OFFICIAL_POPULATION_FINAL_SUMMARY_FILE
    if summary_path.is_file():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        st.json({k: summary[k] for k in ("status", "ready_for_apply", "teams_count", "fixtures_count", "players_count") if k in summary})

    render_section_header("Upload official FIFA schedule")
    schedule_upload = st.file_uploader("FIFA schedule CSV/XLSX", type=["csv", "xlsx", "xls"], key="sched17f")
    if schedule_upload and st.button("Import schedule to populated fixtures", key="import_sched_17f"):
        tmp = POP_DIR / "_upload_schedule" / schedule_upload.name
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_bytes(schedule_upload.getvalue())
        raw = pd.read_excel(tmp) if tmp.suffix.lower() in {".xlsx", ".xls"} else pd.read_csv(tmp)
        fdf, vdf, audit = normalize_schedule_to_official_schema(raw)
        save_populated_schedule_outputs(fdf, vdf, audit)
        st.success(f"Imported {len(fdf)} fixtures, {len(vdf)} venues (staged only — not applied).")

    render_section_header("Upload official FIFA squad file")
    squad_upload = st.file_uploader("FIFA squad CSV/XLSX", type=["csv", "xlsx", "xls"], key="squad17f")
    if squad_upload and st.button("Import squad to populated players", key="import_squad_17f"):
        tmp = POP_DIR / "_upload_squad" / squad_upload.name
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_bytes(squad_upload.getvalue())
        raw = pd.read_excel(tmp) if tmp.suffix.lower() in {".xlsx", ".xls"} else pd.read_csv(tmp)
        pdf, audit = normalize_squad_to_official_schema(raw)
        save_populated_squad_outputs(pdf, audit)
        st.success(f"Imported {len(pdf)} players (staged only — not applied).")

    render_section_header("Build populated official data")
    if st.button("Run populated-data builder", use_container_width=True, key="build_17f"):
        with st.spinner("Building populated datasets..."):
            st.session_state["step17f_result"] = prepare_step17f_populated_official_data()
        st.rerun()

    if "step17f_result" in st.session_state:
        st.json(st.session_state["step17f_result"])

with tab_complete:
    render_section_header("Completeness dashboard")
    metrics, report_df = calculate_population_completeness()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Teams", str(metrics.get("teams_count", 0)), sub="target 48")
    with c2:
        render_metric_card("Fixtures", str(metrics.get("fixtures_count", 0)), sub="target 104")
    with c3:
        render_metric_card("Players", str(metrics.get("players_count", 0)), sub="target 1248")
    with c4:
        render_metric_card("Teams @ 26", str(metrics.get("teams_with_26_players", 0)), sub="target 48")

    if not report_df.empty:
        with st.expander("Completeness report"):
            st.dataframe(report_df, use_container_width=True)

    render_section_header("Blockers")
    blockers = report_df[report_df["blocking"] == True] if not report_df.empty else pd.DataFrame()  # noqa: E712
    if blockers.empty:
        st.success("No blocking completeness issues — review readiness before apply.")
    else:
        st.warning("Official final mode must remain blocked. Complete missing data first.")
        for _, row in blockers.iterrows():
            st.caption(f"• **{row['category']}**: {row['actual']} / {row['target']} — {row['notes']}")

    render_section_header("Populated data previews")
    for label, fname in (
        ("Teams", POPULATED_OFFICIAL_TEAMS_FILE),
        ("Groups", POPULATED_OFFICIAL_GROUPS_FILE),
        ("Fixtures", POPULATED_OFFICIAL_FIXTURES_FILE),
        ("Venues", POPULATED_OFFICIAL_VENUES_FILE),
        ("Players", POPULATED_OFFICIAL_PLAYERS_FILE),
    ):
        path = POP_DIR / fname
        if path.is_file():
            with st.expander(label):
                st.dataframe(pd.read_csv(path).head(20), use_container_width=True)

    render_section_header("Export import pack")
    pack = EXP_DIR / OFFICIAL_READY_IMPORT_PACK_FILE
    render_download_card("Official-ready import pack", OFFICIAL_READY_IMPORT_PACK_FILE, pack, mime="application/zip")

with tab_workflow:
    render_section_header("Apply preview instructions")
    st.code("""
python scripts/apply_populated_official_data.py --preview
python scripts/apply_populated_official_data.py --apply
python scripts/evaluate_official_final_readiness.py
    """, language="bash")
    render_warning_panel("Do not apply until populated data is complete and verified against FIFA sources.")

    render_section_header("Final readiness status")
    if readiness.get("is_official_final_ready"):
        st.success("All readiness checks passed.")
    else:
        st.error("official_final is BLOCKED.")
        for b in readiness.get("blockers", [])[:10]:
            st.caption(f"• {b.get('name', b.get('id', b))}")

    render_section_header("Next action")
    ready = metrics.get("teams_count", 0) >= 48 and metrics.get("players_count", 0) >= 1248
    if ready and not readiness.get("is_official_final_ready"):
        st.info("Data counts look complete — verify sources, run apply preview, then apply if diffs look correct.")
    elif metrics.get("players_count", 0) < 1248:
        st.info("Upload official FIFA squad file(s) or fill squad import template, then rebuild.")
    elif metrics.get("fixtures_count", 0) < 104:
        st.info("Upload official FIFA schedule file, then rebuild.")
    else:
        st.info("Continue filling verified official data from FIFA sources.")

    render_section_header("Step 17G — import execution")
    st.caption("Stage schedule/squad/workbook files, preview diffs, optionally apply when ready.")
    exec_schedule = st.file_uploader("Schedule file (17G)", type=["csv", "xlsx", "xls"], key="exec_sched")
    exec_squad = st.file_uploader("Squad file (17G)", type=["csv", "xlsx", "xls"], key="exec_squad")
    exec_workbook = st.file_uploader("Master workbook (17G)", type=["xlsx", "xls"], key="exec_wb")
    do_apply = st.checkbox("Apply if ready (17G)", value=False)

    if st.button("Stage and preview import (17G)", use_container_width=True, key="exec_17g"):
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
        with st.spinner("Running import execution..."):
            st.session_state["step17g_result"] = prepare_step17g_official_import_execution(
                schedule_file=sched_path,
                squad_file=squad_path,
                workbook_file=wb_path,
                apply=do_apply,
            )
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

    render_section_header("Step 17H — blocker cleanup")
    metrics_h, _ = calculate_population_completeness()
    h1, h2, h3, h4 = st.columns(4)
    with h1:
        render_metric_card("Total fixtures", str(metrics_h.get("fixtures_count", 0)))
    with h2:
        render_metric_card("Group stage", str(metrics_h.get("group_stage_fixtures_count", 0)))
    with h3:
        render_metric_card("Knockout", str(metrics_h.get("knockout_fixtures_count", 0)))
    with h4:
        render_metric_card("Official teams", str(len(get_official_team_list())))

    if st.button("Analyze apply blockers (17H)", use_container_width=True, key="analyze_17h"):
        _summary, report_df_h = analyze_apply_blockers()
        path = save_blocker_cleanup_report(report_df_h)
        st.session_state["step17h_report"] = report_df_h
        st.session_state["step17h_report_path"] = path
        st.rerun()

    if st.button("Apply safe blocker cleanup (17H)", use_container_width=True, key="apply_17h"):
        with st.spinner("Running safe blocker cleanup..."):
            st.session_state["step17h_result"] = apply_safe_blocker_cleanups()
        st.rerun()

    if "step17h_report" in st.session_state:
        with st.expander("Blocker cleanup report"):
            st.dataframe(st.session_state["step17h_report"], use_container_width=True)

    if "step17h_result" in st.session_state:
        r = st.session_state["step17h_result"]
        st.json({k: r[k] for k in (
            "stages_normalized", "teams_groups_rebuilt", "source_labels_updated",
            "ready_for_apply", "final_ready", "official_final_enabled", "remaining_blockers",
        ) if k in r})
        after = r.get("metrics_after", {})
        report_after = create_population_completeness_report(after)
        blockers_h = report_after[report_after["blocking"] == True]  # noqa: E712
        warnings = report_after[report_after["category"] == "optional_metadata_warnings"]
        st.caption(
            f"True blockers: {len(blockers_h)} | Optional metadata warnings: "
            f"{warnings.iloc[0]['actual'] if not warnings.empty else 0}"
        )
