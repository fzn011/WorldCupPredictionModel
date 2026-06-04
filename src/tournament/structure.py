"""Tournament structure assembly and persistence helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C

PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")
TOURNAMENT_STRUCTURE_FILE = getattr(C, "TOURNAMENT_STRUCTURE_FILE", "tournament_structure.json")

WC2026_TOTAL_TEAMS = getattr(C, "WC2026_TOTAL_TEAMS", 48)
WC2026_GROUPS = getattr(C, "WC2026_GROUPS", ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"])
WC2026_TEAMS_PER_GROUP = getattr(C, "WC2026_TEAMS_PER_GROUP", 4)
WC2026_TOTAL_GROUP_MATCHES = getattr(C, "WC2026_TOTAL_GROUP_MATCHES", 72)
WC2026_QUALIFIED_FROM_GROUP_TOP_N = getattr(C, "WC2026_QUALIFIED_FROM_GROUP_TOP_N", 2)
WC2026_BEST_THIRD_PLACED_QUALIFIERS = getattr(C, "WC2026_BEST_THIRD_PLACED_QUALIFIERS", 8)


def build_tournament_structure(
    groups_df: pd.DataFrame,
    fixtures_df: pd.DataFrame,
    knockout_df: pd.DataFrame,
) -> dict[str, Any]:
    """Build a simulation-ready tournament structure summary dictionary."""
    group_counts = groups_df.groupby("group")["team"].count().to_dict()
    fixture_counts = fixtures_df.groupby("group")["match_id"].count().to_dict()
    knockout_rounds = knockout_df.groupby("round")["match_id"].count().to_dict()

    structure: dict[str, Any] = {
        "format": {
            "total_teams": WC2026_TOTAL_TEAMS,
            "groups": len(WC2026_GROUPS),
            "teams_per_group": WC2026_TEAMS_PER_GROUP,
            "group_matches": WC2026_TOTAL_GROUP_MATCHES,
            "top_per_group_qualify": WC2026_QUALIFIED_FROM_GROUP_TOP_N,
            "best_third_placed_qualify": WC2026_BEST_THIRD_PLACED_QUALIFIERS,
        },
        "groups": {
            "labels": WC2026_GROUPS,
            "team_counts": group_counts,
            "teams": groups_df.sort_values(["group", "slot"]).to_dict(orient="records"),
        },
        "fixture_counts": {
            "total": int(len(fixtures_df)),
            "by_group": fixture_counts,
        },
        "knockout_rounds": knockout_rounds,
    }
    return structure


def save_tournament_structure(structure: dict[str, Any], output_path: str | None = None) -> str:
    """Save tournament structure JSON under processed folder."""
    path = Path(output_path) if output_path else PROCESSED_DATA_DIR / TOURNAMENT_STRUCTURE_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(structure, f, ensure_ascii=False, indent=2)
    return str(path)
