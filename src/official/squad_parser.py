"""Parse and prepare official World Cup squad data.

Converts sample player candidates to official player format, handles position
normalization, calculates ages, and generates templates for manual squad entry.
"""

from __future__ import annotations

import pandas as pd
from datetime import datetime
import hashlib

from src.utils.constants import (
    OFFICIAL_POSITION_CODES,
    OFFICIAL_POSITION_MAP,
    OFFICIAL_PLAYERS_REQUIRED_COLUMNS,
)


def normalize_position_code(position_code_or_position: str) -> tuple[str, str]:
    """Normalize position to standardized code and name.
    
    Args:
        position_code_or_position: Either position code (GK, DF, MF, FW) 
                                  or position name (goalkeeper, defender, etc.)
        
    Returns:
        (position_code, position_name) tuple.
        
    Raises:
        ValueError: If position is not recognized.
    """
    input_str = position_code_or_position.strip().upper()
    
    # Check if it's already a code
    if input_str in OFFICIAL_POSITION_CODES:
        code = input_str
        position = OFFICIAL_POSITION_MAP[code]
        return code, position
    
    # Check if it's a position name
    position_lower = position_code_or_position.strip().lower()
    for code, position in OFFICIAL_POSITION_MAP.items():
        if position == position_lower:
            return code, position
    
    # Handle variations
    if position_lower == "forward":
        return "FW", "forward"
    elif position_lower == "midfielder":
        return "MF", "midfielder"
    elif position_lower == "defender":
        return "DF", "defender"
    elif position_lower == "goalkeeper":
        return "GK", "goalkeeper"
    
    raise ValueError(f"Unknown position: {position_code_or_position}")


def calculate_age_at_tournament_start(
    date_of_birth: str,
    tournament_start_date: str = "2026-06-11"
) -> int | None:
    """Calculate player age at tournament start.
    
    Args:
        date_of_birth: Date string (YYYY-MM-DD format).
        tournament_start_date: Tournament start date (default June 11, 2026).
        
    Returns:
        Age as integer, or None if date cannot be parsed.
    """
    try:
        dob = datetime.strptime(str(date_of_birth).strip(), "%Y-%m-%d")
        tournament_date = datetime.strptime(tournament_start_date, "%Y-%m-%d")
        age = (
            tournament_date.year - dob.year - 
            ((tournament_date.month, tournament_date.day) < (dob.month, dob.day))
        )
        return max(0, age)  # Ensure non-negative
    except (ValueError, TypeError):
        return None


def parse_official_squad_csv(path: str) -> pd.DataFrame:
    """Parse manually prepared official squad CSV.
    
    Expected columns (flexible, will be normalized):
    - team, team_code, shirt_number, position_code, player_name, 
      first_names, last_names, name_on_shirt, date_of_birth, club, height_cm
    
    Args:
        path: Path to manually prepared squad CSV.
        
    Returns:
        DataFrame normalized to OFFICIAL_PLAYERS_REQUIRED_COLUMNS.
        
    Raises:
        FileNotFoundError: If file not found.
        ValueError: If required columns missing.
    """
    import os
    if not os.path.exists(path):
        raise FileNotFoundError(f"Squad CSV not found: {path}")
    
    df = pd.read_csv(path)
    
    # Normalize columns to lowercase
    df.columns = [c.lower().strip() for c in df.columns]
    
    # Ensure minimum required columns present
    required = {"team", "player_name"}
    if not required.issubset(set(df.columns)):
        raise ValueError(
            f"Squad CSV must include at least: {required}. Found: {set(df.columns)}"
        )
    
    # Create standardized output
    result = pd.DataFrame()
    
    # Copy or create player_id
    if "player_id" in df.columns:
        result["player_id"] = df["player_id"]
    else:
        # Generate deterministic player_id from player_name + team
        result["player_id"] = (
            df["player_name"].astype(str) + "_" + 
            df.get("team", "unknown").astype(str)
        ).apply(lambda x: hashlib.md5(x.encode()).hexdigest()[:16])
    
    result["team"] = df.get("team", "")
    result["team_code"] = df.get("team_code", "")
    result["shirt_number"] = pd.to_numeric(df.get("shirt_number", 0), errors="coerce").fillna(0).astype(int)
    
    # Handle position
    if "position_code" in df.columns and "position" in df.columns:
        result["position_code"] = df["position_code"]
        result["position"] = df["position"]
    elif "position_code" in df.columns:
        result["position_code"] = df["position_code"]
        result["position"] = result["position_code"].apply(
            lambda x: OFFICIAL_POSITION_MAP.get(x.upper(), "unknown") if pd.notna(x) else "unknown"
        )
    elif "position" in df.columns:
        result[["position_code", "position"]] = df["position"].apply(
            lambda x: pd.Series(normalize_position_code(str(x)))
        )
    else:
        result["position_code"] = "GK"
        result["position"] = "goalkeeper"
    
    result["player_name"] = df["player_name"]
    result["first_names"] = df.get("first_names", "")
    result["last_names"] = df.get("last_names", "")
    result["name_on_shirt"] = df.get("name_on_shirt", df.get("player_name", ""))
    result["date_of_birth"] = df.get("date_of_birth", "")
    
    # Calculate age
    result["age_at_tournament_start"] = result["date_of_birth"].apply(
        calculate_age_at_tournament_start
    )
    
    result["club"] = df.get("club", "")
    result["club_country"] = df.get("club_country", "")
    result["height_cm"] = pd.to_numeric(df.get("height_cm", 0), errors="coerce").fillna(0).astype(int)
    result["source"] = "manual_input"
    result["last_verified_at"] = datetime.now().strftime("%Y-%m-%d")
    
    return result[OFFICIAL_PLAYERS_REQUIRED_COLUMNS]


def create_official_players_template_from_sample(
    sample_players_df: pd.DataFrame,
    official_teams_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Create official players template from sample player candidates.
    
    Converts sample format to official format. Use only for template generation
    when official squad data not yet available.
    
    Args:
        sample_players_df: DataFrame with sample player candidates.
        official_teams_df: Optional official teams for validation.
        
    Returns:
        DataFrame in official_players format with source='sample_to_be_verified'.
    """
    result = pd.DataFrame()
    
    # Generate stable player_id
    result["player_id"] = (
        sample_players_df["player"].astype(str) + "_" + 
        sample_players_df["team"].astype(str)
    ).apply(lambda x: hashlib.md5(x.encode()).hexdigest()[:16])
    
    result["team"] = sample_players_df["team"]
    result["team_code"] = sample_players_df["team"].str[:3].str.upper()
    result["shirt_number"] = 0  # Not available in sample
    
    # Normalize position
    position_norm = sample_players_df["position"].apply(normalize_position_code)
    result["position_code"] = position_norm.apply(lambda x: x[0])
    result["position"] = position_norm.apply(lambda x: x[1])
    
    result["player_name"] = sample_players_df["player"]
    result["first_names"] = ""
    result["last_names"] = ""
    result["name_on_shirt"] = sample_players_df["player"]
    result["date_of_birth"] = sample_players_df.get("date_of_birth", "")
    
    # Calculate age
    result["age_at_tournament_start"] = result["date_of_birth"].apply(
        calculate_age_at_tournament_start
    )
    
    result["club"] = sample_players_df.get("club", "")
    result["club_country"] = ""
    result["height_cm"] = 0
    result["source"] = "sample_to_be_verified"
    result["last_verified_at"] = datetime.now().strftime("%Y-%m-%d")
    
    return result[OFFICIAL_PLAYERS_REQUIRED_COLUMNS]
