"""Player-level World Cup awards analytics utilities."""

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

PLAYER_CANDIDATES_FILE = getattr(C, "PLAYER_CANDIDATES_FILE", "player_candidates.csv")
SAMPLE_PLAYER_CANDIDATES_FILE = getattr(C, "SAMPLE_PLAYER_CANDIDATES_FILE", "sample_player_candidates.csv")
MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE = getattr(
    C,
    "MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE",
    "monte_carlo_team_stage_probabilities.csv",
)
PLAYER_POSITIONS = list(getattr(C, "PLAYER_POSITIONS", ["forward", "midfielder", "defender", "goalkeeper"]))
POSITION_WEIGHTS = dict(getattr(C, "POSITION_WEIGHTS", {}))
TEAM_PROGRESSION_WEIGHTS = dict(getattr(C, "TEAM_PROGRESSION_WEIGHTS", {}))
YOUNG_PLAYER_CUTOFF_DATE_2026 = str(getattr(C, "YOUNG_PLAYER_CUTOFF_DATE_2026", "2005-01-01"))

REQUIRED_PLAYER_COLUMNS: list[str] = [
    "player",
    "team",
    "position",
    "age",
    "date_of_birth",
    "base_player_rating",
    "expected_minutes_share",
    "goals_prior",
    "assists_prior",
    "chance_creation_prior",
    "defensive_actions_prior",
    "goalkeeper_actions_prior",
    "discipline_risk",
    "star_role_score",
    "flair_score",
]

NUMERIC_PLAYER_COLUMNS: list[str] = [
    "age",
    "base_player_rating",
    "expected_minutes_share",
    "goals_prior",
    "assists_prior",
    "chance_creation_prior",
    "defensive_actions_prior",
    "goalkeeper_actions_prior",
    "discipline_risk",
    "star_role_score",
    "flair_score",
]

PROGRESSION_COLUMNS: list[str] = [
    "round_of_32_probability",
    "round_of_16_probability",
    "quarter_final_probability",
    "semi_final_probability",
    "final_probability",
    "champion_probability",
]

POSITION_GOAL_FACTORS: dict[str, float] = {
    "forward": 1.2,
    "midfielder": 0.8,
    "defender": 0.35,
    "goalkeeper": 0.02,
}


def _ensure_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in columns:
        if col not in out.columns:
            out[col] = 0.0
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0.0)
    return out



def _expected_matches(df: pd.DataFrame) -> pd.Series:
    out = df.copy()
    for col in PROGRESSION_COLUMNS[:-1]:
        if col not in out.columns:
            out[col] = 0.0
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0.0)
    return (
        3.0
        + out["round_of_32_probability"]
        + out["round_of_16_probability"]
        + out["quarter_final_probability"]
        + out["semi_final_probability"]
        + out["final_probability"]
    )



def load_player_candidates(path: str | None = None, official_only: bool = True) -> pd.DataFrame:
    """Load player-candidate priors from processed or sample storage.
    
    In official mode (official_only=True), prefers official_award_candidates.csv
    which contains only official World Cup squad players.
    
    Args:
        path: Custom path to candidates file.
        official_only: If True, require official candidates. If False, allow sample.
        
    Returns:
        Player candidates DataFrame.
        
    Raises:
        FileNotFoundError: If official_award_candidates not found and official_only=True.
    """
    if path is not None:
        candidate_path = Path(path)
    else:
        if official_only:
            # Require official award candidates
            official_path = PROCESSED_DATA_DIR / getattr(C, "OFFICIAL_AWARD_CANDIDATES_FILE", "official_award_candidates.csv")
            if not official_path.is_file():
                raise FileNotFoundError(
                    f"Official award candidates not found: {official_path}. "
                    f"Run: python scripts/prepare_official_squads.py"
                )
            candidate_path = official_path
        else:
            # Fallback to sample if official not available
            processed_path = PROCESSED_DATA_DIR / PLAYER_CANDIDATES_FILE
            official_path = PROCESSED_DATA_DIR / getattr(C, "OFFICIAL_AWARD_CANDIDATES_FILE", "official_award_candidates.csv")
            sample_path = SAMPLE_DATA_DIR / SAMPLE_PLAYER_CANDIDATES_FILE
            
            if official_path.is_file():
                candidate_path = official_path
            elif processed_path.is_file():
                candidate_path = processed_path
            else:
                candidate_path = sample_path

    if not candidate_path.is_file():
        raise FileNotFoundError(f"Player candidate file not found: {candidate_path}")

    df = pd.read_csv(candidate_path)
    if "team" in df.columns:
        df["team"] = df["team"].map(standardize_team_name)
    return df



