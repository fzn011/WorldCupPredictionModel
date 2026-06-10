"""Compatibility alias for Golden Ball generation within the broader awards predictor."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.awards.prepare_awards import prepare_step17_world_cup_awards  # noqa: E402


def main() -> int:
    print("Golden Ball is now part of the broader World Cup Awards Predictor.")
    try:
        summary = prepare_step17_world_cup_awards()
    except FileNotFoundError:
        print("Run python scripts/run_monte_carlo.py --simulations 10 --seed 42 first.")
        return 0

    print("=== Step 17 Golden Ball Summary (Compatibility View) ===")
    for key in [
        "status",
        "validation_passed",
        "top_golden_ball_player",
        "top_golden_boot_player",
        "top_golden_glove_player",
        "report_path",
        "validation_report_path",
    ]:
        print(f"{key}: {summary.get(key)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
