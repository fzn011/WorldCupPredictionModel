"""CLI for Step 12 group-stage simulation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.simulation.prepare_group_stage import prepare_step12_group_stage_simulation


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simulate FIFA 2026 group stage.")
    parser.add_argument("--seed", type=int, default=42)
    return parser


def main() -> int:
    args = _parser().parse_args()
    summary = prepare_step12_group_stage_simulation(random_seed=int(args.seed))

    print("=== Step 12 Group-Stage Simulation Summary ===")
    for key in [
        "status",
        "validation_passed",
        "simulated_matches",
        "automatic_qualifiers",
        "best_third_placed_qualifiers",
        "round_of_32_qualifiers",
        "group_stage_simulated_matches_path",
        "group_stage_tables_path",
        "group_stage_rankings_path",
        "best_third_placed_teams_path",
        "round_of_32_qualifiers_path",
        "group_stage_simulation_validation_report_path",
        "group_stage_simulation_summary_path",
    ]:
        print(f"{key}: {summary.get(key)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
