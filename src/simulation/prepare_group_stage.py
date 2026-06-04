"""Step 12 group-stage simulation preparation orchestrator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.simulation.group_stage import (
    build_group_tables,
    create_group_stage_summary,
    rank_group_tables,
    select_group_qualifiers,
    simulate_group_stage,
    validate_group_stage_simulation,
)
from src.tournament.fixtures import load_tournament_fixtures
import src.utils.constants as C

PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")
GROUP_STAGE_SIMULATED_MATCHES_FILE = getattr(C, "GROUP_STAGE_SIMULATED_MATCHES_FILE", "group_stage_simulated_matches.csv")
GROUP_STAGE_TABLES_FILE = getattr(C, "GROUP_STAGE_TABLES_FILE", "group_stage_tables.csv")
GROUP_STAGE_RANKINGS_FILE = getattr(C, "GROUP_STAGE_RANKINGS_FILE", "group_stage_rankings.csv")
BEST_THIRD_PLACED_TEAMS_FILE = getattr(C, "BEST_THIRD_PLACED_TEAMS_FILE", "best_third_placed_teams.csv")
ROUND_OF_32_QUALIFIERS_FILE = getattr(C, "ROUND_OF_32_QUALIFIERS_FILE", "round_of_32_qualifiers.csv")
GROUP_STAGE_SIMULATION_SUMMARY_FILE = getattr(C, "GROUP_STAGE_SIMULATION_SUMMARY_FILE", "group_stage_simulation_summary.json")
GROUP_STAGE_SIMULATION_VALIDATION_REPORT_FILE = getattr(
    C, "GROUP_STAGE_SIMULATION_VALIDATION_REPORT_FILE", "group_stage_simulation_validation_report.csv"
)


def _save_csv(df: pd.DataFrame, file_name: str) -> str:
    path = PROCESSED_DATA_DIR / file_name
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return str(path)


def prepare_step12_group_stage_simulation(random_seed: int = 42) -> dict[str, Any]:
    """Run full Step 12 group-stage simulation pipeline and persist outputs."""
    fixtures_df = load_tournament_fixtures()
    simulated_matches_df = simulate_group_stage(fixtures_df=fixtures_df, random_seed=random_seed)
    group_tables_df = build_group_tables(simulated_matches_df)
    ranked_tables_df = rank_group_tables(group_tables_df)

    automatic_df, best_third_df, qualifiers_df = select_group_qualifiers(ranked_tables_df)
    is_valid, validation_report_df = validate_group_stage_simulation(
        simulated_matches_df=simulated_matches_df,
        ranked_tables_df=ranked_tables_df,
        qualifiers_df=qualifiers_df,
    )

    summary = create_group_stage_summary(
        simulated_matches_df=simulated_matches_df,
        ranked_tables_df=ranked_tables_df,
        automatic_qualifiers_df=automatic_df,
        best_third_df=best_third_df,
        qualifiers_df=qualifiers_df,
        validation_passed=is_valid,
        random_seed=random_seed,
    )

    simulated_matches_path = _save_csv(simulated_matches_df, GROUP_STAGE_SIMULATED_MATCHES_FILE)
    group_tables_path = _save_csv(group_tables_df, GROUP_STAGE_TABLES_FILE)
    group_rankings_path = _save_csv(ranked_tables_df, GROUP_STAGE_RANKINGS_FILE)
    best_third_path = _save_csv(best_third_df, BEST_THIRD_PLACED_TEAMS_FILE)
    qualifiers_path = _save_csv(qualifiers_df, ROUND_OF_32_QUALIFIERS_FILE)
    validation_report_path = _save_csv(validation_report_df, GROUP_STAGE_SIMULATION_VALIDATION_REPORT_FILE)

    summary_path = PROCESSED_DATA_DIR / GROUP_STAGE_SIMULATION_SUMMARY_FILE
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    summary.update(
        {
            "group_stage_simulated_matches_path": simulated_matches_path,
            "group_stage_tables_path": group_tables_path,
            "group_stage_rankings_path": group_rankings_path,
            "best_third_placed_teams_path": best_third_path,
            "round_of_32_qualifiers_path": qualifiers_path,
            "group_stage_simulation_validation_report_path": validation_report_path,
            "group_stage_simulation_summary_path": str(summary_path),
        }
    )

    return summary


if __name__ == "__main__":
    print(prepare_step12_group_stage_simulation())
