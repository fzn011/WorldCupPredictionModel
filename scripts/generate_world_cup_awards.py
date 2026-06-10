"""Generate Step 17 World Cup awards analytics artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.awards.prepare_awards import prepare_step17_world_cup_awards  # noqa: E402


def main() -> int:
    try:
        summary = prepare_step17_world_cup_awards()
    except FileNotFoundError:
        print("Run python scripts/run_monte_carlo.py --simulations 10 --seed 42 first.")
        return 0

    print("=== Step 17 World Cup Awards Summary ===")
    for key in [
        "status",
        "validation_passed",
        "top_golden_ball_player",
        "top_golden_boot_player",
        "top_golden_glove_player",
        "top_young_player",
        "top_fair_play_team",
        "top_entertaining_team",
        "team_of_tournament_count",
        "report_path",
        "validation_report_path",
    ]:
        print(f"{key}: {summary.get(key)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
