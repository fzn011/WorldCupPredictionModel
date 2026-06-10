"""Player-level World Cup awards analytics (Step 18)."""

from __future__ import annotations

from typing import Any

import pandas as pd

import src.utils.constants as C
from src.awards import award_data
from src.awards.award_data import (
    calculate_team_progression_score as _team_progression_score,
    ensure_player_identity_columns,
    load_official_award_candidates,
    merge_players_with_team_progression,
    normalize_official_award_candidates,
    require_official_final_ready,
)

PROGRESSION_COLUMNS: list[str] = [
    "round_of_32_probability",
    "round_of_16_probability",
    "quarter_final_probability",
    "semi_final_probability",
    "final_probability",
    "champion_probability",
]

DEFAULT_PRIORS: dict[str, float] = {
    "base_player_rating": 50.0,
    "expected_minutes_share": 0.5,
    "goals_prior": 0.0,
    "assists_prior": 0.0,
    "chance_creation_prior": 0.0,
    "defensive_actions_prior": 0.0,
    "goalkeeper_actions_prior": 0.0,
    "discipline_risk": 0.5,
    "star_role_score": 0.0,
    "flair_score": 0.0,
}


def ensure_numeric_award_columns(players_df: pd.DataFrame) -> pd.DataFrame:
    """Convert award numeric columns and fill conservative defaults."""
    out = players_df.copy()
    for col, default in DEFAULT_PRIORS.items():
        if col not in out.columns:
            out[col] = default
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(default)
    for col in PROGRESSION_COLUMNS:
        if col not in out.columns:
            out[col] = 0.0
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0.0)
    if "team_progression_score" not in out.columns:
        out["team_progression_score"] = out.apply(_team_progression_score, axis=1)
    return out


def calculate_expected_matches(row: pd.Series) -> float:
    """Expected matches from group stage baseline + progression probabilities."""
    return (
        3.0
        + float(row.get("round_of_32_probability", 0.0))
        + float(row.get("round_of_16_probability", 0.0))
        + float(row.get("quarter_final_probability", 0.0))
        + float(row.get("semi_final_probability", 0.0))
        + float(row.get("final_probability", 0.0))
    )


def _position_weights(row: pd.Series) -> dict[str, float]:
    group = str(row.get("position_group", row.get("position", "midfielder"))).strip().lower()
    return dict(C.AWARD_POSITION_WEIGHTS.get(group, C.AWARD_POSITION_WEIGHTS["midfielder"]))


def calculate_player_impact_components(players_df: pd.DataFrame) -> pd.DataFrame:
    """Add expected matches and impact components used by award formulas."""
    out = ensure_numeric_award_columns(ensure_player_identity_columns(players_df))
    out["expected_matches"] = out.apply(calculate_expected_matches, axis=1)

    attacking: list[float] = []
    creative: list[float] = []
    defensive: list[float] = []
    goalkeeper: list[float] = []
    star: list[float] = []
    progression: list[float] = []

    for _, row in out.iterrows():
        w = _position_weights(row)
        attacking.append(row["goals_prior"] * w["attacking"])
        creative.append(row["chance_creation_prior"] * w["creative"] + row["assists_prior"] * w["creative"] * 0.5)
        defensive.append(row["defensive_actions_prior"] * w["defensive"])
        goalkeeper.append(row["goalkeeper_actions_prior"] * w.get("golden_glove", 0.0))
        star.append(row["star_role_score"] + row["flair_score"] * 0.5)
        progression.append(row["team_progression_score"])

    out["attacking_component"] = attacking
    out["creative_component"] = creative
    out["defensive_component"] = defensive
    out["goalkeeper_component"] = goalkeeper
    out["star_component"] = star
    out["team_progression_component"] = progression
    return out


def _normalize_probability(scores: pd.Series) -> pd.Series:
    positive = scores.clip(lower=0.0)
    total = float(positive.sum())
    return positive / total if total > 0 else 0.0


def _player_sort_column(df: pd.DataFrame) -> str:
    """Return a stable player label column for tie-break sorting."""
    if "player_name" in df.columns:
        return "player_name"
    if "player" in df.columns:
        return "player"
    if "player_id" in df.columns:
        return "player_id"
    raise KeyError("Award candidates missing player_name, player, and player_id columns")


