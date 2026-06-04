"""Simulate one full tournament run for Step 14."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.simulation.prepare_full_tournament import prepare_step14_full_tournament_single_run  # noqa: E402


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Step 14 full tournament single-run simulation.")
    parser.add_argument("--seed", type=int, default=42)
    return parser


def main() -> int:
    args = _parser().parse_args()
    summary = prepare_step14_full_tournament_single_run(random_seed=int(args.seed))

    print("=== Step 14 Full Tournament Single-Run Summary ===")
    for key in [
        "status",
        "validation_passed",
        "champion",
        "runner_up",
        "third_place",
        "fourth_place",
        "total_matches",
        "group_stage_matches",
        "knockout_matches",
        "full_tournament_matches_path",
        "full_tournament_group_tables_path",
        "full_tournament_knockout_matches_path",
        "full_tournament_path_report_path",
        "full_tournament_result_path",
        "validation_report_path",
    ]:
        print(f"{key}: {summary.get(key)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
