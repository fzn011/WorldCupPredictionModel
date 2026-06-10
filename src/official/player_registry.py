"""Official player registry operations.

Builds squad summaries, team-player mappings, and merges player priors with
official players to create official award candidates with safe defaults.
"""

from __future__ import annotations

import pandas as pd
from datetime import datetime


def build_official_squads_summary(players_df: pd.DataFrame) -> pd.DataFrame:
    """Build squad summary from official players.
    
    Creates one row per team with player counts by position.
    
    Args:
        players_df: Official players DataFrame.
        
    Returns:
        Squad summary DataFrame with columns:
        team, team_code, player_count, goalkeepers, defenders, midfielders, 
        forwards, source, last_verified_at
    """
    summary_rows = []
    
    for team in sorted(players_df["team"].unique()):
        team_players = players_df[players_df["team"] == team]
        
        gk_count = len(team_players[team_players["position_code"] == "GK"])
        df_count = len(team_players[team_players["position_code"] == "DF"])
        mf_count = len(team_players[team_players["position_code"] == "MF"])
        fw_count = len(team_players[team_players["position_code"] == "FW"])
        total = len(team_players)
        
        # Get metadata from first player of team
        first_player = team_players.iloc[0]
        
        summary_rows.append({
            "team": team,
            "team_code": first_player.get("team_code", ""),
            "player_count": total,
            "goalkeepers": gk_count,
            "defenders": df_count,
            "midfielders": mf_count,
            "forwards": fw_count,
            "source": first_player.get("source", ""),
            "last_verified_at": first_player.get("last_verified_at", ""),
        })
    
    return pd.DataFrame(summary_rows)


def build_team_player_map(players_df: pd.DataFrame) -> pd.DataFrame:
    """Build team-to-player mappings from official players.
    
    Args:
        players_df: Official players DataFrame.
        
    Returns:
        Team-player map with columns:
        team, team_code, player_id, player_name, position_code, position, 
        shirt_number, source, last_verified_at
    """
    return players_df[[
        "team",
        "team_code",
        "player_id",
        "player_name",
        "position_code",
        "position",
        "shirt_number",
        "source",
        "last_verified_at",
    ]].copy()


def merge_player_priors_with_official_players(
    official_players_df: pd.DataFrame,
    player_priors_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Merge player priors with official players.
    
    Performs LEFT JOIN to keep all official players, enriching with priors
    where available. Conservative defaults for missing priors.
    
    Args:
        official_players_df: Official players.
        player_priors_df: Player award priors.
        
    Returns:
        (official_award_candidates_df, unmatched_priors_report_df)
    """
    # Standardize player and team names for matching
    official_players_df = official_players_df.copy()
    player_priors_df = player_priors_df.copy()
    
    official_players_df["player_team_key"] = (
        official_players_df["player_name"].str.lower().str.strip() + "|" +
        official_players_df["team"].str.lower().str.strip()
    )
    
    player_priors_df["player_team_key"] = (
        player_priors_df["player"].str.lower().str.strip() + "|" +
        player_priors_df["team"].str.lower().str.strip()
    )
    
    # Left join: all official players, matching priors where found
    merged = official_players_df.merge(
        player_priors_df,
        on="player_team_key",
        how="left",
        indicator=True
    )
    
    # Separate matched and unmatched priors
    unmatched_priors = player_priors_df[
        ~player_priors_df["player_team_key"].isin(
            official_players_df["player_team_key"]
        )
    ].copy()
    
    # Fill conservative defaults for missing priors
    default_values = {
        "base_player_rating": 50,
        "expected_minutes_share": 0.50,
        "goals_prior": 0,
        "assists_prior": 0,
        "chance_creation_prior": 0,
        "defensive_actions_prior": 0,
        "goalkeeper_actions_prior": 0,
        "discipline_risk": 0.5,
        "star_role_score": 0,
        "flair_score": 0,
    }
    
    for col, default_val in default_values.items():
        merged[col] = merged[col].fillna(default_val)
    
    # Add has_player_prior flag
    merged["has_player_prior"] = merged["_merge"] == "both"
    merged["prior_source"] = merged.apply(
        lambda row: "user_prior" if row["has_player_prior"] else "conservative_default",
        axis=1
    )
    
    # Build official_award_candidates with required columns
    candidates = pd.DataFrame()
    candidates["player_id"] = merged["player_id"]
    candidates["team"] = merged["team_x"] if "team_x" in merged.columns else merged["team"]
    candidates["team_code"] = merged["team_code_x"] if "team_code_x" in merged.columns else merged.get("team_code", "")
    candidates["shirt_number"] = merged["shirt_number"]
    candidates["position_code"] = merged["position_code"]
    candidates["position"] = merged["position_x"] if "position_x" in merged.columns else merged["position"]
    candidates["player_name"] = merged["player_name"]
    candidates["date_of_birth"] = merged["date_of_birth"]
    candidates["age_at_tournament_start"] = merged["age_at_tournament_start"]
    candidates["club"] = merged["club"]
    candidates["height_cm"] = merged["height_cm"]
    candidates["base_player_rating"] = merged["base_player_rating"]
    candidates["expected_minutes_share"] = merged["expected_minutes_share"]
    candidates["goals_prior"] = merged["goals_prior"]
    candidates["assists_prior"] = merged["assists_prior"]
    candidates["chance_creation_prior"] = merged["chance_creation_prior"]
    candidates["defensive_actions_prior"] = merged["defensive_actions_prior"]
    candidates["goalkeeper_actions_prior"] = merged["goalkeeper_actions_prior"]
    candidates["discipline_risk"] = merged["discipline_risk"]
    candidates["star_role_score"] = merged["star_role_score"]
    candidates["flair_score"] = merged["flair_score"]
    candidates["has_player_prior"] = merged["has_player_prior"]
    candidates["prior_source"] = merged["prior_source"]
    candidates["source"] = merged["source_x"] if "source_x" in merged.columns else merged.get("source", "")
    candidates["last_verified_at"] = merged["last_verified_at_x"] if "last_verified_at_x" in merged.columns else merged.get("last_verified_at", "")
    
    # Create unmatched priors report
    unmatched_report = pd.DataFrame()
    unmatched_report["player"] = unmatched_priors["player"]
    unmatched_report["team"] = unmatched_priors["team"]
    unmatched_report["base_player_rating"] = unmatched_priors.get("base_player_rating", "")
    unmatched_report["source"] = "unmatched_prior"
    unmatched_report["notes"] = "Player not in official_players.csv - excluded from award candidates"
    
    return candidates, unmatched_report
