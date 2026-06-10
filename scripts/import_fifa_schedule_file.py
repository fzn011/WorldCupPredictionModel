#!/usr/bin/env python
"""Import FIFA downloadable schedule file into populated fixtures/venues (Step 17F)."""

from __future__ import annotations

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import pandas as pd

from src.official.fifa_schedule_importer import (
    normalize_schedule_to_official_schema,
    save_populated_schedule_outputs,
)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Import FIFA schedule file")
    parser.add_argument("--file", required=True, help="Path to FIFA schedule CSV/XLSX")
    args = parser.parse_args()

    path = args.file
    if path.lower().endswith((".xlsx", ".xls")):
        raw = pd.read_excel(path)
    else:
        raw = pd.read_csv(path)

    fixtures_df, venues_df, audit_df = normalize_schedule_to_official_schema(raw)
    outputs = save_populated_schedule_outputs(fixtures_df, venues_df, audit_df)

    warnings = audit_df["warnings"].fillna("").tolist() if not audit_df.empty and "warnings" in audit_df.columns else []

    print("=" * 60)
    print("Step 17F: Import FIFA Schedule File")
    print("=" * 60)
    print(f"rows imported:    {len(raw)}")
    print(f"fixtures saved:   {len(fixtures_df)} -> {outputs.get('fixtures_path')}")
    print(f"venues saved:     {len(venues_df)} -> {outputs.get('venues_path')}")
    print(f"audit path:       {outputs.get('audit_path')}")
    if warnings:
        print("warnings:")
        for w in warnings:
            if w:
                print(f"  - {w}")
    print("=" * 60)


if __name__ == "__main__":
    main()
