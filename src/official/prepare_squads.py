"""Orchestrate Step 17B: Official squads and player priors merge.

Main entry point for preparing official World Cup squads and player priors.
Generates all necessary files for award candidates layer.
"""

from __future__ import annotations

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

from src.utils.constants import (
    PROJECT_ROOT,
    OFFICIAL_PROCESSED_DIR,
    PROCESSED_DATA_DIR,
    SAMPLE_DATA_DIR,
    OFFICIAL_PLAYERS_FILE,
    OFFICIAL_SQUADS_FILE,
    OFFICIAL_TEAM_PLAYER_MAP_FILE,
    OFFICIAL_SQUAD_SUMMARY_FILE,
    OFFICIAL_SQUAD_VALIDATION_REPORT_FILE,
    OFFICIAL_PLAYER_PRIOR_MERGE_REPORT_FILE,
    PLAYER_AWARD_PRIORS_FILE,
    OFFICIAL_AWARD_CANDIDATES_FILE,
    SAMPLE_PLAYER_AWARD_PRIORS_FILE,
    SAMPLE_PLAYER_CANDIDATES_FILE,
)
from src.official.loaders import load_official_teams
from src.official.squad_parser import create_official_players_template_from_sample
from src.official.squad_loaders import load_official_players
from src.official.player_registry import (
    build_official_squads_summary,
    build_team_player_map,
    merge_player_priors_with_official_players,
)
from src.official.squad_validators import validate_squad_bundle
from src.awards.player_priors import create_player_award_priors_template, save_player_award_priors_template


