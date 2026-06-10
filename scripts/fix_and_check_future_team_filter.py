#!/usr/bin/env python
"""Debug helper for future-match team dropdown official vs fallback behavior."""

from __future__ import annotations

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import src.utils.constants as C
from src.features.future_match_features import get_available_teams
from src.official.loaders import get_official_team_list


def _is_sorted_unique(teams: list[str]) -> tuple[bool, bool]:
    return teams == sorted(teams), len(teams) == len(set(teams))


def main() -> None:
    official_teams_path = C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR / C.OFFICIAL_TEAMS_FILE
    populated_teams_path = C.PROJECT_ROOT / C.OFFICIAL_POPULATED_DATA_DIR / C.POPULATED_OFFICIAL_TEAMS_FILE
    official_count = len(get_official_team_list())
    official_only = get_available_teams(official_only=True)
    fallback = get_available_teams(official_only=False)

    sorted_off, unique_off = _is_sorted_unique(official_only)
    sorted_fb, unique_fb = _is_sorted_unique(fallback)

    print("=" * 60)
    print("Future Team Filter Diagnostic (Step 17G/17H)")
    print("=" * 60)
    print(f"official_teams.csv present: {official_teams_path.is_file()}")
    print(f"populated_official_teams.csv present: {populated_teams_path.is_file()}")
    print(f"Official team list count:   {official_count}")
    print(f"get_available_teams(official_only=True):  {len(official_only)} teams")
    print(f"get_available_teams(official_only=False): {len(fallback)} teams")
    print(f"Official-only sorted: {sorted_off}, unique: {unique_off}")
    print(f"Fallback sorted:      {sorted_fb}, unique: {unique_fb}")
    print("\nFirst 20 official-only teams:")
    for t in official_only[:20]:
        print(f"  - {t}")
    print("\nFirst 20 fallback teams:")
    for t in fallback[:20]:
        print(f"  - {t}")
    print("=" * 60)


if __name__ == "__main__":
    main()
