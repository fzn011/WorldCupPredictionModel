"""CLI script to prepare official World Cup squads and player priors.

Usage:
    python scripts/prepare_official_squads.py [--strict-squad-size] [--overwrite-priors]
"""

from __future__ import annotations

import sys
import argparse
import pandas as pd
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.official.prepare_squads import prepare_step17b_official_squads_and_priors
from src.official.squad_loaders import load_official_players


def main():
    parser = argparse.ArgumentParser(
        description="Prepare official World Cup squads and player priors (Step 17B)"
    )
    parser.add_argument(
        "--strict-squad-size",
        action="store_true",
        help="Fail validation if squads are incomplete (default: warn only)"
    )
    parser.add_argument(
        "--overwrite-priors",
        action="store_true",
        help="Regenerate player priors template even if file exists"
    )
    
    args = parser.parse_args()
    
    # Run orchestrator
    print("Preparing Step 17B: Official squads and player priors...")
    print()
    
    result = prepare_step17b_official_squads_and_priors(
        strict_squad_size=args.strict_squad_size,
        overwrite_priors=args.overwrite_priors,
    )
    
    # Print summary
    print(f"Status: {result.get('status', 'unknown')}")
    print(f"Validation passed: {result.get('validation_passed', False)}")
    print(f"Official players count: {result.get('official_players_count', 0)}")
    print(f"Teams with players: {result.get('official_teams_with_players', 0)}")
    print(f"Teams with 26 players: {result.get('teams_with_26_players', 0)}/48")
    print(f"Official award candidates: {result.get('official_award_candidates_count', 0)}")
    print(f"Unmatched priors: {result.get('unmatched_priors_count', 0)}")
    print(f"Errors: {result.get('errors_count', 0)}")
    print(f"Warnings: {result.get('warnings_count', 0)}")
    print(f"Sample/template rows: {result.get('sample_to_be_verified_count', 0)}")
    print()
    
    if result.get("notes"):
        print("Notes:")
        for note in result["notes"]:
            print(f"  - {note}")
        print()
    
    # Print output paths
    print("Output files:")
    print(f"  Official players: {result.get('official_players_path', 'N/A')}")
    print(f"  Official squads: {result.get('official_squads_path', 'N/A')}")
    print(f"  Team-player map: {result.get('official_team_player_map_path', 'N/A')}")
    print(f"  Player priors: {result.get('player_award_priors_path', 'N/A')}")
    print(f"  Award candidates: {result.get('official_award_candidates_path', 'N/A')}")
    print(f"  Validation report: {result.get('validation_report_path', 'N/A')}")
    print(f"  Prior merge report: {result.get('prior_merge_report_path', 'N/A')}")
    print(f"  Squad summary: {result.get('squad_summary_path', 'N/A')}")
    print()
    
    # Print validation issues if any
    if result.get("errors_count", 0) > 0 or result.get("warnings_count", 0) > 0:
        print("Validation report (first 20 issues):")
        try:
            report_path = result.get("validation_report_path")
            if report_path:
                report = pd.read_csv(report_path)
                print(report.head(20).to_string(index=False))
        except Exception as e:
            print(f"  Could not load report: {e}")
    
    return 0 if result.get("validation_passed") else 1


if __name__ == "__main__":
    sys.exit(main())
