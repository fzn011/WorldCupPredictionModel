#!/usr/bin/env python
"""Step 17G: Run official data import execution workflow."""

from __future__ import annotations

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.official.prepare_import_execution import prepare_step17g_official_import_execution


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Step 17G official data import execution")
    parser.add_argument("--schedule-file", help="Official FIFA schedule CSV/XLSX")
    parser.add_argument("--squad-file", help="Official FIFA squad CSV/XLSX")
    parser.add_argument("--workbook-file", help="Master import workbook XLSX")
    parser.add_argument("--apply", action="store_true", help="Apply populated data if ready")
    parser.add_argument(
        "--force-draft-apply",
        action="store_true",
        help="Attempt apply even when incomplete (official_final stays blocked)",
    )
    args = parser.parse_args()

    result = prepare_step17g_official_import_execution(
        schedule_file=args.schedule_file,
        squad_file=args.squad_file,
        workbook_file=args.workbook_file,
        apply=args.apply,
        force_draft_apply=args.force_draft_apply,
    )

    print("=" * 60)
    print("Step 17G: Official Data Import Execution")
    print("=" * 60)
    print(f"Status:                    {result.get('status')}")
    print(f"Staged fixtures count:     {result.get('staged_fixtures_count')}")
    print(f"Staged players count:      {result.get('staged_players_count')}")
    print(f"Populated fixtures count:  {result.get('populated_fixtures_count')}")
    print(f"Populated players count:   {result.get('populated_players_count')}")
    print(f"Teams with 26 players:     {result.get('teams_with_26_players')}")
    print(f"ready_for_apply:           {result.get('ready_for_apply')}")
    print(f"applied:                   {result.get('applied')}")
    print(f"final_ready:               {result.get('final_ready')}")
    print(f"official_final_enabled:    {result.get('official_final_enabled')}")
    print(f"Blockers count:            {result.get('blockers_count')}")
    print(f"Warnings count:            {result.get('warnings_count')}")
    print(f"Execution report:          {result.get('import_execution_report_path')}")
    print(f"Completeness report:       {result.get('completeness_report_path')}")
    print(f"Readiness report:          {result.get('final_readiness_report_path')}")
    print(f"Next action:               {result.get('next_action')}")
    if result.get("notes"):
        print("\nNotes:")
        for note in result["notes"]:
            print(f"  - {note}")
    print("=" * 60)


if __name__ == "__main__":
    main()
