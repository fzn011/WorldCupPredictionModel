"""Official award data loaders for Step 18 (requires official_final mode)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C
from src.official.final_readiness import evaluate_official_final_readiness
from src.official.loaders import load_official_teams
from src.official.promotion import load_official_final_mode
from src.utils.team_name_mapping import standardize_team_name

PROJECT_ROOT = C.PROJECT_ROOT
PROCESSED_DATA_DIR = PROJECT_ROOT / C.PROCESSED_DATA_DIR
OFFICIAL_PROCESSED_DIR = PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR

PROGRESSION_COLUMNS: list[str] = [
    "round_of_32_probability",
    "round_of_16_probability",
    "quarter_final_probability",
    "semi_final_probability",
    "final_probability",
    "champion_probability",
]

OFFICIAL_FINAL_ERROR = (
    "World Cup awards require official_final mode. Run official final readiness and promotion first."
)


def require_official_final_ready() -> dict[str, Any]:
    """Require official_final_enabled and final readiness before awards generation."""
    mode = load_official_final_mode()
    if not mode.get("official_final_enabled", False):
        raise RuntimeError(OFFICIAL_FINAL_ERROR)

    readiness = evaluate_official_final_readiness()
    if not readiness.get("is_official_final_ready", False):
        raise RuntimeError(OFFICIAL_FINAL_ERROR)

    return {
        "official_final_enabled": True,
        "final_ready": True,
        "readiness_status": readiness.get("status"),
        "readiness_summary": readiness.get("summary", {}),
        "promoted_at": mode.get("promoted_at"),
    }


def normalize_official_award_candidates(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize official candidate schema for award scoring."""
    out = df.copy()
    if "player_name" in out.columns:
        out["player"] = out["player_name"].astype(str)
    elif "player" not in out.columns:
        out["player"] = ""

    out["team"] = out["team"].map(standardize_team_name)

    def _position_group(row: pd.Series) -> str:
        code = str(row.get("position_code", "")).strip().upper()
        pos = str(row.get("position", "")).strip().upper()
        if code in C.AWARD_POSITION_GROUPS:
            return C.AWARD_POSITION_GROUPS[code]
        if pos in C.AWARD_POSITION_GROUPS:
            return C.AWARD_POSITION_GROUPS[pos]
        pos_lower = str(row.get("position", "")).strip().lower()
        if pos_lower in C.PLAYER_POSITIONS:
            return pos_lower
        return "midfielder"

    out["position_group"] = out.apply(_position_group, axis=1)
    out["position"] = out["position_group"]
    if "age_at_tournament_start" in out.columns:
        out["age"] = pd.to_numeric(out["age_at_tournament_start"], errors="coerce")
    elif "age" not in out.columns:
        out["age"] = pd.NA
    return out


def load_official_award_candidates() -> pd.DataFrame:
    """Load official award candidates only (no sample fallback)."""
    require_official_final_ready()
    path = PROCESSED_DATA_DIR / C.OFFICIAL_AWARD_CANDIDATES_FILE
    if not path.is_file():
        raise FileNotFoundError(
            f"Official award candidates not found: {path}. Run: python scripts/prepare_official_squads.py"
        )
    df = pd.read_csv(path)
    missing = [c for c in C.OFFICIAL_AWARD_CANDIDATES_REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Official award candidates missing required columns: {missing}")
    return normalize_official_award_candidates(df)


def load_team_stage_probabilities(path: str | None = None) -> pd.DataFrame:
    """Load Monte Carlo team stage probabilities."""
    stage_path = Path(path) if path else PROCESSED_DATA_DIR / C.MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE
    if not stage_path.is_file():
        raise FileNotFoundError("Run python scripts/run_monte_carlo.py --simulations 10 --seed 42 first.")
    df = pd.read_csv(stage_path)
    if "team" in df.columns:
        df["team"] = df["team"].map(standardize_team_name)
    return df


def load_official_teams_for_awards() -> pd.DataFrame:
    """Load 48 official teams for team-level awards."""
    require_official_final_ready()
    teams_df = load_official_teams()
    if len(teams_df) < C.OFFICIAL_REQUIRED_TEAM_COUNT:
        raise ValueError(
            f"Expected {C.OFFICIAL_REQUIRED_TEAM_COUNT} official teams, found {len(teams_df)}"
        )
    teams_df = teams_df.copy()
    teams_df["team"] = teams_df["team"].map(standardize_team_name)
    return teams_df


def load_team_award_profiles() -> pd.DataFrame:
    """Load team award profiles or generate conservative defaults from official teams."""
    require_official_final_ready()
    profile_path = PROCESSED_DATA_DIR / C.TEAM_AWARD_PROFILES_FILE
    official_teams = load_official_teams_for_awards()
    official_set = set(official_teams["team"].astype(str))

    if profile_path.is_file():
        df = pd.read_csv(profile_path)
        df["team"] = df["team"].map(standardize_team_name)
        df = df[df["team"].isin(official_set)].copy()
        if not df.empty:
            return df

    rows = []
    for team in sorted(official_set):
        rows.append(
            {
                "team": team,
                "attacking_style_score": 50,
                "discipline_score": 50,
                "entertainment_score_prior": 50,
                "fan_popularity_proxy": 50,
                "source": "default_generated_from_official_teams",
            }
        )
    return pd.DataFrame(rows)


def calculate_team_progression_score(row: pd.Series) -> float:
    """Weighted team progression score from Monte Carlo probabilities."""
    score = 0.0
    weights = getattr(C, "AWARD_TEAM_PROGRESSION_WEIGHTS", C.TEAM_PROGRESSION_WEIGHTS)
    for col, weight in weights.items():
        score += float(pd.to_numeric(row.get(col, 0.0), errors="coerce") or 0.0) * float(weight)
    return score


def merge_players_with_team_progression(
    players_df: pd.DataFrame,
    team_stage_df: pd.DataFrame,
) -> pd.DataFrame:
    """Merge team progression probabilities into player table."""
    players = players_df.copy()
    players["team"] = players["team"].map(standardize_team_name)
    stages = team_stage_df.copy()
    stages["team"] = stages["team"].map(standardize_team_name)
    keep_cols = ["team", *[col for col in PROGRESSION_COLUMNS if col in stages.columns]]
    merged = players.merge(stages[keep_cols], on="team", how="left")
    for col in PROGRESSION_COLUMNS:
        if col not in merged.columns:
            merged[col] = 0.0
        merged[col] = pd.to_numeric(merged[col], errors="coerce").fillna(0.0)
    merged["has_team_progression_data"] = merged[PROGRESSION_COLUMNS].sum(axis=1) > 0
    merged["team_progression_score"] = merged.apply(calculate_team_progression_score, axis=1)
    return merged
