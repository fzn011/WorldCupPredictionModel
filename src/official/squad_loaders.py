"""Load official World Cup squad and player data.

Provides loaders for official players, squads, team-player maps, player priors,
and merged official award candidates. All loaders standardize team names and
return DataFrames in canonical form.
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path

from src.utils.constants import (
    PROJECT_ROOT,
    OFFICIAL_PROCESSED_DIR,
    PROCESSED_DATA_DIR,
    SAMPLE_DATA_DIR,
    OFFICIAL_PLAYERS_FILE,
    OFFICIAL_SQUADS_FILE,
    OFFICIAL_TEAM_PLAYER_MAP_FILE,
    PLAYER_AWARD_PRIORS_FILE,
    OFFICIAL_AWARD_CANDIDATES_FILE,
    SAMPLE_PLAYER_AWARD_PRIORS_FILE,
)
from src.utils.team_name_mapping import standardize_team_name


def load_official_players(path: str | None = None) -> pd.DataFrame:
    """Load official World Cup players.
    
    Args:
        path: Custom path to official_players.csv. Defaults to standard location.
        
    Returns:
        DataFrame with official player data.
        
    Raises:
        FileNotFoundError: If file does not exist.
    """
    if path is None:
        path = PROJECT_ROOT / OFFICIAL_PROCESSED_DIR / OFFICIAL_PLAYERS_FILE
    else:
        path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Official players file not found: {path}")
    
    df = pd.read_csv(path)
    
    # Standardize team names
    if "team" in df.columns:
        df["team"] = df["team"].apply(standardize_team_name)
    
    return df


def load_official_squads(path: str | None = None) -> pd.DataFrame:
    """Load official World Cup squads summary.
    
    Args:
        path: Custom path to official_squads.csv. Defaults to standard location.
        
    Returns:
        DataFrame with squad summaries by team.
        
    Raises:
        FileNotFoundError: If file does not exist.
    """
    if path is None:
        path = PROJECT_ROOT / OFFICIAL_PROCESSED_DIR / OFFICIAL_SQUADS_FILE
    else:
        path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Official squads file not found: {path}")
    
    df = pd.read_csv(path)
    
    # Standardize team names
    if "team" in df.columns:
        df["team"] = df["team"].apply(standardize_team_name)
    
    return df


def load_official_team_player_map(path: str | None = None) -> pd.DataFrame:
    """Load official team-to-player mappings.
    
    Args:
        path: Custom path to official_team_player_map.csv. Defaults to standard location.
        
    Returns:
        DataFrame with team-player relationships.
        
    Raises:
        FileNotFoundError: If file does not exist.
    """
    if path is None:
        path = PROJECT_ROOT / OFFICIAL_PROCESSED_DIR / OFFICIAL_TEAM_PLAYER_MAP_FILE
    else:
        path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Official team-player map not found: {path}")
    
    df = pd.read_csv(path)
    
    # Standardize team names
    if "team" in df.columns:
        df["team"] = df["team"].apply(standardize_team_name)
    
    return df


def load_player_award_priors(path: str | None = None) -> pd.DataFrame:
    """Load player award priors.
    
    Prefers data/processed/player_award_priors.csv (editable).
    Falls back to data/sample/sample_player_award_priors.csv if primary not found.
    
    Args:
        path: Custom path to priors CSV. Defaults to standard locations.
        
    Returns:
        DataFrame with player award priors.
        
    Raises:
        FileNotFoundError: If neither primary nor fallback exists.
    """
    if path is None:
        primary_path = PROJECT_ROOT / PROCESSED_DATA_DIR / PLAYER_AWARD_PRIORS_FILE
        fallback_path = PROJECT_ROOT / SAMPLE_DATA_DIR / SAMPLE_PLAYER_AWARD_PRIORS_FILE
        
        if primary_path.exists():
            path = primary_path
        elif fallback_path.exists():
            path = fallback_path
        else:
            raise FileNotFoundError(
                f"Neither primary ({primary_path}) nor fallback ({fallback_path}) priors found"
            )
    else:
        path = Path(path)
    
    df = pd.read_csv(path)
    
    # Standardize team names
    if "team" in df.columns:
        df["team"] = df["team"].apply(standardize_team_name)
    
    return df


def load_official_award_candidates(path: str | None = None) -> pd.DataFrame:
    """Load merged official award candidates (players + priors).
    
    Args:
        path: Custom path to official_award_candidates.csv. Defaults to standard location.
        
    Returns:
        DataFrame with official award candidates.
        
    Raises:
        FileNotFoundError: If file does not exist.
    """
    if path is None:
        path = PROJECT_ROOT / PROCESSED_DATA_DIR / OFFICIAL_AWARD_CANDIDATES_FILE
    else:
        path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Official award candidates not found: {path}")
    
    df = pd.read_csv(path)
    
    # Standardize team names
    if "team" in df.columns:
        df["team"] = df["team"].apply(standardize_team_name)
    
    return df


def get_official_player_list() -> list[str]:
    """Get sorted list of official player names.
    
    Returns:
        Sorted list of unique official player names.
    """
    df = load_official_players()
    players = sorted(df["player_name"].unique().tolist())
    return players


def is_official_player(player_name: str, team: str | None = None) -> bool:
    """Check if player is in official squad.
    
    Args:
        player_name: Player name to check.
        team: Optional team name. If provided, checks player/team pair.
        
    Returns:
        True if player is official, False otherwise.
    """
    try:
        df = load_official_players()
        
        if team is not None:
            team = standardize_team_name(team)
            match = df[(df["player_name"] == player_name) & (df["team"] == team)]
        else:
            match = df[df["player_name"] == player_name]
        
        return len(match) > 0
    except FileNotFoundError:
        return False
