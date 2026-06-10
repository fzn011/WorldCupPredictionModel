"""Validate official World Cup squad data.

Comprehensive validators for official players, squads, team-player maps,
player priors, and award candidates. All return tuple[bool, pd.DataFrame]
with validation report containing severity levels (error/warning).
"""

from __future__ import annotations

import pandas as pd
from src.utils.constants import (
    OFFICIAL_REQUIRED_PLAYERS_PER_TEAM,
    OFFICIAL_REQUIRED_TOTAL_PLAYERS,
    OFFICIAL_POSITION_CODES,
    OFFICIAL_POSITION_MAP,
    OFFICIAL_PLAYERS_REQUIRED_COLUMNS,
    OFFICIAL_AWARD_CANDIDATES_REQUIRED_COLUMNS,
    PLAYER_PRIOR_REQUIRED_COLUMNS,
)
from src.official.squad_contracts import check_squad_required_columns


def validate_official_players(
    players_df: pd.DataFrame,
    official_teams_df: pd.DataFrame | None = None,
    strict_squad_size: bool = False,
) -> tuple[bool, pd.DataFrame]:
    """Validate official World Cup players.
    
    Args:
        players_df: DataFrame with official players.
        official_teams_df: Optional official teams for cross-check.
        strict_squad_size: If True, error on incomplete squads. If False, warn.
        
    Returns:
        (validation_passed, report_df)
        Report has columns: severity, row_index, field, value, message
    """
    report_rows = []
    # Check required columns
    has_cols, missing = check_squad_required_columns(
        players_df,
        OFFICIAL_PLAYERS_REQUIRED_COLUMNS,
        "official_players"
    )
    if not has_cols:
        for col in missing:
            report_rows.append({
                "severity": "error",
                "row_index": -1,
                "field": col,
                "value": "N/A",
                "message": f"Missing required column: {col}",
            })
        # Return early if required columns are missing
        return (False, pd.DataFrame(report_rows))
    
    # Check each row
    for idx, row in players_df.iterrows():
        # player_id unique
        if players_df[players_df["player_id"] == row["player_id"]].shape[0] > 1:
            report_rows.append({
                "severity": "error",
                "row_index": idx,
                "field": "player_id",
                "value": row["player_id"],
                "message": "Duplicate player_id",
            })
        
        # player_name not empty
        if pd.isna(row["player_name"]) or str(row["player_name"]).strip() == "":
            report_rows.append({
                "severity": "error",
                "row_index": idx,
                "field": "player_name",
                "value": "",
                "message": "player_name cannot be empty",
            })
        
        # team not empty
        if pd.isna(row["team"]) or str(row["team"]).strip() == "":
            report_rows.append({
                "severity": "error",
                "row_index": idx,
                "field": "team",
                "value": "",
                "message": "team cannot be empty",
            })
        
        # position_code valid
        pos_code = str(row.get("position_code", "")).upper().strip()
        if pos_code not in OFFICIAL_POSITION_CODES:
            report_rows.append({
                "severity": "error",
                "row_index": idx,
                "field": "position_code",
                "value": pos_code,
                "message": f"Invalid position_code. Must be one of: {OFFICIAL_POSITION_CODES}",
            })
        
        # position matches position_code
        if pos_code in OFFICIAL_POSITION_MAP:
            expected_pos = OFFICIAL_POSITION_MAP[pos_code]
            actual_pos = str(row.get("position", "")).lower().strip()
            if actual_pos != expected_pos:
                report_rows.append({
                    "severity": "warning",
                    "row_index": idx,
                    "field": "position",
                    "value": actual_pos,
                    "message": f"position '{actual_pos}' does not match position_code '{pos_code}' (expected '{expected_pos}')",
                })
        
        # source tracking
        if row.get("source") == "sample_to_be_verified":
            report_rows.append({
                "severity": "warning",
                "row_index": idx,
                "field": "source",
                "value": "sample_to_be_verified",
                "message": "Player from sample template - requires official verification",
            })
    
    # Check squad sizes
    teams_count = {}
    for team in players_df["team"].unique():
        team_players = players_df[players_df["team"] == team]
        count = len(team_players)
        teams_count[team] = count
        
        if count < OFFICIAL_REQUIRED_PLAYERS_PER_TEAM:
            severity = "error" if strict_squad_size else "warning"
            report_rows.append({
                "severity": severity,
                "row_index": -1,
                "field": "team",
                "value": team,
                "message": f"Team '{team}' has {count} players, expected {OFFICIAL_REQUIRED_PLAYERS_PER_TEAM}",
            })
    
    # Check total players
    total = len(players_df)
    if total < OFFICIAL_REQUIRED_TOTAL_PLAYERS:
        severity = "error" if strict_squad_size else "warning"
        report_rows.append({
            "severity": severity,
            "row_index": -1,
            "field": "total_count",
            "value": str(total),
            "message": f"Total {total} players, expected {OFFICIAL_REQUIRED_TOTAL_PLAYERS}",
        })
    
    report = pd.DataFrame(report_rows) if report_rows else pd.DataFrame(
        columns=["severity", "row_index", "field", "value", "message"]
    )
    
    # Validation passes if no error rows
    passed = len(report[report["severity"] == "error"]) == 0
    
    return passed, report


