#!/usr/bin/env python
"""Analyze and apply safe official data apply blockers cleanup (Step 17H)."""

from __future__ import annotations

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.official.blocker_cleanup import (
    analyze_apply_blockers,
    apply_safe_blocker_cleanups,
    save_blocker_cleanup_report,
)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Official apply blocker cleanup (Step 17H)")
    parser.add_argument("--apply", action="store_true", help="Run safe cleanups (does not promote official_final)")
    args = parser.parse_args()

    print("=" * 60)
    print("Step 17H: Official Data Apply Blocker Cleanup")
    print("=" * 60)

    summary, report_df = analyze_apply_blockers()
    report_path = save_blocker_cleanup_report(report_df)
    print(f"Report saved: {report_path}")
    print(f"Blocking categories: {summary.get('blocking_count', 0)}")

    if report_df.empty:
        print("No blockers detected.")
    else:
        for category in report_df["category"].unique():
            subset = report_df[report_df["category"] == category]
            print(f"\n[{category}]")
            for _, row in subset.iterrows():
                flag = "BLOCKING" if row.get("blocking") else "info"
                print(f"  ({flag}) {row.get('issue')}")
                if row.get("suggested_fix"):
                    print(f"    → {row['suggested_fix']}")

    if not args.apply:
        print("\nDry run only. To apply safe cleanups:")
        print("  python scripts/cleanup_official_apply_blockers.py --apply")
        print("\nThen preview apply:")
        print("  python scripts/apply_populated_official_data.py --preview")
        print("=" * 60)
        return

    result = apply_safe_blocker_cleanups()
    metrics_after = result.get("metrics_after", {})
    print("\n--- Applied safe cleanups ---")
    for note in result.get("notes", []):
        print(f"  • {note}")
    print(f"\nStages normalized:     {result.get('stages_normalized')}")
    print(f"Teams/groups rebuilt:  {result.get('teams_groups_rebuilt')}")
    print(f"Source labels updated: {result.get('source_labels_updated')}")
    print(f"\nFixtures:              {metrics_after.get('fixtures_count', 0)}")
    print(f"Group-stage fixtures:  {metrics_after.get('group_stage_fixtures_count', 0)}")
    print(f"Knockout fixtures:     {metrics_after.get('knockout_fixtures_count', 0)}")
    print(f"Players:               {metrics_after.get('players_count', 0)}")
    print(f"Teams w/ 26 players:   {metrics_after.get('teams_with_26_players', 0)}")
    print(f"ready_for_apply:       {result.get('ready_for_apply')}")
    print(f"final_ready:           {result.get('final_ready')}")
    print(f"official_final_enabled:{result.get('official_final_enabled')}")

    remaining = result.get("remaining_blockers", [])
    if remaining:
        print(f"\nRemaining blockers: {', '.join(remaining)}")
    else:
        print("\nNo remaining blocking categories in cleanup report.")

    print("\nNext command:")
    print("  python scripts/apply_populated_official_data.py --preview")
    print("=" * 60)


if __name__ == "__main__":
    main()
