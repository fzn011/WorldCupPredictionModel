"""Step 17E orchestrator: source-assisted official FIFA data population."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import src.utils.constants as C
from src.official.final_readiness import evaluate_official_final_readiness
from src.official.import_pack import create_import_pack_summary, create_import_pack_zip
from src.official.prepare_population_pack import prepare_step17d_official_data_population_pack
from src.official.source_downloader import download_all_official_sources, ensure_source_dirs
from src.official.source_parsers import build_source_coverage_report, parse_all_source_snapshots
from src.official.source_registry import load_official_source_registry
from src.official.staging_validation import (
    load_staged_data,
    save_staging_validation_report,
    validate_all_staged_data,
)


def _reports_dir() -> Path:
    p = C.PROJECT_ROOT / C.OFFICIAL_SOURCE_REPORTS_DIR
    p.mkdir(parents=True, exist_ok=True)
    return p


def prepare_step17e_source_assisted_population(
    download_sources: bool = False,
    parse_sources: bool = True,
    create_pack: bool = True,
    force_download: bool = False,
) -> dict[str, Any]:
    """Run Step 17E source-assisted population workflow."""
    notes: list[str] = []
    ensure_source_dirs()
    registry = load_official_source_registry()

    downloaded_sources: dict[str, Any] = {}
    if download_sources:
        dl = download_all_official_sources(force=force_download)
        downloaded_sources = dl.get("results", {})
        failed = [k for k, v in downloaded_sources.items() if not v.get("success")]
        if failed:
            notes.append(
                f"Some FIFA source downloads failed or were skipped: {', '.join(failed)}. "
                "Use manual workbook/CSV fallback."
            )
    else:
        notes.append("Source download skipped; using existing snapshots or manual staging only.")

    parsed_sources: dict[str, Any] = {}
    parse_warnings_count = 0
    if parse_sources:
        parsed_sources = parse_all_source_snapshots()
        parse_warnings_count = parsed_sources.get("parse_warnings_count", 0)
        if parse_warnings_count:
            notes.append(
                f"Parsing produced {parse_warnings_count} partial/warning rows; inspect parse report."
            )
    else:
        notes.append("Source parsing skipped.")

    staged = load_staged_data()
    staged_counts = {
        "teams": len(staged.get("teams", [])),
        "groups": len(staged.get("groups", [])),
        "fixtures": len(staged.get("fixtures", [])),
        "venues": len(staged.get("venues", [])),
        "players": len(staged.get("players", [])),
    }

    coverage_df = build_source_coverage_report(staged_counts)
    coverage_path = _reports_dir() / C.OFFICIAL_SOURCE_COVERAGE_REPORT_FILE
    coverage_df.to_csv(coverage_path, index=False)

    staging_validation_passed, validation_report = validate_all_staged_data(strict_final=False)
    save_staging_validation_report(validation_report)

    try:
        prepare_step17d_official_data_population_pack()
    except Exception as exc:
        notes.append(f"Population pack refresh note: {exc}")

    import_pack_path = ""
    if create_pack:
        import_pack_path = create_import_pack_zip()
        create_import_pack_summary()

    try:
        readiness = evaluate_official_final_readiness()
    except Exception as exc:
        readiness = {
            "is_official_final_ready": False,
            "status": "blocked",
            "error": str(exc),
        }
        notes.append(f"Readiness evaluation error (official_final remains blocked): {exc}")
    final_ready = bool(readiness.get("is_official_final_ready", False))
    if not final_ready:
        notes.append(
            "official_final remains BLOCKED until all readiness checks pass. "
            "This is correct — do not fake readiness."
        )

    if not staged_counts["players"]:
        notes.append("Staged players count is 0 — squad data likely requires manual FIFA import.")

    if staging_validation_passed and all(staged_counts.get(k, 0) > 0 for k in ("teams", "groups", "fixtures")):
        status = "source_population_ready"
    elif parsed_sources or staged_counts.get("teams", 0) > 0:
        status = "needs_manual_review"
    else:
        status = "needs_manual_review"

    summary = {
        "status": status,
        "registry_path": str(C.PROJECT_ROOT / C.OFFICIAL_SOURCE_DATA_DIR / C.OFFICIAL_SOURCE_REGISTRY_FILE),
        "downloaded_sources": downloaded_sources,
        "parsed_sources": {k: v for k, v in parsed_sources.items() if k != "staged_paths"},
        "staged_teams_count": staged_counts["teams"],
        "staged_groups_count": staged_counts["groups"],
        "staged_fixtures_count": staged_counts["fixtures"],
        "staged_venues_count": staged_counts["venues"],
        "staged_players_count": staged_counts["players"],
        "staging_validation_passed": staging_validation_passed,
        "parse_warnings_count": parse_warnings_count,
        "coverage_report_path": str(coverage_path),
        "import_pack_path": import_pack_path,
        "final_ready": final_ready,
        "official_final_status": readiness.get("status", "blocked"),
        "notes": notes,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    summary_path = _reports_dir() / C.OFFICIAL_SOURCE_POPULATION_SUMMARY_FILE
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    summary["summary_path"] = str(summary_path)
    return summary


if __name__ == "__main__":
    print(json.dumps(prepare_step17e_source_assisted_population(), indent=2))