def calculate_golden_ball_predictions(players_df: pd.DataFrame) -> pd.DataFrame:
    """Estimate Golden/Silver/Bronze Ball rankings and probabilities."""
    out = calculate_player_impact_components(players_df)
    weights = out.apply(_position_weights, axis=1)
    pos_gb = weights.apply(lambda w: w["golden_ball"])

    out["golden_ball_score"] = (
        out["base_player_rating"] * pos_gb
        + out["attacking_component"]
        + out["creative_component"]
        + out["defensive_component"]
        + out["goalkeeper_component"]
        + out["star_component"]
        + out["team_progression_component"]
    )
    out["final_golden_ball_score"] = (out["golden_ball_score"] * out["expected_minutes_share"]).clip(lower=0.0)
    out["golden_ball_probability"] = _normalize_probability(out["final_golden_ball_score"])

    sort_name = _player_sort_column(out)
    out = out.sort_values(
        ["golden_ball_probability", "final_golden_ball_score", sort_name],
        ascending=[False, False, True],
    ).reset_index(drop=True)
    out["golden_ball_rank"] = range(1, len(out) + 1)
    podium = {1: "Golden Ball", 2: "Silver Ball", 3: "Bronze Ball"}
    out["award"] = out["golden_ball_rank"].map(lambda r: podium.get(int(r), ""))
    out["award_podium"] = out["award"]
    return out


def calculate_golden_boot_predictions(players_df: pd.DataFrame) -> pd.DataFrame:
    """Estimate Golden/Silver/Bronze Boot using expected-goals proxy."""
    out = calculate_player_impact_components(players_df)
    weights = out.apply(_position_weights, axis=1)
    boot_weight = weights.apply(lambda w: w["golden_boot"])

    out["expected_goals"] = (
        out["goals_prior"] * out["expected_matches"] * out["expected_minutes_share"] * boot_weight
    )
    out["boot_tiebreak_score"] = (
        out["expected_goals"] + out["assists_prior"] * 0.25 + out["expected_minutes_share"] * 0.10
    )
    out["expected_goals_score"] = out["expected_goals"]
    out["golden_boot_probability"] = _normalize_probability(out["boot_tiebreak_score"])

    sort_name = _player_sort_column(out)
    out = out.sort_values(["boot_tiebreak_score", "expected_goals", sort_name], ascending=[False, False, True]).reset_index(
        drop=True
    )
    out["golden_boot_rank"] = range(1, len(out) + 1)
    podium = {1: "Golden Boot", 2: "Silver Boot", 3: "Bronze Boot"}
    out["award"] = out["golden_boot_rank"].map(lambda r: podium.get(int(r), ""))
    out["boot_podium"] = out["award"]
    return out


def calculate_golden_glove_predictions(players_df: pd.DataFrame) -> pd.DataFrame:
    """Estimate Golden Glove among goalkeepers only."""
    out = players_df.copy()
    pos_code = out.get("position_code", pd.Series("", index=out.index)).astype(str).str.upper()
    pos_group = out.get("position_group", out.get("position", pd.Series("", index=out.index))).astype(str).str.lower()
    mask = (pos_code == "GK") | pos_group.eq("goalkeeper")
    out = out[mask].copy()
    out = ensure_numeric_award_columns(out)

    out["golden_glove_score"] = (
        out["base_player_rating"]
        + out["goalkeeper_actions_prior"] * 4.0
        + out["team_progression_score"] * 2.0
        + out["expected_minutes_share"] * 5.0
        + out["discipline_risk"]
    ).clip(lower=0.0)
    out["golden_glove_probability"] = _normalize_probability(out["golden_glove_score"])

    sort_name = _player_sort_column(out)
    out = out.sort_values(["golden_glove_score", sort_name], ascending=[False, True]).reset_index(drop=True)
    out["golden_glove_rank"] = range(1, len(out) + 1)
    out["award"] = out["golden_glove_rank"].map({1: "Golden Glove"}).fillna("")
    return out


def is_young_player_eligible(row: pd.Series) -> bool:
    """Young Player eligibility from DOB cutoff or age <= 21."""
    cutoff = pd.Timestamp(C.YOUNG_PLAYER_CUTOFF_DATE_2026)
    dob = pd.to_datetime(row.get("date_of_birth"), errors="coerce")
    age = pd.to_numeric(row.get("age_at_tournament_start", row.get("age")), errors="coerce")
    if pd.notna(dob) and dob >= cutoff:
        return True
    if pd.notna(age) and float(age) <= 21:
        return True
    return False


def filter_young_player_candidates(players_df: pd.DataFrame, tournament_year: int = 2026) -> pd.DataFrame:
    _ = tournament_year
    return players_df[players_df.apply(is_young_player_eligible, axis=1)].copy()


