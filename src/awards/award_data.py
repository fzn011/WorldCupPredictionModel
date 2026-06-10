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


def ensure_player_identity_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure player_name and player columns exist for sorting and reports."""
    out = df.copy()
    lower_map = {str(c).lower().replace(" ", "_"): c for c in out.columns}

    if "player_name" not in out.columns:
        for key in ("player", "name", "player_name"):
            if key in lower_map:
                out["player_name"] = out[lower_map[key]].astype(str)
                break

    if "player_name" not in out.columns and "player_id" in out.columns:
        out["player_name"] = out["player_id"].astype(str)

    if "player" not in out.columns:
        if "player_name" in out.columns:
            out["player"] = out["player_name"].astype(str)
        elif "player_id" in out.columns:
            out["player"] = out["player_id"].astype(str)
            if "player_name" not in out.columns:
                out["player_name"] = out["player"]
        else:
            out["player_name"] = ""
            out["player"] = ""
    elif "player_name" not in out.columns:
        out["player_name"] = out["player"].astype(str)

    return out


def normalize_official_award_candidates(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize official candidate schema for award scoring."""
    out = ensure_player_identity_columns(df.copy())

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


def load_official_award_candidates(
    *,
    use_enriched_candidates: bool | None = None,
) -> pd.DataFrame:
    """Load official award candidates only (no sample fallback).

    Uses enriched_official_award_candidates.csv when available and requested.
    """
    require_official_final_ready()
    enriched_path = PROCESSED_DATA_DIR / C.ENRICHED_OFFICIAL_AWARD_CANDIDATES_FILE
    base_path = PROCESSED_DATA_DIR / C.OFFICIAL_AWARD_CANDIDATES_FILE

    if use_enriched_candidates is None:
        use_enriched_candidates = enriched_path.is_file()

    if use_enriched_candidates and enriched_path.is_file():
        df = pd.read_csv(enriched_path)
        source = C.ENRICHED_OFFICIAL_AWARD_CANDIDATES_FILE
    else:
        if not base_path.is_file():
            raise FileNotFoundError(
                f"Official award candidates not found: {base_path}. Run: python scripts/prepare_official_squads.py"
            )
        df = pd.read_csv(base_path)
        source = C.OFFICIAL_AWARD_CANDIDATES_FILE

    missing = [c for c in C.OFFICIAL_AWARD_CANDIDATES_REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Official award candidates missing required columns: {missing}")

    normalized = normalize_official_award_candidates(df)
    normalized.attrs["candidate_source"] = source
    _validate_candidates_against_official_players(normalized)
    return normalized


def _validate_candidates_against_official_players(df: pd.DataFrame) -> None:
    """Ensure every candidate player_id exists in official_players.csv."""
    from src.official.loaders import load_official_players

    official_ids = set(load_official_players()["player_id"].astype(str))
    candidate_ids = set(df["player_id"].astype(str))
    unknown = candidate_ids - official_ids
    if unknown:
        raise ValueError(
            f"Award candidates contain {len(unknown)} player_id values outside official_players.csv"
        )


def get_award_candidate_source(use_enriched_candidates: bool | None = None) -> str:
    """Return which candidate file would be used for awards generation."""
    enriched_path = PROCESSED_DATA_DIR / C.ENRICHED_OFFICIAL_AWARD_CANDIDATES_FILE
    if use_enriched_candidates is None:
        use_enriched_candidates = enriched_path.is_file()
    if use_enriched_candidates and enriched_path.is_file():
        return C.ENRICHED_OFFICIAL_AWARD_CANDIDATES_FILE
    return C.OFFICIAL_AWARD_CANDIDATES_FILE


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
