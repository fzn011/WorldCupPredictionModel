"""Inspect official-style World Cup 2026 data bundle."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.official.loaders import (
    load_official_fixtures,
    load_official_groups,
    load_official_match_calendar,
    load_official_teams,
    load_official_venues,
    load_source_manifest,
    official_path,
)
import src.utils.constants as C  # noqa: E402

OFFICIAL_DATA_SUMMARY_FILE = getattr(C, "OFFICIAL_DATA_SUMMARY_FILE", "official_data_summary.json")
OFFICIAL_DATA_VALIDATION_REPORT_FILE = getattr(C, "OFFICIAL_DATA_VALIDATION_REPORT_FILE", "official_data_validation_report.csv")


def main() -> int:
    summary_path = official_path(OFFICIAL_DATA_SUMMARY_FILE)
    validation_path = official_path(OFFICIAL_DATA_VALIDATION_REPORT_FILE)
    if not summary_path.is_file():
        print("Run python scripts/prepare_official_worldcup_data.py first.")
        return 0

    with summary_path.open("r", encoding="utf-8") as f:
        summary = json.load(f)
    validation_df = pd.read_csv(validation_path) if validation_path.is_file() else pd.DataFrame()
    teams_df = load_official_teams()
    groups_df = load_official_groups()
    fixtures_df = load_official_fixtures()
    venues_df = load_official_venues()
    calendar_df = load_official_match_calendar()
    manifest = load_source_manifest()

    print("=== Step 17A Official World Cup Data Inspection ===")
    print("summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    print("\nTeams by group:")
    print(groups_df[["group", "slot", "team"]].sort_values(["group", "slot"]).to_string(index=False))

    print("\nFixtures count by stage:")
    if not fixtures_df.empty:
        print(fixtures_df["stage"].value_counts(dropna=False).to_string())
    else:
        print("No fixtures found.")

    print("\nVenue list:")
    if not venues_df.empty:
        cols = [col for col in ["venue", "stadium", "city", "country", "timezone", "source"] if col in venues_df.columns]
        print(venues_df[cols].to_string(index=False))
    else:
        print("No venues found.")

    print("\nValidation failures:")
    failed = validation_df[validation_df["passed"] == False] if not validation_df.empty else pd.DataFrame()
    if failed.empty:
        print("No validation failures.")
    else:
        print(failed.to_string(index=False))

    print("\nSource manifest:")
    for key, value in manifest.items():
        print(f"  {key}: {value}")

    print("\nOfficial match calendar preview:")
    if calendar_df.empty:
        print("No match calendar found.")
    else:
        print(calendar_df.head(20).to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
