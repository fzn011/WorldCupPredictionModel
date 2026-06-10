#!/usr/bin/env python
"""Import FIFA squad CSV/XLSX into populated official players (Step 17F)."""

from __future__ import annotations

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import pandas as pd

from src.official.fifa_squad_importer import (
    normalize_squad_to_official_schema,
    save_populated_squad_outputs,
    validate_imported_squad_completeness,
)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Import FIFA squad file")
    parser.add_argument("--file", required=True, help="Path to FIFA squad CSV/XLSX")
    args = parser.parse_args()

    path = args.file
    if path.lower().endswith((".xlsx", ".xls")):
        raw = pd.read_excel(path)
    else:
        raw = pd.read_csv(path)

    players_df, audit_df = normalize_squad_to_official_schema(raw)
    outputs = save_populated_squad_outputs(players_df, audit_df)
    passed, validation = validate_imported_squad_completeness(players_df)

    teams = players_df["team"].nunique() if not players_df.empty else 0
    per_team = players_df.groupby("team").size() if not players_df.empty else pd.Series(dtype=int)
    teams_26 = int((per_team == 26).sum()) if len(per_team) else 0

    warnings = audit_df["warnings"].fillna("").tolist() if not audit_df.empty and "warnings" in audit_df.columns else []

    print("=" * 60)
    print("Step 17F: Import FIFA Squad File")
    print("=" * 60)
    print(f"players imported:      {len(players_df)}")
    print(f"teams found:           {teams}")
    print(f"teams with 26 players: {teams_26}")
    print(f"validation passed:     {passed}")
    print(f"audit path:            {outputs.get('audit_path')}")
    if not validation.empty:
        print("\nValidation:")
        print(validation.to_string(index=False))
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            if w:
                print(f"  - {w}")
    print("=" * 60)


if __name__ == "__main__":
    main()