def validate_official_squads(
    squads_df: pd.DataFrame,
    players_df: pd.DataFrame | None = None,
) -> tuple[bool, pd.DataFrame]:
    """Validate official squad summaries.
    
    Args:
        squads_df: DataFrame with squad summaries.
        players_df: Optional players for cross-check.
        
    Returns:
        (validation_passed, report_df)
    """
    report_rows = []
    
    # Check required columns
    required_cols = ["team", "team_code", "player_count", "goalkeepers", 
                     "defenders", "midfielders", "forwards"]
    has_cols, missing = check_squad_required_columns(squads_df, required_cols)
    if not has_cols:
        for col in missing:
            report_rows.append({
                "severity": "error",
                "row_index": -1,
                "field": col,
                "value": "N/A",
                "message": f"Missing required column: {col}",
            })
    
    for idx, row in squads_df.iterrows():
        team = row["team"]
        expected_count = row.get("player_count", 0)
        
        # Check position counts sum to player_count
        pos_sum = (row.get("goalkeepers", 0) + row.get("defenders", 0) + 
                   row.get("midfielders", 0) + row.get("forwards", 0))
        
        if pos_sum != expected_count:
            report_rows.append({
                "severity": "warning",
                "row_index": idx,
                "field": "player_count",
                "value": str(expected_count),
                "message": f"Position counts sum ({pos_sum}) != player_count ({expected_count})",
            })
        
        # Cross-check with players if provided
        if players_df is not None:
            team_players = players_df[players_df["team"] == team]
            actual_count = len(team_players)
            
            if actual_count != expected_count:
                report_rows.append({
                    "severity": "warning",
                    "row_index": idx,
                    "field": "player_count",
                    "value": str(expected_count),
                    "message": f"Squad says {expected_count} players, but {actual_count} in official_players.csv",
                })
    
    report = pd.DataFrame(report_rows) if report_rows else pd.DataFrame(
        columns=["severity", "row_index", "field", "value", "message"]
    )
    
    passed = len(report[report["severity"] == "error"]) == 0
    return passed, report


