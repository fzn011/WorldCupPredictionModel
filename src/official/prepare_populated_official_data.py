"""Step 17F orchestrator: populate official FIFA World Cup 2026 data."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C
from src.official.apply_imports import apply_official_import_file
from src.official.final_readiness import evaluate_official_final_readiness
from src.official.fifa_schedule_importer import (
    normalize_schedule_to_official_schema,
    save_populated_schedule_outputs,
)
from src.official.fifa_squad_importer import (
    normalize_squad_to_official_schema,
    save_populated_squad_outputs,
)
from src.official.populated_data_builder import (
    build_all_populated_official_data,
    create_official_ready_import_pack,
)
from src.official.population_completeness import (
    calculate_population_completeness,
    population_is_ready_for_apply,
    save_population_completeness_report,
)
from src.official.prepare_squads import prepare_step17b_official_squads_and_priors


def _ensure_dirs() -> None:
    for rel in (
        C.OFFICIAL_POPULATED_DATA_DIR,
        C.OFFICIAL_POPULATED_REPORTS_DIR,
        C.OFFICIAL_POPULATED_EXPORTS_DIR,
    ):
        (C.PROJECT_ROOT / rel).mkdir(parents=True, exist_ok=True)


def _populated_dir() -> Path:
    return C.PROJECT_ROOT / C.OFFICIAL_POPULATED_DATA_DIR


def _apply_populated_files() -> dict[str, Any]:
    """Apply populated CSVs through safe import workflow."""
    mapping = {
        "teams": C.POPULATED_OFFICIAL_TEAMS_FILE,
        "groups": C.POPULATED_OFFICIAL_GROUPS_FILE,
        "venues": C.POPULATED_OFFICIAL_VENUES_FILE,
        "fixtures": C.POPULATED_OFFICIAL_FIXTURES_FILE,
        "players": C.POPULATED_OFFICIAL_PLAYERS_FILE,
        "player_priors": C.POPULATED_PLAYER_AWARD_PRIORS_FILE,
    }
    results: dict[str, Any] = {}
    for target, filename in mapping.items():
        path = _populated_dir() / filename
        if not path.is_file():
            results[target] = {"success": False, "error": f"Missing {path}"}
            continue
        results[target] = apply_official_import_file(
            path,
            template_type=target,
            create_backup=True,
            re_prepare=False,
        )
    prepare_step17b_official_squads_and_priors()
    return results


def prepare_step17f_populated_official_data(
    schedule_file: str | None = None,
    squad_file: str | None = None,
    apply_if_complete: bool = False,
) -> dict[str, Any]:
    """Run Step 17F populated official data workflow."""
    _ensure_dirs()
    notes: list[str] = []

    if schedule_file:
        if schedule_file.lower().endswith((".xlsx", ".xls")):
            schedule_raw = pd.read_excel(schedule_file)
        else:
            schedule_raw = pd.read_csv(schedule_file)
        fixtures_df, venues_df, audit_df = normalize_schedule_to_official_schema(schedule_raw)
        save_populated_schedule_outputs(fixtures_df, venues_df, audit_df)
        notes.append(f"Schedule file imported: {schedule_file}")

    if squad_file:
        raw = pd.read_excel(squad_file) if squad_file.lower().endswith((".xlsx", ".xls")) else pd.read_csv(squad_file)
        players_df, audit_df = normalize_squad_to_official_schema(raw)
        save_populated_squad_outputs(players_df, audit_df)
        notes.append(f"Squad file imported: {squad_file}")

    build_result = build_all_populated_official_data()
    metrics, report_df = calculate_population_completeness()
    completeness_path = save_population_completeness_report(report_df)
    import_pack_path = create_official_ready_import_pack()

    ready = population_is_ready_for_apply(metrics)
    applied = False
    status = "needs_more_data"

    if apply_if_complete:
        if ready:
            apply_results = _apply_populated_files()
            applied = all(r.get("success") for r in apply_results.values() if isinstance(r, dict))
            status = "applied" if applied else "failed"
            if not applied:
                notes.append("Apply attempted but one or more imports failed.")
        else:
            notes.append("Apply skipped — population not ready (blocking metrics remain).")
    elif ready:
        status = "ready_for_apply"
        notes.append("Population complete — run apply_populated_official_data.py --apply to promote.")

    if not ready:
        blockers = report_df[report_df["blocking"] == True]["category"].tolist()  # noqa: E712
        notes.append(f"Blocking categories: {', '.join(blockers) if blockers else 'see completeness report'}")
        notes.append("official_final must remain blocked until all data is verified.")

    try:
        readiness = evaluate_official_final_readiness()
    except Exception as exc:
        readiness = {"is_official_final_ready": False, "status": "blocked", "error": str(exc)}
        notes.append(f"Readiness evaluation error (official_final remains blocked): {exc}")
    final_ready = bool(readiness.get("is_official_final_ready", False))

    summary = {
        "status": status,
        "ready_for_apply": ready,
        "applied": applied,
        "teams_count": metrics.get("teams_count", 0),
        "fixtures_count": metrics.get("fixtures_count", 0),
        "group_stage_fixtures_count": metrics.get("group_stage_fixtures_count", 0),
        "knockout_fixtures_count": metrics.get("knockout_fixtures_count", 0),
        "venues_count": metrics.get("venues_count", 0),
        "players_count": metrics.get("players_count", 0),
        "teams_with_26_players": metrics.get("teams_with_26_players", 0),
        "sample_to_be_verified_count": metrics.get("sample_to_be_verified_count", 0),
        "placeholder_issues_count": metrics.get("placeholder_issues_count", 0),
        "completeness_report_path": completeness_path,
        "import_pack_path": import_pack_path,
        "final_ready": final_ready,
        "build_paths": build_result.get("paths", {}),
        "notes": notes,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    summary_path = C.PROJECT_ROOT / C.OFFICIAL_POPULATED_REPORTS_DIR / C.OFFICIAL_POPULATION_FINAL_SUMMARY_FILE
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    summary["summary_path"] = str(summary_path)
    return summary


if __name__ == "__main__":
    print(json.dumps(prepare_step17f_populated_official_data(), indent=2))
