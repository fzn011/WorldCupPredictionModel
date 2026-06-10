"""Run Step 15 Monte Carlo simulation pipeline."""

from __future__ import annotations

import argparse
import sys
import time
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
    print("=== Step 15B Monte Carlo Run ===")
    print(f"starting simulations={int(args.simulations)} base_seed={int(args.seed)}")
    started = time.perf_counter()

    summary = prepare_step15_monte_carlo_simulation(
        num_simulations=int(args.simulations),
        base_seed=int(args.seed),
    )
    runtime_seconds = float(time.perf_counter() - started)

    cache_info = summary.get("cache_info", {}) if isinstance(summary, dict) else {}

    print(f"runtime_seconds: {runtime_seconds:.2f}")
    print("cache_info:")
    print(f"  total_requests: {cache_info.get('total_requests', 0)}")
    print(f"  cache_hits: {cache_info.get('cache_hits', 0)}")
    print(f"  cache_misses: {cache_info.get('cache_misses', 0)}")
    print(f"  cache_size: {cache_info.get('cache_size', 0)}")

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
