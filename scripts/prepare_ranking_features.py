"""Prepare Step 7 ranking-enhanced feature dataset."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.features.prepare_ranking_features import prepare_step7_ranking_features  # noqa: E402


def main() -> None:
    summary = prepare_step7_ranking_features()
    print("=== Step 7 Ranking Feature Preparation Summary ===")
    print(f"Status: {summary.get('status')}")
    print(f"Mode: {summary.get('mode')}")
    print(f"Rows: {summary.get('rows')}")
    print(f"Columns: {summary.get('columns')}")
    print(f"Unique teams: {summary.get('unique_teams')}")
    print(f"Team strength rows: {summary.get('team_strength_rows')}")
    print(f"Output path: {summary.get('output_path')}")
    print(f"Merge report path: {summary.get('ranking_merge_report_path')}")
    print(f"Notes: {summary.get('notes')}")


if __name__ == "__main__":
    main()
