"""Step 17 Golden Ball / Best Player prediction utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C
from src.utils.team_name_mapping import standardize_team_name

PROJECT_ROOT = getattr(C, "PROJECT_ROOT", Path(__file__).resolve().parents[2])
DATA_DIR = getattr(C, "DATA_DIR", PROJECT_ROOT / "data")
PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", DATA_DIR / "processed")
SAMPLE_DATA_DIR = getattr(C, "SAMPLE_DATA_DIR", DATA_DIR / "sample")
REPORTS_DIR = PROJECT_ROOT / "reports"

PLAYER_CANDIDATES_FILE = getattr(C, "PLAYER_CANDIDATES_FILE", "player_candidates.csv")
SAMPLE_PLAYER_CANDIDATES_FILE = getattr(C, "SAMPLE_PLAYER_CANDIDATES_FILE", "sample_player_candidates.csv")
MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE = getattr(
    C,
    "MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE",
    "monte_carlo_team_stage_probabilities.csv",
)
GOLDEN_BALL_CANDIDATES_FILE = getattr(C, "GOLDEN_BALL_CANDIDATES_FILE", "golden_ball_candidates.csv")
GOLDEN_BALL_PREDICTIONS_FILE = getattr(C, "GOLDEN_BALL_PREDICTIONS_FILE", "golden_ball_predictions.csv")
GOLDEN_BALL_SUMMARY_FILE = getattr(C, "GOLDEN_BALL_SUMMARY_FILE", "golden_ball_summary.json")
GOLDEN_BALL_VALIDATION_REPORT_FILE = getattr(
    C,
    "GOLDEN_BALL_VALIDATION_REPORT_FILE",
    "golden_ball_validation_report.csv",
)
GOLDEN_BALL_REPORT_FILE = getattr(C, "GOLDEN_BALL_REPORT_FILE", "golden_ball_report.md")

PLAYER_POSITIONS = list(getattr(C, "PLAYER_POSITIONS", ["forward", "midfielder", "defender", "goalkeeper"]))
POSITION_WEIGHTS = dict(getattr(C, "POSITION_WEIGHTS", {}))
TEAM_PROGRESSION_WEIGHTS = dict(getattr(C, "TEAM_PROGRESSION_WEIGHTS", {}))

REQUIRED_PLAYER_COLUMNS: list[str] = [
    "player",
    "team",
    "position",
    "base_player_rating",
    "expected_minutes_share",
    "goals_prior",
    "assists_prior",
    "chance_creation_prior",
    "defensive_actions_prior",
    "goalkeeper_actions_prior",
    "star_role_score",
]

TEAM_STAGE_COLUMNS: list[str] = [
    "team",
    "round_of_32_probability",
    "round_of_16_probability",
    "quarter_final_probability",
    "semi_final_probability",
    "final_probability",
    "champion_probability",
]

NUMERIC_PLAYER_COLUMNS: list[str] = [
    "base_player_rating",
    "expected_minutes_share",
    "goals_prior",
    "assists_prior",
    "chance_creation_prior",
    "defensive_actions_prior",
    "goalkeeper_actions_prior",
    "star_role_score",
]


def _format_markdown_value(value: Any) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, float):
        text = f"{value:.6g}"
    else:
        text = str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def _dataframe_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    headers = [str(column) for column in df.columns]
    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"
    data_rows = [
        "| " + " | ".join(_format_markdown_value(v) for v in row) + " |"
        for row in df.itertuples(index=False, name=None)
    ]
    return "\n".join([header_row, separator_row, *data_rows])


def load_player_candidates(path: str | None = None) -> pd.DataFrame:
    """Load player candidates from processed file first, else sample fallback."""
    if path:
        candidate_path = Path(path)
    else:
        processed_path = PROCESSED_DATA_DIR / PLAYER_CANDIDATES_FILE
        sample_path = SAMPLE_DATA_DIR / SAMPLE_PLAYER_CANDIDATES_FILE
        candidate_path = processed_path if processed_path.is_file() else sample_path

    if not candidate_path.is_file():
        raise FileNotFoundError(f"Player candidate file not found: {candidate_path}")

    df = pd.read_csv(candidate_path)
    if "team" in df.columns:
        df["team"] = df["team"].map(standardize_team_name)
    return df


def validate_player_candidates(df: pd.DataFrame) -> tuple[bool, pd.DataFrame]:
    """Validate candidate dataset structure and value constraints."""
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
    checks.append(
        {
            "check": "player_not_empty",
            "expected": "non-empty",
            "actual": bool(player_not_empty),
            "passed": bool(player_not_empty),
        }
    )
    checks.append(
        {
            "check": "team_not_empty",
            "expected": "non-empty",
            "actual": bool(team_not_empty),
            "passed": bool(team_not_empty),
        }
    )

    allowed_positions = {p.lower() for p in PLAYER_POSITIONS}
    position_series = df["position"].fillna("").astype(str).str.strip().str.lower()
    invalid_positions = sorted(set(position_series[position_series.ne("") & ~position_series.isin(allowed_positions)].tolist()))
    checks.append(
        {
            "check": "position_allowed",
            "expected": f"subset of {sorted(allowed_positions)}",
            "actual": ", ".join(invalid_positions) if invalid_positions else "ok",
            "passed": len(invalid_positions) == 0,
        }
    )

    numeric_conversion_ok = True
    for col in NUMERIC_PLAYER_COLUMNS:
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.isna().any():
            numeric_conversion_ok = False
            break
    checks.append(
        {
            "check": "numeric_columns_convertible",
            "expected": "all numeric columns convertible",
            "actual": bool(numeric_conversion_ok),
            "passed": bool(numeric_conversion_ok),
        }
    )

    numeric_df = df.copy()
    for col in NUMERIC_PLAYER_COLUMNS:
        numeric_df[col] = pd.to_numeric(numeric_df[col], errors="coerce")

    minutes_in_range = numeric_df["expected_minutes_share"].between(0.0, 1.0, inclusive="both").all()
    base_rating_non_negative = (numeric_df["base_player_rating"] >= 0).all()

    checks.append(
        {
            "check": "expected_minutes_share_range",
            "expected": "0<=x<=1",
            "actual": bool(minutes_in_range),
            "passed": bool(minutes_in_range),
        }
    )
    checks.append(
        {
            "check": "base_player_rating_non_negative",
            "expected": ">=0",
            "actual": bool(base_rating_non_negative),
            "passed": bool(base_rating_non_negative),
        }
    )

    report_df = pd.DataFrame(checks)
    is_valid = bool(report_df["passed"].all())
    return is_valid, report_df


def load_team_stage_probabilities(path: str | None = None) -> pd.DataFrame:
    """Load Monte Carlo team stage probabilities."""
    stage_path = Path(path) if path else PROCESSED_DATA_DIR / MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE
    if not stage_path.is_file():
        raise FileNotFoundError("Run python scripts/run_monte_carlo.py --simulations 10 --seed 42 first.")
    df = pd.read_csv(stage_path)
    if "team" in df.columns:
        df["team"] = df["team"].map(standardize_team_name)
    return df


def calculate_position_impact_score(row: pd.Series) -> float:
    """Calculate position-adjusted player impact score from prior profile columns."""
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
    """Calculate weighted team progression signal from Monte Carlo stage probabilities."""
    score = 0.0
    for col, weight in TEAM_PROGRESSION_WEIGHTS.items():
        value = float(pd.to_numeric(team_row.get(col, 0.0), errors="coerce") or 0.0)
        score += value * float(weight)
    return score


def add_team_progression_to_players(players_df: pd.DataFrame, team_stage_df: pd.DataFrame) -> pd.DataFrame:
    """Attach team progression probabilities and scores to player candidates."""
    out = players_df.copy()
    out["team"] = out["team"].map(standardize_team_name)

    stage_keep = [col for col in TEAM_STAGE_COLUMNS if col in team_stage_df.columns]
    stage_df = team_stage_df[stage_keep].copy()
    stage_df["team"] = stage_df["team"].map(standardize_team_name)

    merged = out.merge(stage_df, on="team", how="left", suffixes=("", "_team_stage"))
    probability_cols = [
        "round_of_32_probability",
        "round_of_16_probability",
        "quarter_final_probability",
        "semi_final_probability",
        "final_probability",
        "champion_probability",
    ]
    for col in probability_cols:
        if col not in merged.columns:
            merged[col] = 0.0
        merged[col] = pd.to_numeric(merged[col], errors="coerce").fillna(0.0)

    merged["has_team_progression_data"] = merged[probability_cols].sum(axis=1) > 0
    merged["team_progression_score"] = merged.apply(calculate_team_progression_score, axis=1)
    return merged


def calculate_golden_ball_scores(players_df: pd.DataFrame) -> pd.DataFrame:
    """Compute explainable Golden Ball scores and probability estimates."""
    out = players_df.copy()
    for col in NUMERIC_PLAYER_COLUMNS:
        if col not in out.columns:
            out[col] = 0.0
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0.0)

    if "team_progression_score" not in out.columns:
        out["team_progression_score"] = 0.0
    out["team_progression_score"] = pd.to_numeric(out["team_progression_score"], errors="coerce").fillna(0.0)

    out["position"] = out["position"].fillna("midfielder").astype(str).str.strip().str.lower()
    out["position_impact_score"] = out.apply(calculate_position_impact_score, axis=1)
    out["minutes_factor"] = out["expected_minutes_share"].clip(lower=0.0, upper=1.0)

    out["raw_golden_ball_score"] = (
        out["base_player_rating"]
        + out["position_impact_score"]
        + out["star_role_score"]
        + out["team_progression_score"]
    )
    out["final_golden_ball_score"] = (out["raw_golden_ball_score"] * out["minutes_factor"]).clip(lower=0.0)

    total_score = float(out["final_golden_ball_score"].sum())
    if total_score > 0:
        out["golden_ball_probability"] = out["final_golden_ball_score"] / total_score
    else:
        out["golden_ball_probability"] = 0.0

    out = out.sort_values(["golden_ball_probability", "final_golden_ball_score", "player"], ascending=[False, False, True]).reset_index(drop=True)
    out["rank"] = range(1, len(out) + 1)
    return out


def create_golden_ball_summary(predictions_df: pd.DataFrame, validation_passed: bool) -> dict[str, Any]:
    """Create compact Step 17 summary payload."""
    top_row = predictions_df.iloc[0] if not predictions_df.empty else pd.Series(dtype=object)
    top_probability = float(pd.to_numeric(top_row.get("golden_ball_probability", 0.0), errors="coerce") or 0.0)

    return {
        "status": "ok" if validation_passed else "validation_failed",
        "validation_passed": bool(validation_passed),
        "candidate_count": int(len(predictions_df)),
        "teams_represented": int(predictions_df["team"].nunique()) if "team" in predictions_df.columns and not predictions_df.empty else 0,
        "top_player": str(top_row.get("player", "—")) if not predictions_df.empty else "—",
        "top_team": str(top_row.get("team", "—")) if not predictions_df.empty else "—",
        "top_probability": top_probability,
        "notes": "This is an explainable analytics estimate based on manually editable player priors and Monte Carlo team progression probabilities. It is not an official award prediction.",
    }


def create_golden_ball_report(predictions_df: pd.DataFrame, summary: dict[str, Any]) -> str:
    """Generate Markdown report for Golden Ball analytics estimate."""
    top20 = predictions_df.head(20).copy()
    if not top20.empty:
        top20["golden_ball_probability_percent"] = (top20["golden_ball_probability"] * 100).round(2)
        top20 = top20[
            [
                "rank",
                "player",
                "team",
                "position",
                "golden_ball_probability",
                "golden_ball_probability_percent",
                "final_golden_ball_score",
                "team_progression_score",
                "position_impact_score",
                "star_role_score",
            ]
        ]

    position_breakdown = pd.DataFrame()
    if "position" in predictions_df.columns and not predictions_df.empty:
        position_breakdown = (
            predictions_df.groupby("position", as_index=False)
            .agg(
                candidate_count=("player", "count"),
                total_probability=("golden_ball_probability", "sum"),
                avg_final_score=("final_golden_ball_score", "mean"),
            )
            .sort_values("total_probability", ascending=False)
        )

    lines = [
        "# Golden Ball / Best Player Analytics Report",
        "",
        "## Methodology",
        "- Uses manually editable candidate priors (no live scraping).",
        "- Applies position-specific impact weighting (forward/midfielder/defender/goalkeeper).",
        "- Adds team progression influence from Monte Carlo stage probabilities.",
        "- Applies expected-minutes factor for likely tournament involvement.",
        "- Converts final scores to probability shares across candidates.",
        "",
        "## Summary",
        f"- Candidate count: {summary.get('candidate_count', 0)}",
        f"- Teams represented: {summary.get('teams_represented', 0)}",
        f"- Top player: {summary.get('top_player', '—')}",
        f"- Top team: {summary.get('top_team', '—')}",
        f"- Top probability: {float(summary.get('top_probability', 0.0)):.2%}",
        f"- Validation passed: {summary.get('validation_passed', False)}",
        "",
        "## Top 20 candidates",
        _dataframe_to_markdown(top20) if not top20.empty else "No candidates available.",
        "",
        "## Position breakdown",
        _dataframe_to_markdown(position_breakdown) if not position_breakdown.empty else "No position breakdown available.",
        "",
        "## Team progression note",
        "Team progression is a strong factor in this estimate because end-of-tournament awards often favor players whose teams go deep into semi-finals/final.",
        "",
        "## Limitations",
        "- This is an explainable analytics estimate, not an official award prediction.",
        "- Candidate priors are manually editable inputs and should be updated before production use.",
        "- No live player-stat scraping is used in this step.",
        "- Output quality depends on both player priors and Monte Carlo team progression quality.",
        "",
        "## Responsible-use note",
        "This educational model output is not betting advice.",
    ]
    return "\n".join(lines)


def save_golden_ball_outputs(
    candidates_df: pd.DataFrame,
    predictions_df: pd.DataFrame,
    validation_report_df: pd.DataFrame,
    summary: dict[str, Any],
    report_markdown: str,
) -> dict[str, str]:
    """Persist Step 17 outputs to processed/reports directories."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    candidates_path = PROCESSED_DATA_DIR / GOLDEN_BALL_CANDIDATES_FILE
    predictions_path = PROCESSED_DATA_DIR / GOLDEN_BALL_PREDICTIONS_FILE
    validation_report_path = PROCESSED_DATA_DIR / GOLDEN_BALL_VALIDATION_REPORT_FILE
    summary_path = PROCESSED_DATA_DIR / GOLDEN_BALL_SUMMARY_FILE
    report_path = REPORTS_DIR / GOLDEN_BALL_REPORT_FILE

    candidates_df.to_csv(candidates_path, index=False)
    predictions_df.to_csv(predictions_path, index=False)
    validation_report_df.to_csv(validation_report_path, index=False)
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    report_path.write_text(report_markdown, encoding="utf-8")

    return {
        "candidates_path": str(candidates_path),
        "predictions_path": str(predictions_path),
        "validation_report_path": str(validation_report_path),
        "summary_path": str(summary_path),
        "report_path": str(report_path),
    }
