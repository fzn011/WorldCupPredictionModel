"""Step 17G orchestrator: official data import execution workflow."""

from __future__ import annotations

import json
from typing import Any

import src.utils.constants as C
from src.official.final_readiness import evaluate_official_final_readiness
from src.official.import_execution import (
    create_import_execution_summary,
    detect_available_import_inputs,
    run_import_apply_if_ready,
    run_import_preview,
    run_import_staging,
    save_import_execution_report,
)
from src.official.population_completeness import (
    calculate_population_completeness,
    save_population_completeness_report,
)
from src.official.promotion import load_official_final_mode


def prepare_step17g_official_import_execution(
    schedule_file: str | None = None,
    squad_file: str | None = None,
    workbook_file: str | None = None,
    apply: bool = False,
    force_draft_apply: bool = False,
) -> dict[str, Any]:
    """Run Step 17G official data import execution end-to-end."""
    notes: list[str] = []

    inputs = detect_available_import_inputs(schedule_file, squad_file, workbook_file)
    staging_result = run_import_staging(schedule_file, squad_file, workbook_file)
    notes.extend(staging_result.get("notes", []))

    preview_result = run_import_preview()
    metrics, completeness_df = calculate_population_completeness()
    completeness_path = save_population_completeness_report(completeness_df)

    apply_result: dict[str, Any] | None = None
    if apply:
        apply_result = run_import_apply_if_ready(
            force=False,
            force_draft_apply=force_draft_apply,
        )
        notes.extend(apply_result.get("notes", []))
        if apply_result.get("status") == "blocked_not_ready":
            notes.append("Apply blocked because populated official data is incomplete.")

    try:
        readiness_summary = evaluate_official_final_readiness()
    except Exception as exc:
        readiness_summary = {
            "is_official_final_ready": False,
            "status": "blocked",
            "error": str(exc),
            "summary": {"blocker_count": 1, "warning_count": 0},
            "blockers": [{"id": "readiness_evaluation_failed"}],
        }
        notes.append(f"Readiness evaluation error: {exc}")

    summary = create_import_execution_summary(
        staging_result,
        preview_result,
        apply_result,
        readiness_summary,
    )
    summary["inputs"] = inputs
    summary["staging_validation_passed"] = staging_result.get("staging_validation_passed", False)
    summary["preview_status"] = preview_result.get("status")
    summary["completeness_report_path"] = completeness_path
    summary["final_readiness_report_path"] = str(
        C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR / C.OFFICIAL_FINAL_READINESS_REPORT_FILE
    )
    summary["import_execution_report_path"] = save_import_execution_report(summary)
    summary["notes"] = notes

    return summary


if __name__ == "__main__":
    print(json.dumps(prepare_step17g_official_import_execution(), indent=2))
