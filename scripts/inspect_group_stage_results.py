"""Inspect Step 12 group-stage simulation outputs."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import src.utils.constants as C

PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")
GROUP_STAGE_SIMULATED_MATCHES_FILE = getattr(C, "GROUP_STAGE_SIMULATED_MATCHES_FILE", "group_stage_simulated_matches.csv")
GROUP_STAGE_RANKINGS_FILE = getattr(C, "GROUP_STAGE_RANKINGS_FILE", "group_stage_rankings.csv")
BEST_THIRD_PLACED_TEAMS_FILE = getattr(C, "BEST_THIRD_PLACED_TEAMS_FILE", "best_third_placed_teams.csv")
ROUND_OF_32_QUALIFIERS_FILE = getattr(C, "ROUND_OF_32_QUALIFIERS_FILE", "round_of_32_qualifiers.csv")
GROUP_STAGE_SIMULATION_VALIDATION_REPORT_FILE = getattr(
    C, "GROUP_STAGE_SIMULATION_VALIDATION_REPORT_FILE", "group_stage_simulation_validation_report.csv"
)


def _load(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.is_file() else pd.DataFrame()


def main() -> int:
    simulated_path = PROCESSED_DATA_DIR / GROUP_STAGE_SIMULATED_MATCHES_FILE
    rankings_path = PROCESSED_DATA_DIR / GROUP_STAGE_RANKINGS_FILE
    best_third_path = PROCESSED_DATA_DIR / BEST_THIRD_PLACED_TEAMS_FILE
    qualifiers_path = PROCESSED_DATA_DIR / ROUND_OF_32_QUALIFIERS_FILE
    validation_path = PROCESSED_DATA_DIR / GROUP_STAGE_SIMULATION_VALIDATION_REPORT_FILE

    required_paths = [simulated_path, rankings_path, best_third_path, qualifiers_path, validation_path]
    missing = [str(p) for p in required_paths if not p.is_file()]
    if missing:
        print("Group-stage simulation outputs are missing.")
        print("Run: python scripts/simulate_group_stage.py --seed 42")
        print("Missing files:")
        for p in missing:
            print(f"- {p}")
        return 0

    simulated_df = _load(simulated_path)
    rankings_df = _load(rankings_path)
    best_third_df = _load(best_third_path)
    qualifiers_df = _load(qualifiers_path)
    validation_df = _load(validation_path)

    print("=== Step 12 Group-Stage Results Inspection ===")

    print("Group tables by group:")
    for group in sorted(rankings_df["group"].unique().tolist()):
        print(f"\nGroup {group}")
        print(
            rankings_df.loc[rankings_df["group"] == group, [
                "group_rank", "team", "points", "goal_difference", "goals_for", "goals_against", "wins", "draws", "losses"
            ]].sort_values("group_rank").to_string(index=False)
        )

    print("\nRound-of-32 qualifiers:")
    print(
        qualifiers_df[["group", "group_rank", "team", "qualification_type", "points", "goal_difference", "goals_for"]]
        .sort_values(["qualification_type", "group", "group_rank", "team"])
        .to_string(index=False)
    )

    print("\nBest third-placed teams:")
    print(
        best_third_df[["group", "team", "points", "goal_difference", "goals_for", "wins"]]
        .sort_values(["points", "goal_difference", "goals_for", "wins", "team"], ascending=[False, False, False, False, True])
        .to_string(index=False)
    )

    print("\nValidation report:")
    print(validation_df.to_string(index=False))

    print("\nTop 10 simulated matches:")
    print(simulated_df.head(10).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
