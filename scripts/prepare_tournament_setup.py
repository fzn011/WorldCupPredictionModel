"""CLI wrapper for Step 11 tournament setup preparation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.tournament.prepare_tournament import prepare_step11_tournament_setup


def main() -> None:
    summary = prepare_step11_tournament_setup()
    print("=== Step 11 Tournament Setup Summary ===")
    for key in [
        "status",
        "groups_valid",
        "fixtures_valid",
        "total_teams",
        "total_groups",
        "total_group_matches",
        "knockout_placeholder_matches",
        "tournament_groups_path",
        "tournament_fixtures_path",
        "knockout_placeholders_path",
        "tournament_structure_path",
        "validation_report_path",
    ]:
        print(f"{key}: {summary.get(key)}")


if __name__ == "__main__":
    main()
