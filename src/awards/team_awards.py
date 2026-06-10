"""Team-level World Cup awards analytics (Step 18)."""

from __future__ import annotations

from typing import Any

import pandas as pd

import src.utils.constants as C
from src.awards.award_data import load_official_teams_for_awards
from src.awards import award_data
from src.utils.team_name_mapping import standardize_team_name

PROGRESSION_COLUMNS: list[str] = [
    "round_of_32_probability",
    "round_of_16_probability",
    "quarter_final_probability",
    "semi_final_probability",
    "final_probability",
    "champion_probability",
]

NUMERIC_TEAM_COLUMNS: list[str] = [
    "attacking_style_score",
    "discipline_score",
    "entertainment_score_prior",
    "fan_popularity_proxy",
]


def _ensure_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in columns:
        if col not in out.columns:
            out[col] = 50.0
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(50.0)
    for col in PROGRESSION_COLUMNS:
        if col not in out.columns:
            out[col] = 0.0
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0.0)
    return out


def prepare_team_award_data(
    team_profiles_df: pd.DataFrame,
    team_stage_df: pd.DataFrame,
    players_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Merge official teams, profiles, stage probabilities, and player star power."""
    official_teams = load_official_teams_for_awards()
    official_set = set(official_teams["team"].astype(str))

    profiles = team_profiles_df.copy()
    profiles["team"] = profiles["team"].map(standardize_team_name)
    profiles = profiles[profiles["team"].isin(official_set)]

    stages = team_stage_df.copy()
    stages["team"] = stages["team"].map(standardize_team_name)
    keep_cols = ["team", *[c for c in PROGRESSION_COLUMNS if c in stages.columns]]
    merged = profiles.merge(stages[keep_cols], on="team", how="left")
    merged = _ensure_numeric(merged, NUMERIC_TEAM_COLUMNS + PROGRESSION_COLUMNS)

    merged["team_star_power"] = 0.0
    if players_df is not None and not players_df.empty:
        pdf = players_df.copy()
        pdf["team"] = pdf["team"].map(standardize_team_name)
        high_minutes = pdf[pd.to_numeric(pdf.get("expected_minutes_share", 0.5), errors="coerce").fillna(0.5) >= 0.4]
        star_df = (
            high_minutes.groupby("team", as_index=False)
            .agg(team_star_power=("star_role_score", "mean"))
        )
        merged = merged.merge(star_df, on="team", how="left", suffixes=("", "_from_players"))
        if "team_star_power_from_players" in merged.columns:
            merged["team_star_power"] = merged["team_star_power_from_players"].fillna(0.0)
            merged = merged.drop(columns=["team_star_power_from_players"])
        merged["team_star_power"] = merged["team_star_power"].fillna(0.0)

    if players_df is not None and "discipline_risk" in players_df.columns:
        discipline = (
            players_df.assign(team=players_df["team"].map(standardize_team_name))
            .groupby("team", as_index=False)
            .agg(average_discipline_risk=("discipline_risk", "mean"))
        )
        merged = merged.merge(discipline, on="team", how="left")
    else:
        merged["average_discipline_risk"] = 0.5

    merged["average_discipline_risk"] = pd.to_numeric(merged["average_discipline_risk"], errors="coerce").fillna(0.5)
    merged["has_team_progression_data"] = merged[PROGRESSION_COLUMNS].sum(axis=1) > 0
    return merged


def validate_team_award_profiles(df: pd.DataFrame) -> tuple[bool, pd.DataFrame]:
    checks: list[dict[str, Any]] = []
    missing = [c for c in ["team", *NUMERIC_TEAM_COLUMNS] if c not in df.columns]
    checks.append({"check": "required_columns_present", "expected": "all", "actual": missing or "ok", "passed": not missing})
    if missing:
        return False, pd.DataFrame(checks)
    team_ok = df["team"].fillna("").astype(str).str.strip().ne("").all()
    checks.append({"check": "team_not_empty", "expected": True, "actual": bool(team_ok), "passed": bool(team_ok)})
    report = pd.DataFrame(checks)
    return bool(report["passed"].all()), report


def add_team_stage_to_award_profiles(team_profiles_df: pd.DataFrame, team_stage_df: pd.DataFrame) -> pd.DataFrame:
    return prepare_team_award_data(team_profiles_df, team_stage_df, players_df=None)


def calculate_fair_play_predictions(team_df: pd.DataFrame) -> pd.DataFrame:
    """Estimate Fair Play Trophy using discipline and progression eligibility."""
    out = _ensure_numeric(team_df.copy(), NUMERIC_TEAM_COLUMNS + PROGRESSION_COLUMNS)
    eligible = out["round_of_32_probability"] > 0
    out = out[eligible].copy() if eligible.any() else out.copy()

    out["fair_play_score"] = (
        out["discipline_score"]
        + out["round_of_32_probability"] * 10.0
        + out["round_of_16_probability"] * 5.0
        - out.get("average_discipline_risk", 0.5) * 5.0
    ).clip(lower=0.0)

    total = float(out["fair_play_score"].sum())
    out["fair_play_probability"] = out["fair_play_score"] / total if total > 0 else 0.0
    out = out.sort_values(["fair_play_score", "team"], ascending=[False, True]).reset_index(drop=True)
    out["fair_play_rank"] = range(1, len(out) + 1)
    out["award"] = out["fair_play_rank"].map({1: "Fair Play Trophy"}).fillna("")
    return out


def calculate_most_entertaining_team_predictions(
    team_df: pd.DataFrame,
    players_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Estimate Most Entertaining Team."""
    out = _ensure_numeric(team_df.copy(), NUMERIC_TEAM_COLUMNS + PROGRESSION_COLUMNS)
    if players_df is not None and not players_df.empty:
        pdf = players_df.copy()
        pdf["team"] = pdf["team"].map(standardize_team_name)
        star_df = pdf.groupby("team", as_index=False).agg(team_star_power=("star_role_score", "sum"))
        out = out.merge(star_df, on="team", how="left")
    if "team_star_power" not in out.columns:
        out["team_star_power"] = 0.0
    out["team_star_power"] = pd.to_numeric(out["team_star_power"], errors="coerce").fillna(0.0)

    out["most_entertaining_score"] = (
        out["attacking_style_score"]
        + out["entertainment_score_prior"]
        + out["fan_popularity_proxy"]
        + out["team_star_power"]
        + out["semi_final_probability"] * 10.0
        + out["final_probability"] * 15.0
        + out["champion_probability"] * 20.0
    ).clip(lower=0.0)

    total = float(out["most_entertaining_score"].sum())
    out["most_entertaining_probability"] = out["most_entertaining_score"] / total if total > 0 else 0.0
    out = out.sort_values(["most_entertaining_score", "team"], ascending=[False, True]).reset_index(drop=True)
    out["most_entertaining_rank"] = range(1, len(out) + 1)
    out["award"] = out["most_entertaining_rank"].map({1: "Most Entertaining Team"}).fillna("")
    return out


def load_team_award_profiles(path: str | None = None) -> pd.DataFrame:
    if path is not None:
        df = pd.read_csv(path)
        df["team"] = df["team"].map(standardize_team_name)
        return df
    return award_data.load_team_award_profiles()
