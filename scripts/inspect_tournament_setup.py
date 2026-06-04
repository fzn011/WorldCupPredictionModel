"""Inspect prepared tournament setup artifacts for Step 11."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import src.utils.constants as C

PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")
TOURNAMENT_GROUPS_FILE = getattr(C, "TOURNAMENT_GROUPS_FILE", "tournament_groups.csv")
TOURNAMENT_FIXTURES_FILE = getattr(C, "TOURNAMENT_FIXTURES_FILE", "tournament_fixtures.csv")
TOURNAMENT_VALIDATION_REPORT_FILE = getattr(C, "TOURNAMENT_VALIDATION_REPORT_FILE", "tournament_validation_report.csv")
KNOCKOUT_PLACEHOLDER_FILE = getattr(C, "KNOCKOUT_PLACEHOLDER_FILE", "knockout_placeholders.csv")


def main() -> int:
    groups_path = PROCESSED_DATA_DIR / TOURNAMENT_GROUPS_FILE
    fixtures_path = PROCESSED_DATA_DIR / TOURNAMENT_FIXTURES_FILE
    validation_path = PROCESSED_DATA_DIR / TOURNAMENT_VALIDATION_REPORT_FILE
    knockout_path = PROCESSED_DATA_DIR / KNOCKOUT_PLACEHOLDER_FILE

    required_paths = [groups_path, fixtures_path, validation_path, knockout_path]
    missing = [str(path) for path in required_paths if not path.is_file()]
    if missing:
        print("Tournament setup artifacts are missing.")
        print("Run: python scripts/prepare_tournament_setup.py")
        print("Missing:")
        for path in missing:
            print(f"- {path}")
        return 0

    groups_df = pd.read_csv(groups_path)
    fixtures_df = pd.read_csv(fixtures_path)
    validation_df = pd.read_csv(validation_path)
    knockout_df = pd.read_csv(knockout_path)

    print("=== Step 11 Tournament Setup Inspection ===")
    print(f"Group count: {groups_df['group'].nunique()}")
    print("Teams per group:")
    print(groups_df.groupby("group")["team"].count().to_string())

    print(f"Total group fixtures: {len(fixtures_df)}")
    print("Fixture count per group:")
    print(fixtures_df.groupby("group")["match_id"].count().to_string())

    print("Top 10 fixtures:")
    print(fixtures_df.head(10).to_string(index=False))

    overall_valid = bool(validation_df["passed"].all())
    print(f"Validation status: {'passed' if overall_valid else 'failed'}")

    print("Knockout placeholder count by round:")
    print(knockout_df.groupby("round")["match_id"].count().to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
