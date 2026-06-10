"""CLI script to inspect official World Cup squad data.

Usage:
    python scripts/inspect_official_squads.py
"""

from __future__ import annotations

import sys
import pandas as pd
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.utils.constants import (
    PROJECT_ROOT,
    OFFICIAL_PROCESSED_DIR,
    PROCESSED_DATA_DIR,
    OFFICIAL_SQUAD_SUMMARY_FILE,
    OFFICIAL_SQUAD_VALIDATION_REPORT_FILE,
    OFFICIAL_PLAYER_PRIOR_MERGE_REPORT_FILE,
    OFFICIAL_PLAYERS_FILE,
    OFFICIAL_SQUADS_FILE,
    OFFICIAL_AWARD_CANDIDATES_FILE,
)


def main():
    print("=" * 80)
    print("OFFICIAL WORLD CUP SQUAD INSPECTION")
    print("=" * 80)
    print()
    
    base_path = PROJECT_ROOT / OFFICIAL_PROCESSED_DIR
    processed_path = PROJECT_ROOT / PROCESSED_DATA_DIR
    
    # Check if data exists
    summary_path = base_path / OFFICIAL_SQUAD_SUMMARY_FILE
    if not summary_path.exists():
        print("Run python scripts/prepare_official_squads.py first")
        return 1
    
    # Load and print summary
    print("1. SQUAD SUMMARY")
    print("-" * 80)
    try:
        with open(summary_path) as f:
            summary = json.load(f)
        
        print(f"Status: {summary.get('status', 'unknown')}")
        print(f"Validation passed: {summary.get('validation_passed', False)}")
        print(f"Official players: {summary.get('official_players_count', 0)}")
        print(f"Teams: {summary.get('official_teams_with_players', 0)}")
        print(f"Teams with 26 players: {summary.get('teams_with_26_players', 0)}/48")
        print(f"Award candidates: {summary.get('official_award_candidates_count', 0)}")
        print(f"Unmatched priors: {summary.get('unmatched_priors_count', 0)}")
        print(f"Errors: {summary.get('errors_count', 0)}")
        print(f"Warnings: {summary.get('warnings_count', 0)}")
        print(f"Sample/template rows: {summary.get('sample_to_be_verified_count', 0)}")
        
        if summary.get("notes"):
            print("\nNotes:")
            for note in summary["notes"]:
                print(f"  - {note}")
    except Exception as e:
        print(f"Error loading summary: {e}")
    
    print()
    print()
    
    # Print players by team
    print("2. PLAYERS BY TEAM")
    print("-" * 80)
    try:
        players_path = base_path / OFFICIAL_PLAYERS_FILE
        if players_path.exists():
            players = pd.read_csv(players_path)
            
            for team in sorted(players["team"].unique()):
                team_players = players[players["team"] == team]
                gk = len(team_players[team_players["position_code"] == "GK"])
                df = len(team_players[team_players["position_code"] == "DF"])
                mf = len(team_players[team_players["position_code"] == "MF"])
                fw = len(team_players[team_players["position_code"] == "FW"])
                
                print(f"{team:20s} - Total: {len(team_players):2d} (GK:{gk} DF:{df} MF:{mf} FW:{fw})")
    except Exception as e:
        print(f"Could not load players: {e}")
    
    print()
    print()
    
    # Print squads summary
    print("3. SQUAD SUMMARY TABLE")
    print("-" * 80)
    try:
        squads_path = base_path / OFFICIAL_SQUADS_FILE
        if squads_path.exists():
            squads = pd.read_csv(squads_path)
            print(squads.to_string(index=False))
    except Exception as e:
        print(f"Could not load squads: {e}")
    
    print()
    print()
    
    # Print validation report
    print("4. VALIDATION ISSUES (first 15)")
    print("-" * 80)
    try:
        report_path = base_path / OFFICIAL_SQUAD_VALIDATION_REPORT_FILE
        if report_path.exists():
            report = pd.read_csv(report_path)
            
            if len(report) == 0:
                print("No validation issues found")
            else:
                errors = report[report["severity"] == "error"]
                warnings = report[report["severity"] == "warning"]
                
                print(f"Errors: {len(errors)}, Warnings: {len(warnings)}")
                print()
                print(report.head(15).to_string(index=False))
        else:
            print("No validation report found")
    except Exception as e:
        print(f"Could not load validation report: {e}")
    
    print()
    print()
    
    # Print unmatched priors
    print("5. UNMATCHED PRIORS (first 10)")
    print("-" * 80)
    try:
        merge_path = base_path / OFFICIAL_PLAYER_PRIOR_MERGE_REPORT_FILE
        if merge_path.exists():
            unmatched = pd.read_csv(merge_path)
            
            if len(unmatched) == 0:
                print("No unmatched priors")
            else:
                print(f"Total unmatched: {len(unmatched)}")
                print()
                print(unmatched.head(10).to_string(index=False))
        else:
            print("No merge report found")
    except Exception as e:
        print(f"Could not load merge report: {e}")
    
    print()
    print()
    
    # Print award candidates preview
    print("6. AWARD CANDIDATES PREVIEW (first 10)")
    print("-" * 80)
    try:
        candidates_path = processed_path / OFFICIAL_AWARD_CANDIDATES_FILE
        if candidates_path.exists():
            candidates = pd.read_csv(candidates_path)
            
            preview_cols = ["player_name", "team", "position", "base_player_rating", 
                           "expected_minutes_share", "has_player_prior"]
            
            print(f"Total candidates: {len(candidates)}")
            print()
            print(candidates[preview_cols].head(10).to_string(index=False))
        else:
            print("No award candidates found")
    except Exception as e:
        print(f"Could not load award candidates: {e}")
    
    print()
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
