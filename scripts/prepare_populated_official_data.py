#!/usr/bin/env python
"""Step 17F: Prepare populated official FIFA World Cup 2026 data."""

from __future__ import annotations

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.official.prepare_populated_official_data import prepare_step17f_populated_official_data


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Step 17F populated official data builder")
    parser.add_argument("--schedule-file", help="Path to FIFA schedule CSV/XLSX")
    parser.add_argument("--squad-file", help="Path to FIFA squad CSV/XLSX")
    parser.add_argument(
        "--apply-if-complete",
        action="store_true",
        help="Apply populated data only if completeness checks pass",
    )
    args = parser.parse_args()

    result = prepare_step17f_populated_official_data(
        schedule_file=args.schedule_file,
        squad_file=args.squad_file,
        apply_if_complete=args.apply_if_complete,
    )

    print("=" * 60)
    print("Step 17F: Populate Official FIFA World Cup 2026 Data")
    print("=" * 60)
    print(f"Status:                      {result.get('status')}")
    print(f"ready_for_apply:             {result.get('ready_for_apply')}")
    print(f"applied:                     {result.get('applied')}")
    print(f"teams count:                 {result.get('teams_count')}")
    print(f"fixtures count:              {result.get('fixtures_count')}")
    print(f"group-stage fixtures count:  {result.get('group_stage_fixtures_count')}")
    print(f"knockout fixtures count:     {result.get('knockout_fixtures_count')}")
    print(f"venues count:                {result.get('venues_count')}")
    print(f"players count:               {result.get('players_count')}")
    print(f"teams with 26 players:       {result.get('teams_with_26_players')}")
    print(f"sample_to_be_verified count: {result.get('sample_to_be_verified_count')}")
    print(f"placeholder issues count:    {result.get('placeholder_issues_count')}")
    print(f"completeness report path:    {result.get('completeness_report_path')}")
    print(f"import pack path:            {result.get('import_pack_path')}")
    print(f"final_ready:                 {result.get('final_ready')}")
    if result.get("notes"):
        print("\nNotes:")
        for note in result["notes"]:
            print(f"  - {note}")
    print("=" * 60)


if __name__ == "__main__":
    main()
