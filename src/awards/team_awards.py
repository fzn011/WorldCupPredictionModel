"""Team-level World Cup awards analytics utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C
from src.utils.team_name_mapping import standardize_team_name

PROJECT_ROOT = getattr(C, "PROJECT_ROOT", Path(__file__).resolve().parents[2])
DATA_DIR = getattr(C, "DATA_DIR", PROJECT_ROOT / "data")
PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", DATA_DIR / "processed")
SAMPLE_DATA_DIR = getattr(C, "SAMPLE_DATA_DIR", DATA_DIR / "sample")

TEAM_AWARD_PROFILES_FILE = getattr(C, "TEAM_AWARD_PROFILES_FILE", "team_award_profiles.csv")
SAMPLE_TEAM_AWARD_PROFILES_FILE = getattr(C, "SAMPLE_TEAM_AWARD_PROFILES_FILE", "sample_team_award_profiles.csv")

REQUIRED_TEAM_COLUMNS: list[str] = [
    "team",
    "attacking_style_score",
    "discipline_score",
    "entertainment_score_prior",
    "fan_popularity_proxy",
]
NUMERIC_TEAM_COLUMNS: list[str] = [
    "attacking_style_score",
    "discipline_score",
    "entertainment_score_prior",
    "fan_popularity_proxy",
]
PROGRESSION_COLUMNS: list[str] = [
    "round_of_32_probability",
    "round_of_16_probability",
    "quarter_final_probability",
    "semi_final_probability",
    "final_probability",
    "champion_probability",
]


def _ensure_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in columns:
        if col not in out.columns:
            out[col] = 0.0
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0.0)
    return out



def load_team_award_profiles(path: str | None = None) -> pd.DataFrame:
    """Load editable team-level award profiles from processed or sample storage."""
    if path is not None:
        profile_path = Path(path)
    else:
        processed_path = PROCESSED_DATA_DIR / TEAM_AWARD_PROFILES_FILE
        sample_path = SAMPLE_DATA_DIR / SAMPLE_TEAM_AWARD_PROFILES_FILE
        profile_path = processed_path if processed_path.is_file() else sample_path

    if not profile_path.is_file():
        raise FileNotFoundError(f"Team award profile file not found: {profile_path}")

    df = pd.read_csv(profile_path)
    if "team" in df.columns:
        df["team"] = df["team"].map(standardize_team_name)
    return df



def validate_team_award_profiles(df: pd.DataFrame) -> tuple[bool, pd.DataFrame]:
    """Validate team-award priors used for fair-play and entertainment estimates."""
    checks: list[dict[str, Any]] = []
    missing = [col for col in REQUIRED_TEAM_COLUMNS if col not in df.columns]
    checks.append({"check": "required_columns_present", "expected": "all required columns", "actual": ", ".join(missing) if missing else "ok", "passed": len(missing) == 0})
    if missing:
        return False, pd.DataFrame(checks)

    team_not_empty = df["team"].fillna("").astype(str).str.strip().ne("").all()
    checks.append({"check": "team_not_empty", "expected": "non-empty", "actual": bool(team_not_empty), "passed": bool(team_not_empty)})

    numeric_df = _ensure_numeric(df, NUMERIC_TEAM_COLUMNS)
    numeric_ok = not numeric_df[NUMERIC_TEAM_COLUMNS].isna().any().any()
    duplicates = int(df.assign(team=df["team"].map(standardize_team_name)).duplicated(subset=["team"]).sum())
    checks.append({"check": "numeric_columns_convertible", "expected": "all numeric columns convertible", "actual": bool(numeric_ok), "passed": bool(numeric_ok)})
    checks.append({"check": "duplicate_team_rows", "expected": "0", "actual": duplicates, "passed": duplicates == 0})

    report_df = pd.DataFrame(checks)
    return bool(report_df["passed"].all()), report_df



def add_team_stage_to_award_profiles(team_profiles_df: pd.DataFrame, team_stage_df: pd.DataFrame) -> pd.DataFrame:
    """Merge Monte Carlo progression probabilities into team-award profile table."""
    profiles = team_profiles_df.copy()
    profiles["team"] = profiles["team"].map(standardize_team_name)
    stages = team_stage_df.copy()
    stages["team"] = stages["team"].map(standardize_team_name)
    keep_cols = ["team", *[col for col in PROGRESSION_COLUMNS if col in stages.columns]]
    merged = profiles.merge(stages[keep_cols], on="team", how="left")
    merged = _ensure_numeric(merged, PROGRESSION_COLUMNS)
    merged["has_team_progression_data"] = merged[PROGRESSION_COLUMNS].sum(axis=1) > 0
    return merged



def calculate_fair_play_predictions(team_df: pd.DataFrame) -> pd.DataFrame:
    """Estimate Fair Play Trophy using team discipline priors and Round-of-32 qualification probability."""
    out = _ensure_numeric(team_df.copy(), NUMERIC_TEAM_COLUMNS + PROGRESSION_COLUMNS + ["discipline_risk", "discipline_risk_proxy"])
    risk_col = "discipline_risk" if "discipline_risk" in out.columns else "discipline_risk_proxy"
    risk = out[risk_col] if risk_col in out.columns else pd.Series(0.0, index=out.index)
    risk_max = float(risk.max()) if len(risk) else 0.0
    normalized_risk = risk / risk_max if risk_max > 0 else 0.0
    out["fair_play_score"] = (
        out["round_of_32_probability"] * out["discipline_score"] * (1 - 0.2 * normalized_risk)
    ).clip(lower=0.0)
    total = float(out["fair_play_score"].sum())
    out["fair_play_probability"] = out["fair_play_score"] / total if total > 0 else 0.0
    out = out.sort_values(["fair_play_score", "team"], ascending=[False, True]).reset_index(drop=True)
    out["fair_play_rank"] = range(1, len(out) + 1)
    out["award"] = out["fair_play_rank"].map({1: "Fair Play Trophy"}).fillna("")
    return out



def calculate_most_entertaining_team_predictions(team_df: pd.DataFrame, players_df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Estimate Most Entertaining Team using priors, star power, and progression depth."""
    out = _ensure_numeric(team_df.copy(), NUMERIC_TEAM_COLUMNS + PROGRESSION_COLUMNS)
    out["team_star_power"] = 0.0
    if players_df is not None and not players_df.empty and "team" in players_df.columns and "star_role_score" in players_df.columns:
        player_df = players_df.copy()
        player_df["team"] = player_df["team"].map(standardize_team_name)
        star_power = pd.to_numeric(player_df["star_role_score"], errors="coerce").fillna(0.0)
        star_df = pd.DataFrame({"team": player_df["team"], "star_role_score": star_power}).groupby("team", as_index=False).agg(team_star_power=("star_role_score", "sum"))
        out = out.merge(star_df, on="team", how="left", suffixes=("", "_from_players"))
        if "team_star_power_from_players" in out.columns:
            out["team_star_power"] = out["team_star_power_from_players"].fillna(0.0)
            out = out.drop(columns=["team_star_power_from_players"])
        else:
            out["team_star_power"] = out["team_star_power"].fillna(0.0)
    out["most_entertaining_score"] = (
        out["attacking_style_score"]
        + out["entertainment_score_prior"]
        + out["fan_popularity_proxy"]
        + out["team_star_power"]
        + out["semi_final_probability"] * 2.0
        + out["final_probability"] * 3.0
    ).clip(lower=0.0)
    total = float(out["most_entertaining_score"].sum())
    out["most_entertaining_probability"] = out["most_entertaining_score"] / total if total > 0 else 0.0
    out = out.sort_values(["most_entertaining_score", "team"], ascending=[False, True]).reset_index(drop=True)
    out["most_entertaining_rank"] = range(1, len(out) + 1)
    out["award"] = out["most_entertaining_rank"].map({1: "Most Entertaining Team"}).fillna("")
    return out
