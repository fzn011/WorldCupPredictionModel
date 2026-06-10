#!/usr/bin/env python
"""Generate Step 18 World Cup awards analytics artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.awards.prepare_awards import prepare_step18_world_cup_awards  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate World Cup awards predictions")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--use-enriched", action="store_true", help="Use enriched official candidates")
    group.add_argument("--no-enriched", action="store_true", help="Use base official_award_candidates.csv")
    args = parser.parse_args(argv)

    use_enriched: bool | None = None
    if args.use_enriched:
        use_enriched = True
    elif args.no_enriched:
        use_enriched = False

    try:
        summary = prepare_step18_world_cup_awards(use_enriched_candidates=use_enriched)
    except RuntimeError as exc:
        print(str(exc))
        return 1
    except FileNotFoundError as exc:
        print(str(exc))
        return 1

    print("=== Step 18 World Cup Awards Summary ===")
    for key in [
        "status",
        "validation_passed",
        "official_final_enabled",
        "candidate_source",
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
    return 0 if summary.get("validation_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