def calculate_young_player_predictions(players_df: pd.DataFrame) -> pd.DataFrame:
    """Estimate Young Player award probabilities among eligible players."""
    eligible = filter_young_player_candidates(players_df)
    if eligible.empty:
        return pd.DataFrame(columns=list(players_df.columns) + ["young_player_score", "young_player_probability", "young_player_rank", "award"])

    scored = calculate_golden_ball_predictions(eligible)
    scored["young_player_score"] = scored["final_golden_ball_score"]
    scored["young_player_probability"] = _normalize_probability(scored["young_player_score"])
    sort_name = "player_name" if "player_name" in scored.columns else "player"
    scored = scored.sort_values(["young_player_score", sort_name], ascending=[False, True]).reset_index(drop=True)
    scored["young_player_rank"] = range(1, len(scored) + 1)
    scored["award"] = scored["young_player_rank"].map({1: "Young Player Award"}).fillna("")
    return scored


def calculate_player_of_match_proxy(players_df: pd.DataFrame) -> pd.DataFrame:
    """Proxy POTM counts from team impact shares."""
    out = players_df.copy()
    if "final_golden_ball_score" not in out.columns:
        out = calculate_golden_ball_predictions(out)
    out = ensure_numeric_award_columns(out)
    out["expected_matches"] = out.apply(calculate_expected_matches, axis=1)
    team_totals = out.groupby("team")["final_golden_ball_score"].transform("sum").replace(0, 1.0)
    out["player_impact_share"] = out["final_golden_ball_score"] / team_totals
    out["player_impact_share_proxy"] = out["player_impact_share"]
    out["estimated_potm_count"] = out["expected_matches"] * out["player_impact_share"]
    sort_name = _player_sort_column(out)
    out = out.sort_values(["estimated_potm_count", sort_name], ascending=[False, True]).reset_index(drop=True)
    out["player_of_match_proxy_rank"] = range(1, len(out) + 1)
    return out


def calculate_goal_of_tournament_proxy(players_df: pd.DataFrame) -> pd.DataFrame:
    """Proxy goal-of-tournament score from attacking/flair priors."""
    out = players_df.copy()
    if "expected_goals" not in out.columns:
        out = calculate_golden_boot_predictions(out)
    out = ensure_numeric_award_columns(out)
    out["goal_of_tournament_proxy_score"] = (
        out["expected_goals"]
        + out["flair_score"] * 2.0
        + out["star_role_score"]
        + out["final_probability"] * 2.0
        + out["semi_final_probability"]
    ).clip(lower=0.0)
    out["goal_of_tournament_proxy_probability"] = _normalize_probability(out["goal_of_tournament_proxy_score"])
    sort_name = _player_sort_column(out)
    out = out.sort_values(["goal_of_tournament_proxy_score", sort_name], ascending=[False, True]).reset_index(drop=True)
    out["goal_of_tournament_proxy_rank"] = range(1, len(out) + 1)
    return out


def load_player_candidates(path: str | None = None, official_only: bool = True) -> pd.DataFrame:
    if official_only and path is None:
        require_official_final_ready()
        return load_official_award_candidates()
    if path is not None:
        return normalize_official_award_candidates(pd.read_csv(path))
    raise FileNotFoundError("Official award candidates required for awards generation.")


def load_team_stage_probabilities(path: str | None = None) -> pd.DataFrame:
    return award_data.load_team_stage_probabilities(path)


def add_team_progression_to_players(players_df: pd.DataFrame, team_stage_df: pd.DataFrame) -> pd.DataFrame:
    return merge_players_with_team_progression(players_df, team_stage_df)


def calculate_position_impact_score(row: pd.Series) -> float:
    w = _position_weights(row)
    return (
        float(row.get("goals_prior", 0)) * w["attacking"]
        + float(row.get("assists_prior", 0)) * w["creative"]
        + float(row.get("chance_creation_prior", 0)) * w["creative"]
        + float(row.get("defensive_actions_prior", 0)) * w["defensive"]
        + float(row.get("goalkeeper_actions_prior", 0)) * w.get("golden_glove", 0.0)
    )


def calculate_team_progression_score(row: pd.Series) -> float:
    return _team_progression_score(row)


def validate_player_candidates(df: pd.DataFrame) -> tuple[bool, pd.DataFrame]:
    checks: list[dict[str, Any]] = []
    required = ["player_name", "team", "position_code", "position"]
    missing = [c for c in required if c not in df.columns]
    checks.append({"check": "required_columns_present", "expected": "all", "actual": missing or "ok", "passed": not missing})
    if missing:
        return False, pd.DataFrame(checks)
    name_ok = df["player_name"].fillna("").astype(str).str.strip().ne("").all()
    team_ok = df["team"].fillna("").astype(str).str.strip().ne("").all()
    checks.append({"check": "player_name_not_empty", "expected": True, "actual": bool(name_ok), "passed": bool(name_ok)})
    checks.append({"check": "team_not_empty", "expected": True, "actual": bool(team_ok), "passed": bool(team_ok)})
    report = pd.DataFrame(checks)
    return bool(report["passed"].all()), report