def prepare_step17b_official_squads_and_priors(
    strict_squad_size: bool = False,
    overwrite_priors: bool = False,
) -> dict:
    """Main orchestrator for Step 17B: Official squads + player priors.
    
    Workflow:
    1. Load official teams from Step 17A
    2. If official_players.csv missing, create template from sample
    3. Load official players
    4. Build squad summaries and team-player maps
    5. If player_award_priors.csv missing, create template
    6. Load player priors
    7. Merge priors with official players → award candidates
    8. Validate bundle
    9. Save all outputs
    10. Return summary
    
    Args:
        strict_squad_size: If True, error on incomplete squads. If False, warn.
        overwrite_priors: If True, regenerate priors template even if exists.
        
    Returns:
        Summary dict with status, counts, paths, and diagnostics.
    """
    # Ensure output directories
    (PROJECT_ROOT / OFFICIAL_PROCESSED_DIR).mkdir(parents=True, exist_ok=True)
    (PROJECT_ROOT / PROCESSED_DATA_DIR).mkdir(parents=True, exist_ok=True)
    
    # Load official teams from Step 17A
    try:
        official_teams = load_official_teams()
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to load official teams from Step 17A: {e}",
            "validation_passed": False,
        }
    
    # Step 1: Handle official players
    official_players_path = PROJECT_ROOT / OFFICIAL_PROCESSED_DIR / OFFICIAL_PLAYERS_FILE
    
    if not official_players_path.exists():
        # Create template from sample players
        try:
            sample_path = PROJECT_ROOT / SAMPLE_DATA_DIR / SAMPLE_PLAYER_CANDIDATES_FILE
            sample_df = pd.read_csv(sample_path)
            official_players_df = create_official_players_template_from_sample(sample_df, official_teams)
            official_players_df.to_csv(official_players_path, index=False)
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to create official players template: {e}",
                "validation_passed": False,
            }
    
    # Load official players
    try:
        official_players_df = load_official_players()
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to load official players: {e}",
            "validation_passed": False,
        }
    
    # Step 2: Build squad summaries and team-player map
    try:
        official_squads_df = build_official_squads_summary(official_players_df)
        official_team_player_map_df = build_team_player_map(official_players_df)
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to build squad summaries: {e}",
            "validation_passed": False,
        }
    
    # Step 3: Handle player award priors
    player_priors_path = PROJECT_ROOT / PROCESSED_DATA_DIR / PLAYER_AWARD_PRIORS_FILE
    
    if not player_priors_path.exists() or overwrite_priors:
        try:
            priors_template = create_player_award_priors_template(official_players_df)
            save_player_award_priors_template(priors_template, str(player_priors_path), overwrite=True)
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to create/save player priors template: {e}",
                "validation_passed": False,
            }
    
    # Load player priors
    try:
        from src.official.squad_loaders import load_player_award_priors
        player_priors_df = load_player_award_priors()
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to load player priors: {e}",
            "validation_passed": False,
        }
    
    # Step 4: Merge priors with players
    try:
        official_award_candidates_df, unmatched_priors_df = merge_player_priors_with_official_players(
            official_players_df,
            player_priors_df,
        )
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to merge priors with players: {e}",
            "validation_passed": False,
        }
    
    # Step 5: Validate bundle
    try:
        # Ensure player column exists in priors for validation
        if "player" not in player_priors_df.columns and "player_name" in player_priors_df.columns:
            player_priors_df["player"] = player_priors_df["player_name"]
        
        validation_passed, validation_report = validate_squad_bundle(
            official_players_df,
            official_squads_df,
            official_team_player_map_df,
            player_priors_df,
            official_award_candidates_df,
            official_teams,
            strict_squad_size=strict_squad_size,
        )
    except Exception as e:
        return {
            "status": "error",
            "error": f"Validation failed: {e}",
            "validation_passed": False,
        }
    
    # Step 6: Save all outputs
    try:
        official_players_df.to_csv(official_players_path, index=False)
        official_squads_df.to_csv(
            PROJECT_ROOT / OFFICIAL_PROCESSED_DIR / OFFICIAL_SQUADS_FILE,
            index=False
        )
        official_team_player_map_df.to_csv(
            PROJECT_ROOT / OFFICIAL_PROCESSED_DIR / OFFICIAL_TEAM_PLAYER_MAP_FILE,
            index=False
        )
        official_award_candidates_df.to_csv(
            PROJECT_ROOT / PROCESSED_DATA_DIR / OFFICIAL_AWARD_CANDIDATES_FILE,
            index=False
        )
        validation_report.to_csv(
            PROJECT_ROOT / OFFICIAL_PROCESSED_DIR / OFFICIAL_SQUAD_VALIDATION_REPORT_FILE,
            index=False
        )
        unmatched_priors_df.to_csv(
            PROJECT_ROOT / OFFICIAL_PROCESSED_DIR / OFFICIAL_PLAYER_PRIOR_MERGE_REPORT_FILE,
            index=False
        )
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to save outputs: {e}",
            "validation_passed": False,
        }
    
    # Step 7: Generate summary JSON
    sample_to_be_verified_count = len(
        official_players_df[official_players_df["source"] == "sample_to_be_verified"]
    )
    
    teams_with_26 = 0
    for team in official_players_df["team"].unique():
        team_players = official_players_df[official_players_df["team"] == team]
        if len(team_players) == 26:
            teams_with_26 += 1
    
    errors_in_report = len(validation_report[validation_report["severity"] == "error"])
    warnings_in_report = len(validation_report[validation_report["severity"] == "warning"])
    
    # Determine status
    if errors_in_report > 0:
        status = "error"
    elif sample_to_be_verified_count > 0 or teams_with_26 < len(official_players_df["team"].unique()):
        status = "needs_verification"
    else:
        status = "ok"
    
    summary = {
        "status": status,
        "validation_passed": validation_passed,
        "strict_squad_size": strict_squad_size,
        "official_players_count": len(official_players_df),
        "official_teams_with_players": len(official_players_df["team"].unique()),
        "expected_total_players": 1248,
        "teams_with_26_players": teams_with_26,
        "official_award_candidates_count": len(official_award_candidates_df),
        "unmatched_priors_count": len(unmatched_priors_df),
        "errors_count": errors_in_report,
        "warnings_count": warnings_in_report,
        "sample_to_be_verified_count": sample_to_be_verified_count,
        "official_players_path": str(official_players_path),
        "official_squads_path": str(PROJECT_ROOT / OFFICIAL_PROCESSED_DIR / OFFICIAL_SQUADS_FILE),
        "official_team_player_map_path": str(PROJECT_ROOT / OFFICIAL_PROCESSED_DIR / OFFICIAL_TEAM_PLAYER_MAP_FILE),
        "player_award_priors_path": str(player_priors_path),
        "official_award_candidates_path": str(PROJECT_ROOT / PROCESSED_DATA_DIR / OFFICIAL_AWARD_CANDIDATES_FILE),
        "validation_report_path": str(PROJECT_ROOT / OFFICIAL_PROCESSED_DIR / OFFICIAL_SQUAD_VALIDATION_REPORT_FILE),
        "prior_merge_report_path": str(PROJECT_ROOT / OFFICIAL_PROCESSED_DIR / OFFICIAL_PLAYER_PRIOR_MERGE_REPORT_FILE),
        "notes": []
    }
    
    if status == "needs_verification":
        if sample_to_be_verified_count > 0:
            summary["notes"].append(
                f"Official players contain {sample_to_be_verified_count} sample/template rows marked "
                "'sample_to_be_verified' - these require official FIFA source verification"
            )
        if teams_with_26 < len(official_players_df["team"].unique()):
            summary["notes"].append(
                f"Only {teams_with_26}/{len(official_players_df['team'].unique())} teams have exactly 26 players"
            )
    
    # Save summary JSON
    summary_path = PROJECT_ROOT / OFFICIAL_PROCESSED_DIR / OFFICIAL_SQUAD_SUMMARY_FILE
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    
    summary["squad_summary_path"] = str(summary_path)
    
    return summary


if __name__ == "__main__":
    result = prepare_step17b_official_squads_and_priors()
    print(json.dumps(result, indent=2))
