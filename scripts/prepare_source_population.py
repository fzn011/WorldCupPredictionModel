#!/usr/bin/env python
"""Step 17E: Prepare source-assisted official FIFA data population pack."""

from __future__ import annotations

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.official.prepare_source_population import prepare_step17e_source_assisted_population


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Step 17E source-assisted population")
    parser.add_argument("--download", action="store_true", help="Download official FIFA source snapshots")
    parser.add_argument("--force", action="store_true", help="Force re-download snapshots")
    parser.add_argument("--no-parse", action="store_true", help="Skip parsing snapshots")
    parser.add_argument("--no-pack", action="store_true", help="Skip import pack zip creation")
    args = parser.parse_args()

    result = prepare_step17e_source_assisted_population(
        download_sources=args.download,
        parse_sources=not args.no_parse,
        create_pack=not args.no_pack,
        force_download=args.force,
    )

    print("=" * 60)
    print("Step 17E: Source-Assisted Official FIFA Data Population")
    print("=" * 60)
    print(f"Status:                    {result.get('status')}")
    print(f"Staged teams count:        {result.get('staged_teams_count')}")
    print(f"Staged groups count:       {result.get('staged_groups_count')}")
    print(f"Staged fixtures count:     {result.get('staged_fixtures_count')}")
    print(f"Staged venues count:       {result.get('staged_venues_count')}")
    print(f"Staged players count:      {result.get('staged_players_count')}")
    print(f"Staging validation passed: {result.get('staging_validation_passed')}")
    print(f"Parse warnings count:      {result.get('parse_warnings_count')}")
    print(f"Import pack path:          {result.get('import_pack_path')}")
    print(f"final_ready:               {result.get('final_ready')}")
    print(f"Registry path:             {result.get('registry_path')}")
    print(f"Summary path:              {result.get('summary_path')}")
    if result.get("notes"):
        print("\nNotes:")
        for note in result["notes"]:
            print(f"  - {note}")
    print("=" * 60)


if __name__ == "__main__":
    main()
