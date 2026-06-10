#!/usr/bin/env python
"""Ingest manual CSV/XLSX or master workbook into Step 17E staging."""

from __future__ import annotations

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import src.utils.constants as C
from src.official.manual_file_ingestion import ingest_manual_official_file, ingest_master_workbook
from src.official.staging_validation import save_staging_validation_report, validate_all_staged_data


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Ingest manual official file into staging")
    parser.add_argument("--target", "-t", required=True, help="teams|groups|fixtures|venues|players|player_priors|workbook")
    parser.add_argument("--file", "-f", required=True, help="Path to CSV, XLSX, or master workbook")
    args = parser.parse_args()

    print("=" * 60)
    print("Step 17E: Manual Official File Ingestion")
    print("=" * 60)

    if args.target == "workbook":
        result = ingest_master_workbook(args.file)
        print(f"Success: {result.get('success')}")
        if result.get("errors"):
            for err in result["errors"]:
                print(f"  ERROR: {err}")
        for sheet, info in result.get("sheets", {}).items():
            print(f"  Sheet {sheet}: {info}")
    else:
        result = ingest_manual_official_file(args.file, args.target)
        print(f"Success: {result.get('success')}")
        if result.get("errors"):
            for err in result["errors"]:
                print(f"  ERROR: {err}")
        print(f"Staged path: {result.get('staged_path')}")
        print(f"Rows:        {result.get('rows', 0)}")

    passed, report = validate_all_staged_data()
    report_path = save_staging_validation_report(report)
    print(f"\nStaging validation passed: {passed}")
    print(f"Validation report:         {report_path}")

    staging = C.PROJECT_ROOT / C.OFFICIAL_SOURCE_STAGING_DIR
    staged_name = {
        "teams": C.STAGED_OFFICIAL_TEAMS_FILE,
        "groups": C.STAGED_OFFICIAL_GROUPS_FILE,
        "fixtures": C.STAGED_OFFICIAL_FIXTURES_FILE,
        "venues": C.STAGED_OFFICIAL_VENUES_FILE,
        "players": C.STAGED_OFFICIAL_PLAYERS_FILE,
        "player_priors": C.STAGED_PLAYER_AWARD_PRIORS_FILE,
    }.get(args.target, "")
    if staged_name:
        print(
            f"\nNext: python scripts/preview_official_import.py "
            f"--target {args.target} --file {staging / staged_name}"
        )
    print("=" * 60)


if __name__ == "__main__":
    main()