def validate_player_candidates(df: pd.DataFrame) -> tuple[bool, pd.DataFrame]:
    """Validate player candidate priors for award estimation."""
    checks: list[dict[str, Any]] = []
    missing = [col for col in REQUIRED_PLAYER_COLUMNS if col not in df.columns]
    checks.append(
        {
            "check": "required_columns_present",
            "expected": "all required columns",
            "actual": ", ".join(missing) if missing else "ok",
            "passed": len(missing) == 0,
        }
    )
    if missing:
        return False, pd.DataFrame(checks)

    player_not_empty = df["player"].fillna("").astype(str).str.strip().ne("").all()
    team_not_empty = df["team"].fillna("").astype(str).str.strip().ne("").all()
    checks.append({"check": "player_not_empty", "expected": "non-empty", "actual": bool(player_not_empty), "passed": bool(player_not_empty)})
    checks.append({"check": "team_not_empty", "expected": "non-empty", "actual": bool(team_not_empty), "passed": bool(team_not_empty)})

    positions = df["position"].fillna("").astype(str).str.strip().str.lower()
    invalid_positions = sorted(set(positions[~positions.isin(PLAYER_POSITIONS)].tolist()))
    checks.append(
        {
            "check": "position_allowed",
            "expected": f"subset of {PLAYER_POSITIONS}",
            "actual": ", ".join(invalid_positions) if invalid_positions else "ok",
            "passed": len(invalid_positions) == 0,
        }
    )

    numeric_df = _ensure_numeric(df, NUMERIC_PLAYER_COLUMNS)
    numeric_ok = not numeric_df[NUMERIC_PLAYER_COLUMNS].isna().any().any()
    checks.append(
        {
            "check": "numeric_columns_convertible",
            "expected": "all numeric columns convertible",
            "actual": bool(numeric_ok),
            "passed": bool(numeric_ok),
        }
    )

    minutes_ok = numeric_df["expected_minutes_share"].between(0.0, 1.0, inclusive="both").all()
    base_ok = (numeric_df["base_player_rating"] >= 0).all()
    age_ok = (numeric_df["age"] >= 0).all()
    duplicate_count = int(df.assign(team=df["team"].map(standardize_team_name)).duplicated(subset=["player", "team"]).sum())

    checks.append({"check": "expected_minutes_share_range", "expected": "0<=x<=1", "actual": bool(minutes_ok), "passed": bool(minutes_ok)})
    checks.append({"check": "base_player_rating_non_negative", "expected": ">=0", "actual": bool(base_ok), "passed": bool(base_ok)})
    checks.append({"check": "age_non_negative", "expected": ">=0", "actual": bool(age_ok), "passed": bool(age_ok)})
    checks.append({"check": "duplicate_player_team_rows", "expected": "0", "actual": duplicate_count, "passed": duplicate_count == 0})

    report_df = pd.DataFrame(checks)
    return bool(report_df["passed"].all()), report_df



def load_team_stage_probabilities(path: str | None = None) -> pd.DataFrame:
    """Load Monte Carlo stage probabilities for team-level award influence."""
    stage_path = Path(path) if path else PROCESSED_DATA_DIR / MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE
    if not stage_path.is_file():
        raise FileNotFoundError("Run python scripts/run_monte_carlo.py --simulations 10 --seed 42 first.")
    df = pd.read_csv(stage_path)
    if "team" in df.columns:
        df["team"] = df["team"].map(standardize_team_name)
    return df



def calculate_position_impact_score(row: pd.Series) -> float:
    """Calculate position-adjusted player contribution score from editable priors."""
    position = str(row.get("position", "")).strip().lower()
    weights = POSITION_WEIGHTS.get(position, POSITION_WEIGHTS.get("midfielder", {}))
    goals = float(pd.to_numeric(row.get("goals_prior", 0.0), errors="coerce") or 0.0)
    assists = float(pd.to_numeric(row.get("assists_prior", 0.0), errors="coerce") or 0.0)
    chance_creation = float(pd.to_numeric(row.get("chance_creation_prior", 0.0), errors="coerce") or 0.0)
    defensive_actions = float(pd.to_numeric(row.get("defensive_actions_prior", 0.0), errors="coerce") or 0.0)
    goalkeeper_actions = float(pd.to_numeric(row.get("goalkeeper_actions_prior", 0.0), errors="coerce") or 0.0)
    return (
        goals * float(weights.get("goals", 0.0))
        + assists * float(weights.get("assists", 0.0))
        + chance_creation * float(weights.get("chance_creation", 0.0))
        + defensive_actions * float(weights.get("defensive_actions", 0.0))
        + goalkeeper_actions * float(weights.get("goalkeeper_actions", 0.0))
    )