def validate_team_player_map(
    map_df: pd.DataFrame,
    players_df: pd.DataFrame,
    official_teams_df: pd.DataFrame | None = None,
) -> tuple[bool, pd.DataFrame]:
    """Validate team-player map.
    
    Args:
        map_df: DataFrame with team-player mappings.
        players_df: Official players for validation.
        official_teams_df: Optional official teams.
        
    Returns:
        (validation_passed, report_df)
    """
    report_rows = []
    
    required_cols = ["team", "team_code", "player_id", "player_name", 
                     "position_code", "position", "shirt_number"]
    has_cols, missing = check_squad_required_columns(map_df, required_cols)
    if not has_cols:
        for col in missing:
            report_rows.append({
                "severity": "error",
                "row_index": -1,
                "field": col,
                "value": "N/A",
                "message": f"Missing required column: {col}",
            })
    
    official_player_ids = set(players_df["player_id"].unique())
    
    for idx, row in map_df.iterrows():
        player_id = row["player_id"]
        
        # Check player_id exists in official_players
        if player_id not in official_player_ids:
            report_rows.append({
                "severity": "error",
                "row_index": idx,
                "field": "player_id",
                "value": str(player_id),
                "message": f"player_id not found in official_players.csv",
            })
        
        # Check no duplicate player-team
        dup = map_df[(map_df["player_id"] == player_id) & (map_df["team"] == row["team"])]
        if len(dup) > 1:
            report_rows.append({
                "severity": "error",
                "row_index": idx,
                "field": "player_id",
                "value": str(player_id),
                "message": f"Duplicate player in team {row['team']}",
            })
    
    report = pd.DataFrame(report_rows) if report_rows else pd.DataFrame(
        columns=["severity", "row_index", "field", "value", "message"]
    )
    
    passed = len(report[report["severity"] == "error"]) == 0
    return passed, report


def validate_player_award_priors(
    priors_df: pd.DataFrame,
    official_players_df: pd.DataFrame | None = None,
) -> tuple[bool, pd.DataFrame]:
    """Validate player award priors.
    
    Args:
        priors_df: DataFrame with player priors.
        official_players_df: Optional for cross-check.
        
    Returns:
        (validation_passed, report_df)
    """
    report_rows = []
    
    has_cols, missing = check_squad_required_columns(priors_df, PLAYER_PRIOR_REQUIRED_COLUMNS)
    if not has_cols:
        for col in missing:
            report_rows.append({
                "severity": "error",
                "row_index": -1,
                "field": col,
                "value": "N/A",
                "message": f"Missing required column: {col}",
            })
    
    official_player_set = set()
    if official_players_df is not None:
        for _, row in official_players_df.iterrows():
            # Use player_name from official_players_df since that's the column name there
            official_player_set.add((row["player_name"], row["team"]))
    
    for idx, row in priors_df.iterrows():
        # Check numeric columns
        for col in ["base_player_rating", "expected_minutes_share", "goals_prior",
                    "assists_prior", "chance_creation_prior", "defensive_actions_prior",
                    "goalkeeper_actions_prior", "discipline_risk", "star_role_score", "flair_score"]:
            try:
                float(row.get(col, 0))
            except (ValueError, TypeError):
                report_rows.append({
                    "severity": "error",
                    "row_index": idx,
                    "field": col,
                    "value": str(row.get(col, "")),
                    "message": f"{col} must be numeric",
                })
        
        # Check expected_minutes_share range
        try:
            ems = float(row.get("expected_minutes_share", 0.5))
            if not (0 <= ems <= 1):
                report_rows.append({
                    "severity": "warning",
                    "row_index": idx,
                    "field": "expected_minutes_share",
                    "value": str(ems),
                    "message": "expected_minutes_share should be between 0 and 1",
                })
        except (ValueError, TypeError):
            pass
        
        # Check player/team not empty
        player = str(row.get("player", "")).strip()
        team = str(row.get("team", "")).strip()
        
        if not player or not team:
            report_rows.append({
                "severity": "error",
                "row_index": idx,
                "field": "player" if not player else "team",
                "value": player if player else team,
                "message": "player and team cannot be empty",
            })
        
        # Check if unmatched (if official_players provided)
        if official_players_df is not None:
            if (player, team) not in official_player_set:
                report_rows.append({
                    "severity": "warning",
                    "row_index": idx,
                    "field": "player",
                    "value": f"{player} ({team})",
                    "message": "Player not in official_players - will be excluded from candidates",
                })
    
    report = pd.DataFrame(report_rows) if report_rows else pd.DataFrame(
        columns=["severity", "row_index", "field", "value", "message"]
    )
    
    passed = len(report[report["severity"] == "error"]) == 0
    return passed, report


