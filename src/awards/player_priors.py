"""Create and manage player award priors templates.

Player award priors are editable benchmark values for each official player
that serve as starting points for award predictions. Conservative defaults
are used for players without explicit priors.
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path
from datetime import datetime

from src.utils.constants import (
    PROJECT_ROOT,
    PROCESSED_DATA_DIR,
    OFFICIAL_PLAYERS_REQUIRED_COLUMNS,
    PLAYER_PRIOR_REQUIRED_COLUMNS,
)


def create_player_award_priors_template(
    official_players_df: pd.DataFrame,
) -> pd.DataFrame:
    """Create editable player award priors template from official players.
    
    Creates one row per official player with conservative default values.
    This template is meant to be edited and saved for future use.
    
    Args:
        official_players_df: Official players DataFrame.
        
    Returns:
        DataFrame with PLAYER_PRIOR_REQUIRED_COLUMNS and conservative values.
    """
    template = pd.DataFrame()
    
    template["player"] = official_players_df["player_name"]
    template["team"] = official_players_df["team"]
    
    # Conservative defaults
    template["base_player_rating"] = 50
    template["expected_minutes_share"] = 0.50
    template["goals_prior"] = 0
    template["assists_prior"] = 0
    template["chance_creation_prior"] = 0
    template["defensive_actions_prior"] = 0
    template["goalkeeper_actions_prior"] = 0
    template["discipline_risk"] = 0.5
    template["star_role_score"] = 0
    template["flair_score"] = 0
    template["notes"] = "Edit these conservative defaults with expert knowledge"
    
    return template[PLAYER_PRIOR_REQUIRED_COLUMNS]


def save_player_award_priors_template(
    df: pd.DataFrame,
    output_path: str | None = None,
    overwrite: bool = False,
) -> str:
    """Save player award priors template.
    
    Args:
        df: Priors DataFrame.
        output_path: Custom path. Defaults to data/processed/player_award_priors.csv
        overwrite: If False, skip save if file exists. If True, overwrite.
        
    Returns:
        Path where file was saved (or would be saved).
        
    Raises:
        FileExistsError: If file exists and overwrite=False.
    """
    if output_path is None:
        output_path = PROJECT_ROOT / PROCESSED_DATA_DIR / "player_award_priors.csv"
    else:
        output_path = Path(output_path)
    
    # Create directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if output_path.exists() and not overwrite:
        raise FileExistsError(
            f"File already exists: {output_path}. Pass overwrite=True to replace."
        )
    
    df.to_csv(output_path, index=False)
    return str(output_path)
