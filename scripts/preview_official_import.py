#!/usr/bin/env python
"""Preview an official import file before applying."""

from __future__ import annotations

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.official.import_diff import preview_official_import, save_import_diff_report


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Preview official import diff")
    parser.add_argument("--target", "-t", required=True,
                        choices=["teams", "groups", "fixtures", "venues", "players", "player_priors"])
    parser.add_argument("--file", "-f", required=True, help="Path to import CSV file")
    args = parser.parse_args()

    print("=" * 60)
    print("FIFA World Cup 2026 - Import Preview (Step 17D)")
    print("=" * 60)

    diff_df = preview_official_import(args.file, args.target)
    diff_path = save_import_diff_report(diff_df)

    added = int((diff_df["change_type"] == "added_row").sum()) if not diff_df.empty else 0
    removed = int((diff_df["change_type"] == "removed_row").sum()) if not diff_df.empty else 0
    changed = int((diff_df["change_type"] == "changed_value").sum()) if not diff_df.empty else 0
    unchanged = int((diff_df["change_type"] == "unchanged").sum()) if not diff_df.empty else 0

    print(f"\nTarget:           {args.target}")
    print(f"File:             {args.file}")
    print(f"Added rows:       {added}")
    print(f"Removed rows:     {removed}")
    print(f"Changed values:   {changed}")
    print(f"Unchanged rows:   {unchanged}")
    print(f"Diff report path: {diff_path}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