def validate_official_award_candidates(
    candidates_df: pd.DataFrame,
    official_players_df: pd.DataFrame,
) -> tuple[bool, pd.DataFrame]:
    """Validate official award candidates (must be subset of official_players).
    
    Args:
        candidates_df: DataFrame with award candidates.
        official_players_df: Official players for validation.
        
    Returns:
        (validation_passed, report_df)
    """
    report_rows = []
    
    has_cols, missing = check_squad_required_columns(candidates_df, OFFICIAL_AWARD_CANDIDATES_REQUIRED_COLUMNS)
    if not has_cols:
        for col in missing:
            report_rows.append({
                "severity": "error",
                "row_index": -1,
                "field": col,
                "value": "N/A",
                "message": f"Missing required column: {col}",
            })
    
    official_player_ids = set(official_players_df["player_id"].unique())
    
    for idx, row in candidates_df.iterrows():
        player_id = row["player_id"]
        
        # Must be in official_players
        if player_id not in official_player_ids:
            report_rows.append({
                "severity": "error",
                "row_index": idx,
                "field": "player_id",
                "value": str(player_id),
                "message": "Candidate player not in official_players.csv - CRITICAL DATA INTEGRITY ERROR",
            })
        
        # Check expected_minutes_share
        try:
            ems = float(row.get("expected_minutes_share", 0.5))
            if not (0 <= ems <= 1):
                report_rows.append({
                    "severity": "warning",
                    "row_index": idx,
                    "field": "expected_minutes_share",
                    "value": str(ems),
                    "message": "expected_minutes_share out of range [0, 1]",
                })
        except (ValueError, TypeError):
            pass
    
    report = pd.DataFrame(report_rows) if report_rows else pd.DataFrame(
        columns=["severity", "row_index", "field", "value", "message"]
    )
    
    passed = len(report[report["severity"] == "error"]) == 0
    return passed, report


def validate_squad_bundle(
    official_players_df: pd.DataFrame,
    official_squads_df: pd.DataFrame,
    official_team_player_map_df: pd.DataFrame,
    player_priors_df: pd.DataFrame,
    official_award_candidates_df: pd.DataFrame,
    official_teams_df: pd.DataFrame | None = None,
    strict_squad_size: bool = False,
) -> tuple[bool, pd.DataFrame]:
    """Validate entire squad bundle.
    
    Args:
        official_players_df: Official players.
        official_squads_df: Squad summaries.
        official_team_player_map_df: Team-player map.
        player_priors_df: Player priors.
        official_award_candidates_df: Award candidates.
        official_teams_df: Optional official teams.
        strict_squad_size: Strict validation flag.
        
    Returns:
        (validation_passed, combined_report_df)
    """
    all_reports = []
    
    # Validate each component
    _, players_report = validate_official_players(official_players_df, official_teams_df, strict_squad_size)
    if len(players_report) > 0:
        players_report["component"] = "official_players"
        all_reports.append(players_report)
    
    _, squads_report = validate_official_squads(official_squads_df, official_players_df)
    if len(squads_report) > 0:
        squads_report["component"] = "official_squads"
        all_reports.append(squads_report)
    
    _, map_report = validate_team_player_map(official_team_player_map_df, official_players_df)
    if len(map_report) > 0:
        map_report["component"] = "team_player_map"
        all_reports.append(map_report)
    
    _, priors_report = validate_player_award_priors(player_priors_df, official_players_df)
    if len(priors_report) > 0:
        priors_report["component"] = "player_priors"
        all_reports.append(priors_report)
    
    _, candidates_report = validate_official_award_candidates(official_award_candidates_df, official_players_df)
    if len(candidates_report) > 0:
        candidates_report["component"] = "award_candidates"
        all_reports.append(candidates_report)
    
    # Combine reports
    if all_reports:
        combined = pd.concat(all_reports, ignore_index=True)
    else:
        combined = pd.DataFrame(
            columns=["severity", "row_index", "field", "value", "message", "component"]
        )
    
    passed = len(combined[combined["severity"] == "error"]) == 0
    return passed, combined
