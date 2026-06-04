"""Step 11 tournament setup preparation orchestration."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import src.utils.constants as C
from src.tournament.fixtures import (
    generate_group_stage_fixtures,
    save_tournament_fixtures,
    validate_group_stage_fixtures,
)
from src.tournament.groups import (
    load_tournament_groups,
    save_tournament_groups,
    validate_tournament_groups,
)
from src.tournament.knockout import create_knockout_placeholders, save_knockout_placeholders
from src.tournament.structure import build_tournament_structure, save_tournament_structure

PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")
TOURNAMENT_VALIDATION_REPORT_FILE = getattr(C, "TOURNAMENT_VALIDATION_REPORT_FILE", "tournament_validation_report.csv")


def prepare_step11_tournament_setup() -> dict[str, object]:
    """Prepare validated tournament groups, fixtures, knockout placeholders and structure."""
    groups_df = load_tournament_groups()
    groups_valid, groups_report = validate_tournament_groups(groups_df)
    groups_path = save_tournament_groups(groups_df)

    fixtures_df = generate_group_stage_fixtures(groups_df)
    fixtures_valid, fixtures_report = validate_group_stage_fixtures(fixtures_df, groups_df)
    fixtures_path = save_tournament_fixtures(fixtures_df)

    knockout_df = create_knockout_placeholders()
    knockout_path = save_knockout_placeholders(knockout_df)

    structure = build_tournament_structure(groups_df, fixtures_df, knockout_df)
    structure_path = save_tournament_structure(structure)

    validation_report = pd.concat([groups_report, fixtures_report], ignore_index=True)
    validation_report_path = PROCESSED_DATA_DIR / TOURNAMENT_VALIDATION_REPORT_FILE
    validation_report_path.parent.mkdir(parents=True, exist_ok=True)
    validation_report.to_csv(validation_report_path, index=False)

    status = "ok" if groups_valid and fixtures_valid else "validation_failed"

    return {
        "status": status,
        "groups_valid": bool(groups_valid),
        "fixtures_valid": bool(fixtures_valid),
        "total_teams": int(len(groups_df)),
        "total_groups": int(groups_df["group"].nunique()),
        "total_group_matches": int(len(fixtures_df)),
        "knockout_placeholder_matches": int(len(knockout_df)),
        "tournament_groups_path": groups_path,
        "tournament_fixtures_path": fixtures_path,
        "knockout_placeholders_path": knockout_path,
        "tournament_structure_path": structure_path,
        "validation_report_path": str(validation_report_path),
    }


if __name__ == "__main__":
    print(prepare_step11_tournament_setup())
