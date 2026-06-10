"""Main orchestrator for Step 17D official data population pack."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C
from src.official.final_readiness import evaluate_official_final_readiness, save_final_readiness_report
from src.official.import_templates import generate_all_import_templates
from src.official.master_workbook import generate_population_workbook_pack
from src.official.missing_data import build_official_missing_data_report, save_missing_data_report
from src.official.population_guide import save_population_guide
from src.official.population_status import initialize_population_status, load_population_status, save_population_status


def _ensure_dirs() -> None:
    for rel in (
        C.OFFICIAL_POPULATION_DIR,
        C.OFFICIAL_POPULATION_REPORTS_DIR,
        C.OFFICIAL_POPULATION_WORKBOOK_DIR,
        C.OFFICIAL_IMPORT_TEMPLATES_DIR,
    ):
        (C.PROJECT_ROOT / rel).mkdir(parents=True, exist_ok=True)


def generate_population_import_templates() -> dict[str, Path]:
    """Generate Step 17D import templates with population naming."""
    template_dir = C.PROJECT_ROOT / C.OFFICIAL_IMPORT_TEMPLATES_DIR
    template_dir.mkdir(parents=True, exist_ok=True)

    # Generate using existing Step 17C functions into processed dir, then copy/rename
    processed_dir = C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR
    generated = generate_all_import_templates(output_dir=processed_dir, include_existing_data=True)

    type_map = {
        "teams": "teams",
        "groups": "groups",
        "fixtures": "fixtures",
        "venues": "venues",
        "players": "players",
    }

    result: dict[str, Path] = {}
    for key, src_path in generated.items():
        if key not in type_map:
            continue
        dest_name = C.OFFICIAL_POPULATION_TEMPLATE_FILES[type_map[key]]
        dest_path = template_dir / dest_name
        shutil.copy2(src_path, dest_path)
        result[key] = dest_path

    # Player priors template
    priors_name = C.OFFICIAL_POPULATION_TEMPLATE_FILES["player_priors"]
    priors_path = template_dir / priors_name
    priors_source = C.PROJECT_ROOT / C.PROCESSED_DATA_DIR / C.PLAYER_AWARD_PRIORS_FILE
    if priors_source.is_file():
        shutil.copy2(priors_source, priors_path)
    else:
        df = pd.DataFrame(columns=C.IMPORT_PLAYER_PRIORS_REQUIRED_COLUMNS)
        df.to_csv(priors_path, index=False)
    result["player_priors"] = priors_path

    return result


def _count_issues(missing_df: pd.DataFrame) -> dict[str, int]:
    if missing_df.empty:
        return {"sample_to_be_verified": 0, "placeholder_issues": 0, "errors_count": 0, "warnings_count": 0}

    placeholder = int((missing_df["issue_type"] == "placeholder_value").sum())
    sample = int(
        missing_df["value"].fillna("").astype(str).str.strip().eq("sample_to_be_verified").sum()
    )
    errors = int((missing_df["severity"] == "error").sum())
    warnings = int((missing_df["severity"] == "warning").sum())
    return {
        "sample_to_be_verified": sample,
        "placeholder_issues": placeholder,
        "errors_count": errors,
        "warnings_count": warnings,
    }


def _sync_population_status(readiness: dict[str, Any], missing_df: pd.DataFrame) -> dict[str, Any]:
    status = load_population_status()
    final_ready = bool(readiness.get("is_official_final_ready"))

    fill_map = {
        "fill_teams": "teams",
        "fill_groups": "groups",
        "fill_fixtures": "fixtures",
        "fill_venues": "venues",
        "fill_players": "players",
        "fill_player_priors": "award_candidates",
    }

    for step, dataset in fill_map.items():
        if missing_df.empty:
            status["steps"][step]["status"] = "not_started"
            continue
        ds_issues = missing_df[missing_df["dataset"] == dataset]
        if ds_issues.empty:
            status["steps"][step]["status"] = "imported"
        elif (ds_issues["severity"] == "error").any():
            status["steps"][step]["status"] = "needs_review"
        else:
            status["steps"][step]["status"] = "in_progress"

    if final_ready:
        status["steps"]["run_final_readiness"]["status"] = "final_ready"
        status["steps"]["promote_to_official_final"]["status"] = "ready_for_import"
        status["status"] = "final_ready"
    else:
        status["steps"]["run_final_readiness"]["status"] = "blocked"
        status["steps"]["promote_to_official_final"]["status"] = "blocked"
        status["status"] = "in_progress"

    status["official_final_ready"] = final_ready
    status["notes"] = [
        "Population pack generated. Manual FIFA verification required before official_final.",
    ]
    save_population_status(status)
    return status


def prepare_step17d_official_data_population_pack() -> dict[str, Any]:
    """Generate the full Step 17D official data population pack."""
    _ensure_dirs()

    guide_path = save_population_guide()
    templates = generate_population_import_templates()
    workbook_pack = generate_population_workbook_pack()
    missing_df = build_official_missing_data_report()
    missing_path = save_missing_data_report(missing_df)

    try:
        readiness = evaluate_official_final_readiness()
        readiness_path = save_final_readiness_report(readiness)
    except Exception as exc:
        readiness = {
            "status": "blocked",
            "is_official_final_ready": False,
            "summary": {"teams_count": 0, "players_count": 0, "teams_with_26_players": 0},
            "blockers": [{"id": "validation_failed", "details": {"error": str(exc)}}],
            "warnings": [],
        }
        readiness_path = save_final_readiness_report(readiness)
        notes_on_error = [f"Readiness evaluation error: {exc}"]
    else:
        notes_on_error = []

    issue_counts = _count_issues(missing_df)
    _sync_population_status(readiness, missing_df)

    summary = readiness.get("summary", {})
    official_dir = C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR
    teams_count = summary.get("teams_count", 0)
    players_count = summary.get("players_count", 0)
    fixtures_count = 0
    teams_path = official_dir / C.OFFICIAL_TEAMS_FILE
    players_path = official_dir / C.OFFICIAL_PLAYERS_FILE
    fixtures_df_path = official_dir / C.OFFICIAL_FIXTURES_FILE
    if teams_path.is_file() and teams_count == 0:
        teams_count = len(pd.read_csv(teams_path))
    if players_path.is_file() and players_count == 0:
        players_count = len(pd.read_csv(players_path))
    if fixtures_df_path.is_file():
        fixtures_count = len(pd.read_csv(fixtures_df_path))
    notes = list(workbook_pack.get("notes", []))
    notes.extend(notes_on_error)
    notes.append("Population pack ready. official_final remains blocked until all checks pass.")

    return {
        "status": "population_pack_ready",
        "guide_path": guide_path,
        "template_dir": str(C.PROJECT_ROOT / C.OFFICIAL_IMPORT_TEMPLATES_DIR),
        "templates": {k: str(v) for k, v in templates.items()},
        "workbook_path": workbook_pack.get("workbook_path", ""),
        "workbook_readme_path": workbook_pack.get("readme_path", ""),
        "missing_data_report_path": missing_path,
        "readiness_summary_path": str(readiness_path),
        "final_ready": bool(readiness.get("is_official_final_ready")),
        "errors_count": issue_counts["errors_count"],
        "warnings_count": issue_counts["warnings_count"],
        "sample_to_be_verified_count": issue_counts["sample_to_be_verified"],
        "placeholder_issues_count": issue_counts["placeholder_issues"],
        "teams_count": teams_count,
        "fixtures_count": fixtures_count,
        "players_count": players_count,
        "notes": notes,
    }


if __name__ == "__main__":
    result = prepare_step17d_official_data_population_pack()
    print(json.dumps(result, indent=2))
