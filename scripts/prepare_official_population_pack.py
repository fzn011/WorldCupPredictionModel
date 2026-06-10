#!/usr/bin/env python
"""Prepare the Step 17D official data population pack."""

from __future__ import annotations

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.official.prepare_population_pack import prepare_step17d_official_data_population_pack


def main() -> None:
    print("=" * 60)
    print("FIFA World Cup 2026 - Official Data Population Pack (Step 17D)")
    print("=" * 60)

    result = prepare_step17d_official_data_population_pack()

    print(f"\nStatus:                      {result.get('status')}")
    print(f"Guide path:                  {result.get('guide_path')}")
    print(f"Template directory:          {result.get('template_dir')}")
    print(f"Workbook path:               {result.get('workbook_path')}")
    print(f"Workbook README:             {result.get('workbook_readme_path')}")
    print(f"Missing-data report:         {result.get('missing_data_report_path')}")
    print(f"Readiness summary:           {result.get('readiness_summary_path')}")
    print(f"Final ready:                 {result.get('final_ready')}")
    print(f"Errors count:                {result.get('errors_count')}")
    print(f"Warnings count:              {result.get('warnings_count')}")
    print(f"sample_to_be_verified count: {result.get('sample_to_be_verified_count')}")
    print(f"Placeholder issues count:    {result.get('placeholder_issues_count')}")
    print(f"Teams count:                 {result.get('teams_count')}")
    print(f"Fixtures count:              {result.get('fixtures_count')}")
    print(f"Players count:               {result.get('players_count')}")

    if result.get("notes"):
        print("\nNotes:")
        for note in result["notes"]:
            print(f"  - {note}")

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