def calculate_team_progression_score(team_row: pd.Series) -> float:
    """Calculate weighted team progression influence."""
    score = 0.0
    for col, weight in TEAM_PROGRESSION_WEIGHTS.items():
        score += float(pd.to_numeric(team_row.get(col, 0.0), errors="coerce") or 0.0) * float(weight)
    return score



def add_team_progression_to_players(players_df: pd.DataFrame, team_stage_df: pd.DataFrame) -> pd.DataFrame:
    """Merge Monte Carlo progression probabilities into player prior table."""
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



def calculate_golden_ball_predictions(players_df: pd.DataFrame) -> pd.DataFrame:
    """Estimate Golden/Silver/Bronze Ball rankings and probabilities."""
    out = _ensure_numeric(players_df.copy(), NUMERIC_PLAYER_COLUMNS + PROGRESSION_COLUMNS + ["team_progression_score"])
    out["position"] = out.get("position", "midfielder").astype(str).str.strip().str.lower()
    out["position_impact_score"] = out.apply(calculate_position_impact_score, axis=1)
    out["raw_golden_ball_score"] = (
        out["base_player_rating"]
        + out["position_impact_score"]
        + out["star_role_score"]
        + out["team_progression_score"]
    )
    out["final_golden_ball_score"] = (out["raw_golden_ball_score"] * out["expected_minutes_share"]).clip(lower=0.0)
    total = float(out["final_golden_ball_score"].sum())
    out["golden_ball_probability"] = out["final_golden_ball_score"] / total if total > 0 else 0.0
    out = out.sort_values(["golden_ball_probability", "final_golden_ball_score", "player"], ascending=[False, False, True]).reset_index(drop=True)
    out["golden_ball_rank"] = range(1, len(out) + 1)
    out["award_podium"] = out["golden_ball_rank"].map({1: "Golden Ball", 2: "Silver Ball", 3: "Bronze Ball"}).fillna("")
    return out



def calculate_golden_boot_predictions(players_df: pd.DataFrame) -> pd.DataFrame:
    """Estimate Golden/Silver/Bronze Boot using expected-goal proxy scoring."""
    out = _ensure_numeric(players_df.copy(), NUMERIC_PLAYER_COLUMNS + PROGRESSION_COLUMNS)
    out["position"] = out.get("position", "midfielder").astype(str).str.strip().str.lower()
    out["expected_matches"] = _expected_matches(out)
    out["position_goal_factor"] = out["position"].map(POSITION_GOAL_FACTORS).fillna(0.8)
    out["expected_goals_score"] = (
        out["goals_prior"]
        * out["expected_minutes_share"]
        * out["expected_matches"]
        * out["position_goal_factor"]
    )
    out["golden_boot_tiebreak_score"] = out["expected_goals_score"] + out["assists_prior"] * 0.05 + out["chance_creation_prior"] * 0.02
    total = float(out["golden_boot_tiebreak_score"].clip(lower=0.0).sum())
    out["golden_boot_probability"] = out["golden_boot_tiebreak_score"].clip(lower=0.0) / total if total > 0 else 0.0
    out = out.sort_values(["golden_boot_tiebreak_score", "expected_goals_score", "player"], ascending=[False, False, True]).reset_index(drop=True)
    out["golden_boot_rank"] = range(1, len(out) + 1)
    out["boot_podium"] = out["golden_boot_rank"].map({1: "Golden Boot", 2: "Silver Boot", 3: "Bronze Boot"}).fillna("")
    return out



