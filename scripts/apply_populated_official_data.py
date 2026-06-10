#!/usr/bin/env python
"""Preview or apply populated official data (Step 17F)."""

from __future__ import annotations

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import src.utils.constants as C
from src.official.final_readiness import evaluate_official_final_readiness
from src.official.import_diff import preview_official_import, save_import_diff_report
from src.official.population_completeness import calculate_population_completeness, population_is_ready_for_apply
from src.official.stage_normalization import apply_stage_normalization
from src.official.prepare_populated_official_data import prepare_step17f_populated_official_data


POPULATED_MAP = {
    "teams": C.POPULATED_OFFICIAL_TEAMS_FILE,
    "groups": C.POPULATED_OFFICIAL_GROUPS_FILE,
    "venues": C.POPULATED_OFFICIAL_VENUES_FILE,
    "fixtures": C.POPULATED_OFFICIAL_FIXTURES_FILE,
    "players": C.POPULATED_OFFICIAL_PLAYERS_FILE,
    "player_priors": C.POPULATED_PLAYER_AWARD_PRIORS_FILE,
}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Preview or apply populated official data")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preview", action="store_true")
    group.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    populated_dir = C.PROJECT_ROOT / C.OFFICIAL_POPULATED_DATA_DIR
    fixtures_path = populated_dir / C.POPULATED_OFFICIAL_FIXTURES_FILE
    if fixtures_path.is_file():
        import pandas as pd

        fixtures_df = pd.read_csv(fixtures_path)
        if not fixtures_df.empty:
            fixtures_df = apply_stage_normalization(fixtures_df)
            fixtures_df.to_csv(fixtures_path, index=False)

    metrics, report_df = calculate_population_completeness()
    ready = population_is_ready_for_apply(metrics)

    print("=" * 60)
    print("Step 17F: Apply Populated Official Data")
    print("=" * 60)
    print(f"ready_for_apply: {ready}")

    if args.preview:
        for target, filename in POPULATED_MAP.items():
            path = populated_dir / filename
            if not path.is_file():
                print(f"\n{target}: populated file missing ({path})")
                continue
            diff_df = preview_official_import(str(path), target)
            diff_path = save_import_diff_report(diff_df)
            adds = len(diff_df[diff_df["change_type"] == "added"]) if not diff_df.empty else 0
            updates = len(diff_df[diff_df["change_type"] == "updated"]) if not diff_df.empty else 0
            print(f"\n{target}: added={adds}, updated={updates}, diff={diff_path}")
        print("=" * 60)
        return

    if not ready:
        print("\nApply blocked because populated official data is incomplete.")
        print("Try blocker cleanup first:")
        print("  python scripts/cleanup_official_apply_blockers.py --apply")
        print("Apply blocked — population not ready:")
        blockers = report_df[report_df["blocking"] == True]  # noqa: E712
        for _, row in blockers.iterrows():
            print(f"  - {row['category']}: {row['actual']}/{row['target']} — {row['notes']}")
        print("\nNext actions:")
        print("  1. Run blocker cleanup:           python scripts/cleanup_official_apply_blockers.py --apply")
        print("  2. Rebuild populated data:        python scripts/prepare_populated_official_data.py --schedule-file ... --squad-file ...")
        print("  3. Preview apply:                 python scripts/apply_populated_official_data.py --preview")
        print("  4. Re-run readiness:              python scripts/evaluate_official_final_readiness.py")
        print("=" * 60)
        sys.exit(1)

    result = prepare_step17f_populated_official_data(apply_if_complete=True)
    readiness = evaluate_official_final_readiness()
    print(f"\napplied: {result.get('applied')}")
    print(f"status:  {result.get('status')}")
    print(f"official_final ready: {readiness.get('is_official_final_ready')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
