"""Simulate one full knockout bracket for Step 13."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.simulation.prepare_knockout import prepare_step13_knockout_simulation  # noqa: E402


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simulate the Step 13 knockout stage.")
    parser.add_argument("--seed", type=int, default=42)
    return parser


def main() -> int:
    args = _parser().parse_args()
    summary = prepare_step13_knockout_simulation(random_seed=int(args.seed))

    print("=== Step 13 Knockout Simulation Summary ===")
    for key in [
        "status",
        "validation_passed",
        "champion",
        "runner_up",
        "third_place",
        "fourth_place",
        "total_knockout_matches",
        "round_counts",
        "knockout_bracket_filled_path",
        "knockout_simulated_matches_path",
        "single_tournament_result_path",
        "validation_report_path",
        "knockout_simulation_summary_path",
    ]:
        print(f"{key}: {summary.get(key)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
