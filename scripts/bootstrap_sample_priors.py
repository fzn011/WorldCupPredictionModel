"""Create sample player award priors from sample candidates."""

import pandas as pd
from pathlib import Path

# Load sample candidates
sample_path = Path("data/sample/sample_player_candidates.csv")
df = pd.read_csv(sample_path)

# Create priors template with required columns
priors = pd.DataFrame({
    "player": df["player"],
    "team": df["team"],
    "base_player_rating": df["base_player_rating"],
    "expected_minutes_share": df["expected_minutes_share"],
    "goals_prior": df["goals_prior"],
    "assists_prior": df["assists_prior"],
    "chance_creation_prior": df["chance_creation_prior"],
    "defensive_actions_prior": df["defensive_actions_prior"],
    "goalkeeper_actions_prior": df["goalkeeper_actions_prior"],
    "discipline_risk": df["discipline_risk"],
    "star_role_score": df["star_role_score"],
    "flair_score": df["flair_score"],
    "notes": "Sample prior - template for user to edit",
})

# Save to sample dir
output_path = Path("data/sample/sample_player_award_priors.csv")
priors.to_csv(output_path, index=False)
print(f"Created: {output_path}")
print(f"Rows: {len(priors)}")