def calculate_golden_glove_predictions(players_df: pd.DataFrame) -> pd.DataFrame:
    """Estimate Golden Glove among goalkeepers only."""
    out = players_df.copy()
    out["position"] = out.get("position", "").astype(str).str.strip().str.lower()
    out = out[out["position"] == "goalkeeper"].copy()
    out = _ensure_numeric(out, NUMERIC_PLAYER_COLUMNS + PROGRESSION_COLUMNS + ["team_progression_score"])
    out["golden_glove_score"] = (
        out["base_player_rating"]
        + out["goalkeeper_actions_prior"] * float(POSITION_WEIGHTS.get("goalkeeper", {}).get("goalkeeper_actions", 4.0))
        + out["team_progression_score"] * 1.5
        + out["expected_minutes_share"] * 5.0
    ).clip(lower=0.0)
    total = float(out["golden_glove_score"].sum())
    out["golden_glove_probability"] = out["golden_glove_score"] / total if total > 0 else 0.0
    out = out.sort_values(["golden_glove_score", "player"], ascending=[False, True]).reset_index(drop=True)
    out["golden_glove_rank"] = range(1, len(out) + 1)
    out["award"] = out["golden_glove_rank"].map({1: "Golden Glove"}).fillna("")
    return out



def filter_young_player_candidates(players_df: pd.DataFrame, tournament_year: int = 2026) -> pd.DataFrame:
    """Filter players eligible for the Young Player Award."""
    cutoff = pd.Timestamp(YOUNG_PLAYER_CUTOFF_DATE_2026 if tournament_year == 2026 else f"{tournament_year - 21}-01-01")
    out = players_df.copy()
    out["date_of_birth_parsed"] = pd.to_datetime(out.get("date_of_birth"), errors="coerce")
    out = _ensure_numeric(out, ["age"])
    eligible = out["date_of_birth_parsed"].ge(cutoff) | out["age"].le(21)
    return out[eligible].copy()



def calculate_young_player_predictions(players_df: pd.DataFrame) -> pd.DataFrame:
    """Estimate Young Player award probabilities among eligible players."""
    eligible = filter_young_player_candidates(players_df)
    if eligible.empty:
        eligible = players_df.head(0).copy()
        eligible["young_player_score"] = []
        eligible["young_player_probability"] = []
        eligible["young_player_rank"] = []
        eligible["award"] = []
        return eligible
    scored = calculate_golden_ball_predictions(eligible)
    scored["young_player_score"] = scored["final_golden_ball_score"]
    total = float(scored["young_player_score"].sum())
    scored["young_player_probability"] = scored["young_player_score"] / total if total > 0 else 0.0
    scored = scored.sort_values(["young_player_score", "player"], ascending=[False, True]).reset_index(drop=True)
    scored["young_player_rank"] = range(1, len(scored) + 1)
    scored["award"] = scored["young_player_rank"].map({1: "Young Player Award"}).fillna("")
    return scored



def calculate_player_of_match_proxy(players_df: pd.DataFrame) -> pd.DataFrame:
    """Estimate Player of the Match counts as a proxy, not match-event simulation."""
    out = players_df.copy()
    if "final_golden_ball_score" not in out.columns:
        out = calculate_golden_ball_predictions(out)
    out = _ensure_numeric(out, PROGRESSION_COLUMNS + ["final_golden_ball_score"])
    out["expected_matches"] = _expected_matches(out)
    team_totals = out.groupby("team")["final_golden_ball_score"].transform("sum").replace(0, 1.0)
    out["player_impact_share_proxy"] = out["final_golden_ball_score"] / team_totals
    out["estimated_potm_count"] = out["expected_matches"] * out["player_impact_share_proxy"]
    out = out.sort_values(["estimated_potm_count", "player"], ascending=[False, True]).reset_index(drop=True)
    out["player_of_match_proxy_rank"] = range(1, len(out) + 1)
    return out



def calculate_goal_of_tournament_proxy(players_df: pd.DataFrame) -> pd.DataFrame:
    """Estimate a goal-of-the-tournament proxy score from attacking/flair priors."""
    out = players_df.copy()
    if "expected_goals_score" not in out.columns:
        out = calculate_golden_boot_predictions(out)
    out = _ensure_numeric(out, ["expected_goals_score", "flair_score", "star_role_score", "final_probability"])
    out["goal_of_tournament_proxy_score"] = (
        out["expected_goals_score"]
        + out["flair_score"] * 2.0
        + out["star_role_score"]
        + out["final_probability"] * 2.0
    ).clip(lower=0.0)
    total = float(out["goal_of_tournament_proxy_score"].sum())
    out["goal_of_tournament_proxy_probability"] = out["goal_of_tournament_proxy_score"] / total if total > 0 else 0.0
    out = out.sort_values(["goal_of_tournament_proxy_score", "player"], ascending=[False, True]).reset_index(drop=True)
    out["goal_of_tournament_proxy_rank"] = range(1, len(out) + 1)
    return out
