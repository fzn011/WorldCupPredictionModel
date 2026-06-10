"""Official data import execution orchestrator for Step 17G."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C
from src.official.final_readiness import evaluate_official_final_readiness
from src.official.fifa_schedule_importer import normalize_schedule_to_official_schema
from src.official.fifa_squad_importer import normalize_squad_to_official_schema
from src.official.import_diff import preview_official_import, save_import_diff_report
from src.official.manual_file_ingestion import ingest_master_workbook
from src.official.populated_data_builder import build_all_populated_official_data
from src.official.population_completeness import (
    calculate_population_completeness,
    population_is_ready_for_apply,
    save_population_completeness_report,
)
from src.official.prepare_populated_official_data import prepare_step17f_populated_official_data
from src.official.promotion import load_official_final_mode
from src.official.staging_validation import (
    STAGED_FILES,
    load_staged_data,
    save_staging_validation_report,
    validate_all_staged_data,
)

APPLY_TARGETS = list(C.OFFICIAL_SOURCE_APPLY_ORDER)


def _staging_dir() -> Path:
    p = C.PROJECT_ROOT / C.OFFICIAL_SOURCE_STAGING_DIR
    p.mkdir(parents=True, exist_ok=True)
    return p


def _reports_dir() -> Path:
    p = C.PROJECT_ROOT / C.OFFICIAL_POPULATED_REPORTS_DIR
    p.mkdir(parents=True, exist_ok=True)
    return p


def _read_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    return pd.read_csv(path)


def _stage_dataframe(df: pd.DataFrame, staged_filename: str) -> str:
    out = _staging_dir() / staged_filename
    df.to_csv(out, index=False)
    return str(out)


def detect_available_import_inputs(
    schedule_file: str | None = None,
    squad_file: str | None = None,
    workbook_file: str | None = None,
) -> dict[str, Any]:
    """Detect user-supplied files and existing staged official data."""
    detected: dict[str, str] = {}
    has_schedule = bool(schedule_file and Path(schedule_file).is_file())
    has_squad = bool(squad_file and Path(squad_file).is_file())
    has_workbook = bool(workbook_file and Path(workbook_file).is_file())

    if has_schedule:
        detected["schedule_file"] = str(Path(schedule_file).resolve())
    if has_squad:
        detected["squad_file"] = str(Path(squad_file).resolve())
    if has_workbook:
        detected["workbook_file"] = str(Path(workbook_file).resolve())

    staged_present = {}
    for key, filename in STAGED_FILES.items():
        path = _staging_dir() / filename
        staged_present[key] = path.is_file()
        if path.is_file():
            detected[f"staged_{key}"] = str(path)

    has_staged = any(staged_present.values())
    missing = []
    if not has_schedule and not staged_present.get("fixtures"):
        missing.append("schedule_file_or_staged_fixtures")
    if not has_squad and not staged_present.get("players"):
        missing.append("squad_file_or_staged_players")

    return {
        "has_schedule_file": has_schedule,
        "has_squad_file": has_squad,
        "has_workbook_file": has_workbook,
        "has_staged_data": has_staged,
        "staged_present": staged_present,
        "detected_files": detected,
        "missing_expected_inputs": missing,
    }


def run_import_staging(
    schedule_file: str | None = None,
    squad_file: str | None = None,
    workbook_file: str | None = None,
) -> dict[str, Any]:
    """Stage official import files into Step 17E staging area."""
    notes: list[str] = []
    inputs = detect_available_import_inputs(schedule_file, squad_file, workbook_file)

    if workbook_file and Path(workbook_file).is_file():
        wb_result = ingest_master_workbook(workbook_file)
        if not wb_result.get("success"):
            return {
                "status": "failed",
                "errors": wb_result.get("errors", []),
                "notes": notes,
            }
        notes.append(f"Master workbook ingested: {workbook_file}")

    if schedule_file and Path(schedule_file).is_file():
        raw = _read_table(Path(schedule_file))
        fixtures_df, venues_df, _ = normalize_schedule_to_official_schema(raw)
        _stage_dataframe(fixtures_df, C.STAGED_OFFICIAL_FIXTURES_FILE)
        _stage_dataframe(venues_df, C.STAGED_OFFICIAL_VENUES_FILE)
        notes.append(f"Staged {len(fixtures_df)} fixtures and {len(venues_df)} venues from schedule file")

    if squad_file and Path(squad_file).is_file():
        raw = _read_table(Path(squad_file))
        players_df, _ = normalize_squad_to_official_schema(raw)
        _stage_dataframe(players_df, C.STAGED_OFFICIAL_PLAYERS_FILE)
        notes.append(f"Staged {len(players_df)} players from squad file")

    staged = load_staged_data()
    if not staged and not inputs["has_staged_data"]:
        return {
            "status": "no_input_files",
            "staged_teams_count": 0,
            "staged_fixtures_count": 0,
            "staged_venues_count": 0,
            "staged_players_count": 0,
            "staging_validation_passed": False,
            "staging_report_path": "",
            "notes": ["No schedule/squad/workbook files supplied and no staged data found."],
        }

    staged = load_staged_data()
    passed, validation_report = validate_all_staged_data(strict_final=False)
    staging_report_path = save_staging_validation_report(validation_report)

    try:
        build_all_populated_official_data()
    except Exception as exc:
        notes.append(f"Populated builder note: {exc}")

    return {
        "status": "staged" if staged else "no_input_files",
        "staged_teams_count": len(staged.get("teams", [])),
        "staged_groups_count": len(staged.get("groups", [])),
        "staged_fixtures_count": len(staged.get("fixtures", [])),
        "staged_venues_count": len(staged.get("venues", [])),
        "staged_players_count": len(staged.get("players", [])),
        "staging_validation_passed": passed,
        "staging_report_path": staging_report_path,
        "notes": notes,
    }


def run_import_preview() -> dict[str, Any]:
    """Preview staged official data against current processed official files."""
    staged = load_staged_data()
    if not staged:
        return {
            "status": "no_staged_data",
            "preview_reports": {},
            "added_rows": 0,
            "changed_rows": 0,
            "removed_rows": 0,
            "warnings": ["No staged data available for preview."],
        }

    preview_reports: dict[str, str] = {}
    added = changed = removed = 0
    warnings: list[str] = []

    for target in APPLY_TARGETS:
        filename = STAGED_FILES.get(target)
        if not filename:
            continue
        path = _staging_dir() / filename
        if not path.is_file():
            warnings.append(f"Missing staged file for {target}")
            continue
        try:
            diff_df = preview_official_import(str(path), target)
            preview_reports[target] = save_import_diff_report(diff_df)
            if not diff_df.empty and "change_type" in diff_df.columns:
                added += int((diff_df["change_type"] == "added").sum())
                changed += int((diff_df["change_type"] == "updated").sum())
                removed += int((diff_df["change_type"] == "removed").sum())
        except Exception as exc:
            warnings.append(f"Preview failed for {target}: {exc}")

    populated_dir = C.PROJECT_ROOT / C.OFFICIAL_POPULATED_DATA_DIR
    populated_map = {
        "teams": C.POPULATED_OFFICIAL_TEAMS_FILE,
        "groups": C.POPULATED_OFFICIAL_GROUPS_FILE,
        "fixtures": C.POPULATED_OFFICIAL_FIXTURES_FILE,
        "venues": C.POPULATED_OFFICIAL_VENUES_FILE,
        "players": C.POPULATED_OFFICIAL_PLAYERS_FILE,
        "player_priors": C.POPULATED_PLAYER_AWARD_PRIORS_FILE,
    }
    for target, fname in populated_map.items():
        ppath = populated_dir / fname
        if not ppath.is_file():
            continue
        try:
            diff_df = preview_official_import(str(ppath), target)
            preview_reports[f"populated_{target}"] = save_import_diff_report(diff_df)
            if not diff_df.empty and "change_type" in diff_df.columns:
                added += int((diff_df["change_type"] == "added").sum())
                changed += int((diff_df["change_type"] == "updated").sum())
                removed += int((diff_df["change_type"] == "removed").sum())
        except Exception as exc:
            warnings.append(f"Populated preview failed for {target}: {exc}")

    return {
        "status": "preview_ready",
        "preview_reports": preview_reports,
        "added_rows": added,
        "changed_rows": changed,
        "removed_rows": removed,
        "warnings": warnings,
    }


def run_import_apply_if_ready(force: bool = False, force_draft_apply: bool = False) -> dict[str, Any]:
    """Apply populated official data only when completeness checks pass."""
    metrics, report_df = calculate_population_completeness()
    ready = population_is_ready_for_apply(metrics)
    blockers = (
        report_df[report_df["blocking"] == True]["category"].tolist()  # noqa: E712
        if not report_df.empty
        else []
    )

    if not ready and not force_draft_apply:
        return {
            "status": "blocked_not_ready",
            "applied": False,
            "ready_for_apply": False,
            "final_ready": False,
            "blockers": blockers,
            "apply_report_path": "",
            "notes": ["Apply blocked — populated official data incomplete."],
        }

    if force_draft_apply and not ready:
        notes = [
            "Draft apply requested but population is not complete; "
            "official_final will remain blocked after any partial apply."
        ]
    else:
        notes = []

    result = prepare_step17f_populated_official_data(apply_if_complete=True)
    readiness = evaluate_official_final_readiness()
    final_ready = bool(readiness.get("is_official_final_ready", False))

    apply_report_path = _reports_dir() / C.OFFICIAL_POPULATION_APPLY_REPORT_FILE
    apply_payload = {
        "applied": result.get("applied", False),
        "ready_for_apply": ready,
        "final_ready": final_ready,
        "blockers": blockers,
        "force_draft_apply": force_draft_apply,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    apply_report_path.write_text(json.dumps(apply_payload, indent=2), encoding="utf-8")

    status = "applied_final_ready" if result.get("applied") and final_ready else (
        "applied_but_final_blocked" if result.get("applied") else "blocked_not_ready"
    )

    return {
        "status": status,
        "applied": bool(result.get("applied")),
        "ready_for_apply": ready,
        "final_ready": final_ready,
        "blockers": blockers if not final_ready else [],
        "apply_report_path": str(apply_report_path),
        "notes": notes,
    }


def create_import_execution_summary(
    staging_result: dict[str, Any],
    preview_result: dict[str, Any],
    apply_result: dict[str, Any] | None,
    readiness_summary: dict[str, Any],
) -> dict[str, Any]:
    """Combine staging, preview, apply, and readiness into one summary."""
    metrics, _ = calculate_population_completeness()
    final_mode = load_official_final_mode()
    final_ready = bool(readiness_summary.get("is_official_final_ready", False))
    ready_for_apply = population_is_ready_for_apply(metrics)

    blockers_count = readiness_summary.get("summary", {}).get("blocker_count", 0)
    warnings_count = readiness_summary.get("summary", {}).get("warning_count", 0)

    if staging_result.get("status") == "no_input_files":
        status = "no_input_files"
        next_action = "Provide official FIFA schedule and/or squad files, or fill staged data."
    elif not ready_for_apply:
        status = "staged_needs_review" if staging_result.get("staged_fixtures_count") or staging_result.get("staged_players_count") else "blocked_not_ready"
        next_action = "Complete missing official data, review preview diffs, then re-run readiness."
    elif apply_result and apply_result.get("applied") and final_ready:
        status = "applied_final_ready"
        next_action = "All checks passed — official_final promotion may be available via promote_official_final.py."
    elif apply_result and apply_result.get("applied"):
        status = "applied_but_final_blocked"
        next_action = "Data applied but final readiness blockers remain — resolve before Step 18."
    elif ready_for_apply:
        status = "ready_for_apply"
        next_action = "Run with --apply to import populated official data."
    else:
        status = "blocked_not_ready"
        next_action = "Import official schedule/squad files and rebuild populated data."

    return {
        "status": status,
        "staged_fixtures_count": staging_result.get("staged_fixtures_count", 0),
        "staged_players_count": staging_result.get("staged_players_count", 0),
        "populated_fixtures_count": metrics.get("fixtures_count", 0),
        "populated_players_count": metrics.get("players_count", 0),
        "teams_with_26_players": metrics.get("teams_with_26_players", 0),
        "ready_for_apply": ready_for_apply,
        "applied": bool(apply_result.get("applied")) if apply_result else False,
        "final_ready": final_ready,
        "official_final_enabled": bool(final_mode.get("official_final_enabled", False)),
        "blockers_count": blockers_count,
        "warnings_count": warnings_count,
        "next_action": next_action,
    }


def save_import_execution_report(summary: dict[str, Any], output_path: str | None = None) -> str:
    """Save Step 17G import execution summary JSON."""
    path = Path(output_path) if output_path else _reports_dir() / C.OFFICIAL_IMPORT_EXECUTION_SUMMARY_FILE
    if not path.is_absolute():
        path = C.PROJECT_ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {**summary, "saved_at": datetime.now(timezone.utc).isoformat()}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return str(path)
