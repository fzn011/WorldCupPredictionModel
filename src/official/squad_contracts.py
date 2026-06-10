"""Official squad and player data contracts.

Defines the required structure for official World Cup squad data, player priors,
and award candidates to ensure data integrity and consistency across the codebase.
"""

from __future__ import annotations

from src.utils.constants import (
    OFFICIAL_PLAYERS_REQUIRED_COLUMNS,
    OFFICIAL_AWARD_CANDIDATES_REQUIRED_COLUMNS,
    PLAYER_PRIOR_REQUIRED_COLUMNS,
)


def get_squad_contract(name: str) -> list[str]:
    """Retrieve required columns for a squad/player data contract.
    
    Args:
        name: Contract name ('official_players', 'official_award_candidates', 'player_priors', etc.)
        
    Returns:
        List of required column names.
        
    Raises:
        ValueError: If contract name is unknown.
    """
    contracts = {
        "official_players": OFFICIAL_PLAYERS_REQUIRED_COLUMNS,
        "official_award_candidates": OFFICIAL_AWARD_CANDIDATES_REQUIRED_COLUMNS,
        "player_priors": PLAYER_PRIOR_REQUIRED_COLUMNS,
    }
    
    if name not in contracts:
        raise ValueError(
            f"Unknown contract '{name}'. Available: {list(contracts.keys())}"
        )
    
    return contracts[name]


def check_squad_required_columns(
    df,
    required_columns: list[str],
    dataset_name: str = "dataset",
) -> tuple[bool, list[str]]:
    """Check if a DataFrame has all required columns.
    
    Args:
        df: DataFrame to check.
        required_columns: List of required column names.
        dataset_name: Name of dataset for error reporting.
        
    Returns:
        (bool, list[str]): (all_present, missing_columns)
    """
    df_columns = set(df.columns)
    required_set = set(required_columns)
    missing = sorted(required_set - df_columns)
    
    return len(missing) == 0, missing
