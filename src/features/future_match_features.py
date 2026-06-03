"""Future match feature generation for arbitrary team-vs-team predictions."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data.prepare_datasets import prepare_step3_clean_datasets
from src.features.build_features import add_host_flags, add_match_context_features
from src.features.historical_features import build_historical_features_for_match
from src.features.ranking_features import add_ranking_features_to_matches
import src.utils.constants as C
from src.utils.team_name_mapping import slugify_team_name, standardize_team_name

CANONICAL_MATCHES_FILE = getattr(C, "CANONICAL_MATCHES_FILE", "canonical_matches.csv")
CANONICAL_MATCHES_SAMPLE_FILE = getattr(C, "CANONICAL_MATCHES_SAMPLE_FILE", "canonical_matches_sample.csv")
TEAM_REGISTRY_FILE = getattr(C, "TEAM_REGISTRY_FILE", "team_registry.csv")
RANKING_FEATURE_DATASET_FILE = getattr(C, "RANKING_FEATURE_DATASET_FILE", "ranking_feature_dataset.csv")
TEAM_STRENGTH_SNAPSHOT_FILE = getattr(C, "TEAM_STRENGTH_SNAPSHOT_FILE", "team_strength_snapshot.csv")
PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")
CANONICAL_MATCH_COLUMNS = getattr(C, "CANONICAL_MATCH_COLUMNS", [])
DEFAULT_FUTURE_TOURNAMENT = getattr(C, "DEFAULT_FUTURE_TOURNAMENT", "FIFA World Cup")
DEFAULT_FUTURE_CITY = getattr(C, "DEFAULT_FUTURE_CITY", "Unknown")
DEFAULT_FUTURE_COUNTRY = getattr(C, "DEFAULT_FUTURE_COUNTRY", "Unknown")
DEFAULT_FUTURE_NEUTRAL = getattr(C, "DEFAULT_FUTURE_NEUTRAL", 1)



def _load_csv_if_exists(path: Path) -> pd.DataFrame:
    if path.is_file():
        parse_dates = ["date"] if path.name in {CANONICAL_MATCHES_FILE, CANONICAL_MATCHES_SAMPLE_FILE, RANKING_FEATURE_DATASET_FILE} else None
        return pd.read_csv(path, parse_dates=parse_dates)
    return pd.DataFrame()



def load_best_available_processed_data() -> dict:
    """Load canonical/ranking/team-strength/team-registry data with fallback."""
    real_canonical_path = PROCESSED_DATA_DIR / CANONICAL_MATCHES_FILE
    sample_canonical_path = PROCESSED_DATA_DIR / CANONICAL_MATCHES_SAMPLE_FILE

    if real_canonical_path.is_file():
        canonical_df = pd.read_csv(real_canonical_path, parse_dates=["date"])
    elif sample_canonical_path.is_file():
        canonical_df = pd.read_csv(sample_canonical_path, parse_dates=["date"])
    else:
        prepare_step3_clean_datasets()
        if real_canonical_path.is_file():
            canonical_df = pd.read_csv(real_canonical_path, parse_dates=["date"])
        elif sample_canonical_path.is_file():
            canonical_df = pd.read_csv(sample_canonical_path, parse_dates=["date"])
        else:
            raise FileNotFoundError("No canonical dataset found. Run `python main.py` first.")

    ranking_feature_df = _load_csv_if_exists(PROCESSED_DATA_DIR / RANKING_FEATURE_DATASET_FILE)
    team_strength_df = _load_csv_if_exists(PROCESSED_DATA_DIR / TEAM_STRENGTH_SNAPSHOT_FILE)
    team_registry_df = _load_csv_if_exists(PROCESSED_DATA_DIR / TEAM_REGISTRY_FILE)

    if "date" in canonical_df.columns:
        canonical_df["date"] = pd.to_datetime(canonical_df["date"], errors="coerce")

    return {
        "canonical_matches": canonical_df,
        "ranking_feature_dataset": ranking_feature_df,
        "team_strength_snapshot": team_strength_df,
        "team_registry": team_registry_df,
    }



def get_available_teams() -> list[str]:
    """Return sorted, standardized team names available for prediction."""
    loaded = load_best_available_processed_data()
    registry_df = loaded["team_registry"]
    canonical_df = loaded["canonical_matches"]

    values: list[str] = []
    if not registry_df.empty and "team" in registry_df.columns:
        values.extend(registry_df["team"].astype(str).tolist())
    elif not canonical_df.empty:
        for column in ("team_a", "team_b"):
            if column in canonical_df.columns:
                values.extend(canonical_df[column].astype(str).tolist())

    teams = {
        standardize_team_name(value)
        for value in values
        if isinstance(value, str) and value.strip() and value.strip().lower() != "nan"
    }
    return sorted(team for team in teams if team)



def create_future_canonical_match_row(
    team_a: str,
    team_b: str,
    match_date: str,
    tournament: str = DEFAULT_FUTURE_TOURNAMENT,
    city: str = DEFAULT_FUTURE_CITY,
    country: str = DEFAULT_FUTURE_COUNTRY,
    neutral: int = DEFAULT_FUTURE_NEUTRAL,
) -> pd.DataFrame:
    """Create a one-row canonical-like match row with unknown result fields."""
    team_a_clean = standardize_team_name(team_a)
    team_b_clean = standardize_team_name(team_b)

    if not team_a_clean or not team_b_clean:
        raise ValueError("Both team_a and team_b are required.")
    if team_a_clean == team_b_clean:
        raise ValueError("team_a and team_b must be different teams.")

    date_value = pd.to_datetime(match_date, errors="coerce")
    if pd.isna(date_value):
        raise ValueError("match_date must be a valid date string.")

    match_id = f"future_{date_value.strftime('%Y%m%d')}_{slugify_team_name(team_a_clean)}-vs-{slugify_team_name(team_b_clean)}"

    row = {
        "match_id": match_id,
        "date": date_value,
        "year": int(date_value.year),
        "team_a": team_a_clean,
        "team_b": team_b_clean,
        "team_a_score": pd.NA,
        "team_b_score": pd.NA,
        "score_difference": pd.NA,
        "total_goals": pd.NA,
        "result": pd.NA,
        "result_label": None,
        "winner": None,
        "loser": None,
        "is_draw": pd.NA,
        "tournament": tournament or DEFAULT_FUTURE_TOURNAMENT,
        "city": city or DEFAULT_FUTURE_CITY,
        "country": country or DEFAULT_FUTURE_COUNTRY,
        "neutral": int(neutral),
        "has_shootout": 0,
        "shootout_winner": None,
        "shootout_loser": None,
        "progression_winner": None,
        "data_source": "future_user_input",
    }

    df = pd.DataFrame([row])
    if CANONICAL_MATCH_COLUMNS:
        for column in CANONICAL_MATCH_COLUMNS:
            if column not in df.columns:
                df[column] = pd.NA
        df = df[[*CANONICAL_MATCH_COLUMNS, *[c for c in df.columns if c not in CANONICAL_MATCH_COLUMNS]]]

    return df



def _ensure_ranking_columns(feature_row: pd.DataFrame) -> pd.DataFrame:
    out = feature_row.copy()
    maybe_columns = [
        "team_a_fifa_rank",
        "team_b_fifa_rank",
        "diff_fifa_rank",
        "team_a_fifa_points",
        "team_b_fifa_points",
        "diff_fifa_points",
        "team_a_elo_rank",
        "team_b_elo_rank",
        "diff_elo_rank",
        "team_a_elo",
        "team_b_elo",
        "diff_elo",
        "team_a_strength_score",
        "team_b_strength_score",
        "diff_strength_score",
    ]
    for column in maybe_columns:
        if column not in out.columns:
            out[column] = pd.NA

    for flag_col in ["team_a_has_fifa_ranking", "team_b_has_fifa_ranking", "team_a_has_elo", "team_b_has_elo"]:
        if flag_col not in out.columns:
            out[flag_col] = 0
        out[flag_col] = pd.to_numeric(out[flag_col], errors="coerce").fillna(0).astype(int)

    return out



def generate_future_match_feature_row(
    team_a: str,
    team_b: str,
    match_date: str,
    tournament: str = DEFAULT_FUTURE_TOURNAMENT,
    city: str = DEFAULT_FUTURE_CITY,
    country: str = DEFAULT_FUTURE_COUNTRY,
    neutral: int = DEFAULT_FUTURE_NEUTRAL,
) -> pd.DataFrame:
    """Generate a one-row leakage-safe feature row for an arbitrary future match."""
    loaded = load_best_available_processed_data()
    canonical_df = loaded["canonical_matches"].copy()
    team_strength_df = loaded["team_strength_snapshot"].copy()

    if canonical_df.empty:
        raise ValueError("Canonical match history is empty. Run data preparation first.")

    canonical_df["date"] = pd.to_datetime(canonical_df["date"], errors="coerce")
    canonical_df = canonical_df.loc[canonical_df["date"].notna()].copy()

    future_row = create_future_canonical_match_row(
        team_a=team_a,
        team_b=team_b,
        match_date=match_date,
        tournament=tournament,
        city=city,
        country=country,
        neutral=neutral,
    )

    feature_map = build_historical_features_for_match(future_row.iloc[0], canonical_df)

    feature_row = future_row.copy()
    for key, value in feature_map.items():
        feature_row[key] = value

    feature_row = add_match_context_features(feature_row)
    feature_row = add_host_flags(feature_row)

    if not team_strength_df.empty and "team" in team_strength_df.columns:
        team_strength_df = team_strength_df.copy()
        team_strength_df["team"] = team_strength_df["team"].map(standardize_team_name)
        feature_row = add_ranking_features_to_matches(feature_row, team_strength_df)

    feature_row = _ensure_ranking_columns(feature_row)

    # Keep target columns unknown for future prediction rows.
    for target_col in ["result", "result_label", "winner", "loser", "is_draw", "team_a_score", "team_b_score", "score_difference", "total_goals"]:
        if target_col in feature_row.columns:
            feature_row[target_col] = pd.NA

    return feature_row.reset_index(drop=True)



def create_future_prediction_report(feature_row: pd.DataFrame, prediction_result: dict) -> pd.DataFrame:
    """Create a one-row report DataFrame for a future match prediction."""
    if feature_row is None or feature_row.empty:
        raise ValueError("feature_row must contain exactly one row.")

    row = feature_row.iloc[0]
    probabilities = prediction_result.get("probabilities", {})

    report_row = {
        "prediction_timestamp": pd.Timestamp.now("UTC").isoformat(),
        "team_a": row.get("team_a"),
        "team_b": row.get("team_b"),
        "match_date": str(row.get("date")) if pd.notna(row.get("date")) else None,
        "tournament": row.get("tournament"),
        "city": row.get("city"),
        "country": row.get("country"),
        "neutral": row.get("neutral"),
        "model_type": prediction_result.get("model_type"),
        "predicted_class": prediction_result.get("predicted_class"),
        "predicted_label": prediction_result.get("predicted_label"),
        "team_a_loss_probability": probabilities.get("team_a_loss", 0.0),
        "draw_probability": probabilities.get("draw", 0.0),
        "team_a_win_probability": probabilities.get("team_a_win", 0.0),
    }
    return pd.DataFrame([report_row])
