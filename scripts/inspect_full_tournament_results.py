"""Inspect Step 14 full-tournament simulation outputs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import src.utils.constants as C

PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")
FULL_TOURNAMENT_SIMULATED_MATCHES_FILE = getattr(C, "FULL_TOURNAMENT_SIMULATED_MATCHES_FILE", "full_tournament_simulated_matches.csv")
FULL_TOURNAMENT_GROUP_TABLES_FILE = getattr(C, "FULL_TOURNAMENT_GROUP_TABLES_FILE", "full_tournament_group_tables.csv")
FULL_TOURNAMENT_KNOCKOUT_MATCHES_FILE = getattr(C, "FULL_TOURNAMENT_KNOCKOUT_MATCHES_FILE", "full_tournament_knockout_matches.csv")
FULL_TOURNAMENT_STAGE_RESULTS_FILE = getattr(C, "FULL_TOURNAMENT_STAGE_RESULTS_FILE", "full_tournament_stage_results.csv")
FULL_TOURNAMENT_PATH_REPORT_FILE = getattr(C, "FULL_TOURNAMENT_PATH_REPORT_FILE", "full_tournament_path_report.csv")
FULL_TOURNAMENT_RESULT_FILE = getattr(C, "FULL_TOURNAMENT_RESULT_FILE", "single_world_cup_result.json")
FULL_TOURNAMENT_SUMMARY_FILE = getattr(C, "FULL_TOURNAMENT_SUMMARY_FILE", "full_tournament_summary.json")
FULL_TOURNAMENT_VALIDATION_REPORT_FILE = getattr(C, "FULL_TOURNAMENT_VALIDATION_REPORT_FILE", "full_tournament_validation_report.csv")


def _path(name: str) -> Path:
    return PROCESSED_DATA_DIR / name


def _safe_read_csv(path: Path) -> pd.DataFrame | None:
    if not path.is_file():
        return None
    return pd.read_csv(path)


def _safe_read_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    full_matches = _safe_read_csv(_path(FULL_TOURNAMENT_SIMULATED_MATCHES_FILE))
    group_tables = _safe_read_csv(_path(FULL_TOURNAMENT_GROUP_TABLES_FILE))
    knockout_matches = _safe_read_csv(_path(FULL_TOURNAMENT_KNOCKOUT_MATCHES_FILE))
    stage_results = _safe_read_csv(_path(FULL_TOURNAMENT_STAGE_RESULTS_FILE))
    path_report = _safe_read_csv(_path(FULL_TOURNAMENT_PATH_REPORT_FILE))
    summary = _safe_read_json(_path(FULL_TOURNAMENT_SUMMARY_FILE))
    single_result = _safe_read_json(_path(FULL_TOURNAMENT_RESULT_FILE))
    validation = _safe_read_csv(_path(FULL_TOURNAMENT_VALIDATION_REPORT_FILE))

    if any(item is None for item in [full_matches, group_tables, knockout_matches, stage_results, path_report, summary, single_result, validation]):
        print("Missing full-tournament outputs.")
        print("Run: python scripts/simulate_full_tournament.py --seed 42")
        return 0

    print("=== Step 14 Full Tournament Inspection ===")
    print(f"champion: {summary.get('champion')}")
    print(f"runner_up: {summary.get('runner_up')}")
    print(f"third_place: {summary.get('third_place')}")
    print(f"fourth_place: {summary.get('fourth_place')}")
    print(f"validation_passed: {summary.get('validation_passed')}")
    print(f"total_matches: {summary.get('total_matches')}")
    print(f"group_stage_matches: {summary.get('group_stage_matches')}")
    print(f"knockout_matches: {summary.get('knockout_matches')}")
    print()

    print("Stage results:")
    print(stage_results.to_string(index=False))
    print()

    print("Validation report:")
    print(validation.to_string(index=False))
    print()

    print("Top path report rows:")
    print(path_report.head(15).to_string(index=False))
    print()

    if not knockout_matches.empty:
        print("Final and third-place match rows:")
        finals = knockout_matches.loc[knockout_matches["round"].isin(["third_place", "final"])].copy()
        print(finals.to_string(index=False))
        print()

    print(f"group_tables_rows: {len(group_tables)}")
    print(f"full_match_log_rows: {len(full_matches)}")
    print("single_world_cup_result_keys:")
    print(sorted(single_result.keys()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
