"""Run Step 15 Monte Carlo simulation pipeline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.simulation.prepare_monte_carlo import prepare_step15_monte_carlo_simulation  # noqa: E402
import src.utils.constants as C  # noqa: E402

DEFAULT_MONTE_CARLO_SIMULATIONS = int(getattr(C, "DEFAULT_MONTE_CARLO_SIMULATIONS", 100))
DEFAULT_MONTE_CARLO_SEED = int(getattr(C, "DEFAULT_MONTE_CARLO_SEED", 42))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Step 15 Monte Carlo full-tournament simulation.")
    parser.add_argument("--simulations", type=int, default=DEFAULT_MONTE_CARLO_SIMULATIONS)
    parser.add_argument("--seed", type=int, default=DEFAULT_MONTE_CARLO_SEED)
    return parser


def main() -> int:
    args = _parser().parse_args()
    summary = prepare_step15_monte_carlo_simulation(
        num_simulations=int(args.simulations),
        base_seed=int(args.seed),
    )

    print("=== Step 15 Monte Carlo Summary ===")
    for key in [
        "status",
        "num_simulations",
        "successful_simulations",
        "failed_simulations",
        "validation_passed",
        "top_champion",
        "top_champion_probability",
        "simulation_results_path",
        "team_stage_probabilities_path",
        "champion_probabilities_path",
        "finalists_path",
        "semifinalists_path",
        "validation_report_path",
        "summary_path",
    ]:
        print(f"{key}: {summary.get(key)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
