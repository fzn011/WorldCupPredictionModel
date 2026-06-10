#!/usr/bin/env python
"""Apply manual import files to update official World Cup 2026 data.

This script applies verified import CSV files and updates the official
data files, optionally re-validating and re-preparing the data.

Usage:
    python scripts/apply_official_import.py <file_or_directory> [--no-backup] [--no-reprepare]
    python scripts/apply_official_import.py --type <type> <file> [--preview]
    python scripts/apply_official_import.py --target players --file <csv> --preview

Examples:
    python scripts/apply_official_import.py import_teams_template.csv
    python scripts/apply_official_import.py --type teams my_teams_data.csv
    python scripts/apply_official_import.py --target players --file data/official/import_templates/official_players_import_template.csv --preview
"""

from __future__ import annotations

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.official.apply_imports import (
    apply_all_imports,
    apply_official_import_file,
    append_import_audit,
    create_import_report,
)
from src.official.final_readiness import evaluate_official_final_readiness
from src.official.import_diff import preview_official_import, save_import_diff_report
from src.official.missing_data import build_official_missing_data_report, save_missing_data_report


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Apply official import files")
    parser.add_argument("path", nargs="?", help="Path to import file or directory")
    parser.add_argument("--file", "-f", help="Path to import file (alternative to positional path)")
    parser.add_argument("--target", "-t",
                        choices=["teams", "groups", "fixtures", "venues", "players", "player_priors", "squads"],
                        help="Import target type")
    parser.add_argument("--type", choices=["teams", "groups", "fixtures", "venues", "players", "player_priors", "squads"],
                        help="Import type (alias for --target)")
    parser.add_argument("--preview", action="store_true", help="Preview diff without applying")
    parser.add_argument("--no-backup", action="store_true", help="Do not create backups")
    parser.add_argument("--no-reprepare", action="store_true", help="Do not re-prepare data after import")
    args = parser.parse_args()

    import_path = args.file or args.path
    template_type = args.target or args.type

    if not import_path:
        parser.error("Provide a file path or use --file")

    print("=" * 60)
    print("FIFA World Cup 2026 - Official Import Applier")
    print("=" * 60)

    path = Path(import_path)

    if not path.exists():
        print(f"\n✗ Path not found: {path}")
        sys.exit(1)

    if args.preview:
        if not template_type:
            print("\n✗ --preview requires --target or --type")
            sys.exit(1)
        print(f"\nPreview mode: {template_type} from {path}")
        diff_df = preview_official_import(str(path), template_type)
        diff_path = save_import_diff_report(diff_df)
        added = int((diff_df["change_type"] == "added_row").sum()) if not diff_df.empty else 0
        changed = int((diff_df["change_type"] == "changed_value").sum()) if not diff_df.empty else 0
        print(f"  Added rows:     {added}")
        print(f"  Changed values: {changed}")
        print(f"  Diff report:    {diff_path}")
        print("\nNo changes applied (preview only).")
        sys.exit(0)

    print(f"\nPath: {path}")
    print(f"Type: {template_type or 'auto-detect'}")
    print(f"Create backup: {not args.no_backup}")
    print(f"Re-prepare: {not args.no_reprepare}")

    try:
        if path.is_dir():
            print("\nApplying all import files in directory...")
            results = apply_all_imports(
                import_dir=path,
                create_backup=not args.no_backup,
                re_prepare=not args.no_reprepare,
            )

            print("\n" + "-" * 60)
            print("RESULTS")
            print("-" * 60)
            print(f"  Successful: {results['total_success']}")
            print(f"  Failed:     {results['total_failed']}")

            if results["errors"]:
                print("\nErrors:")
                for error in results["errors"]:
                    print(f"  ✗ {error}")

            if results["warnings"]:
                print("\nWarnings:")
                for warning in results["warnings"]:
                    print(f"  ⚠ {warning}")

            report_path = create_import_report(results)
            print(f"\nImport report saved to: {report_path}")

            if results["total_failed"] > 0:
                sys.exit(1)

        else:
            print(f"\nApplying import file: {path.name}")
            result = apply_official_import_file(
                import_file=path,
                template_type=template_type,
                create_backup=not args.no_backup,
                re_prepare=not args.no_reprepare,
            )

            print("\n" + "-" * 60)
            print("RESULT")
            print("-" * 60)

            if result.get("success"):
                print("  ✓ Import successful!")
                print(f"  Type: {result.get('type', 'unknown')}")
                print(f"  Rows imported: {result.get('rows_imported', 0)}")
            else:
                print("  ✗ Import failed!")
                if result.get("errors"):
                    print("\nErrors:")
                    for error in result.get("errors", []):
                        print(f"    ✗ {error}")

            if result.get("warnings"):
                print("\nWarnings:")
                for warning in result.get("warnings", []):
                    print(f"    ⚠ {warning}")

            append_import_audit(
                target=result.get("type", template_type or "unknown"),
                import_file=str(path),
                rows=int(result.get("rows_imported", 0)),
                overwritten=bool(result.get("success")),
                status="success" if result.get("success") else "failed",
                backup_path=str(result.get("backup_path", "")),
            )

            missing_df = build_official_missing_data_report()
            missing_path = save_missing_data_report(missing_df)
            readiness = evaluate_official_final_readiness()

            print(f"\nMissing-data report updated: {missing_path}")
            print(f"Final ready after import:    {readiness.get('is_official_final_ready')}")
            print("\nNext suggested command:")
            print("  python scripts/evaluate_official_final_readiness.py")

            if not result.get("success"):
                sys.exit(1)

        print("\n" + "=" * 60)
        print("Done!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
