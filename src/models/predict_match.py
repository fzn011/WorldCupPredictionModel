"""Baseline match-result prediction helpers."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from src.features.future_match_features import generate_future_match_feature_row
from src.models.model_features import load_feature_columns, load_feature_dataset
from src.models.prediction_utils import get_prediction_confidence
import src.utils.constants as C

BEST_BASELINE_MODEL_FILE = getattr(C, "BEST_BASELINE_MODEL_FILE", "best_baseline_model.joblib")
BASELINE_MODEL_DIR = getattr(C, "BASELINE_MODEL_DIR", "models/baseline")
FEATURE_COLUMNS_FILE = getattr(C, "FEATURE_COLUMNS_FILE", "feature_columns.json")
BEST_IMPROVED_MODEL_FILE = getattr(C, "BEST_IMPROVED_MODEL_FILE", "best_improved_model.joblib")
IMPROVED_MODEL_DIR = getattr(C, "IMPROVED_MODEL_DIR", "models/improved")
IMPROVED_FEATURE_COLUMNS_FILE = getattr(C, "IMPROVED_FEATURE_COLUMNS_FILE", "improved_feature_columns.json")
BEST_RANKING_ENHANCED_MODEL_FILE = getattr(
    C, "BEST_RANKING_ENHANCED_MODEL_FILE", "best_ranking_enhanced_model.joblib"
)
RANKING_ENHANCED_MODEL_DIR = getattr(C, "RANKING_ENHANCED_MODEL_DIR", "models/ranking_enhanced")
RANKING_FEATURE_COLUMNS_FILE = getattr(C, "RANKING_FEATURE_COLUMNS_FILE", "ranking_feature_columns.json")
PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")
RANKING_FEATURE_DATASET_FILE = getattr(C, "RANKING_FEATURE_DATASET_FILE", "ranking_feature_dataset.csv")
RANKING_FEATURE_DATASET_SAMPLE_FILE = getattr(
    C, "RANKING_FEATURE_DATASET_SAMPLE_FILE", "ranking_feature_dataset_sample.csv"
)
RESULT_LABELS = getattr(C, "RESULT_LABELS", {0: "team_a_loss", 1: "draw", 2: "team_a_win"})
TARGET_CLASS_ORDER = getattr(C, "TARGET_CLASS_ORDER", [0, 1, 2])
DEFAULT_FUTURE_MATCH_DATE = getattr(C, "DEFAULT_FUTURE_MATCH_DATE", "2026-06-11")
DEFAULT_FUTURE_TOURNAMENT = getattr(C, "DEFAULT_FUTURE_TOURNAMENT", "FIFA World Cup")
DEFAULT_FUTURE_CITY = getattr(C, "DEFAULT_FUTURE_CITY", "Unknown")
DEFAULT_FUTURE_COUNTRY = getattr(C, "DEFAULT_FUTURE_COUNTRY", "Unknown")
DEFAULT_FUTURE_NEUTRAL = getattr(C, "DEFAULT_FUTURE_NEUTRAL", 1)
PREDICTION_EXPLANATION_COLUMNS = getattr(C, "PREDICTION_EXPLANATION_COLUMNS", [])


def load_baseline_model(model_path: str | None = None):
    """Load the saved best baseline model."""
    path = Path(model_path) if model_path else Path(BASELINE_MODEL_DIR) / BEST_BASELINE_MODEL_FILE
    if not path.is_file():
        raise FileNotFoundError(
            f"Baseline model not found at {path}. Run `python scripts/train_baseline_models.py` first."
        )
    return joblib.load(path)


def load_best_available_model(
    prefer_ranking: bool = True,
    prefer_improved: bool = True,
):
    """Load ranking-enhanced/improved/baseline model by preference order."""
    ranking_path = Path(RANKING_ENHANCED_MODEL_DIR) / BEST_RANKING_ENHANCED_MODEL_FILE
    improved_path = Path(IMPROVED_MODEL_DIR) / BEST_IMPROVED_MODEL_FILE
    baseline_path = Path(BASELINE_MODEL_DIR) / BEST_BASELINE_MODEL_FILE

    if prefer_ranking and ranking_path.is_file():
        return joblib.load(ranking_path), "ranking_enhanced"

    if prefer_improved and improved_path.is_file():
        return joblib.load(improved_path), "improved"

    if baseline_path.is_file():
        return joblib.load(baseline_path), "baseline"

    raise FileNotFoundError(
        "No trained model found. Run baseline, improved, or ranking-enhanced training scripts first."
    )


def _load_feature_columns(feature_columns_path: str | None = None) -> list[str]:
    path = Path(feature_columns_path) if feature_columns_path else Path(BASELINE_MODEL_DIR) / FEATURE_COLUMNS_FILE
    if not path.is_file():
        raise FileNotFoundError(
            f"Feature column list not found at {path}. Run `python scripts/train_baseline_models.py` first."
        )
    return load_feature_columns(str(path))


def load_best_available_feature_columns(
    prefer_ranking: bool = True,
    prefer_improved: bool = True,
) -> list[str]:
    """Load ranking/improved/baseline feature columns by preference order."""
    ranking_path = Path(RANKING_ENHANCED_MODEL_DIR) / RANKING_FEATURE_COLUMNS_FILE
    improved_path = Path(IMPROVED_MODEL_DIR) / IMPROVED_FEATURE_COLUMNS_FILE
    baseline_path = Path(BASELINE_MODEL_DIR) / FEATURE_COLUMNS_FILE

    if prefer_ranking and ranking_path.is_file():
        return load_feature_columns(str(ranking_path))
    if prefer_improved and improved_path.is_file():
        return load_feature_columns(str(improved_path))
    if baseline_path.is_file():
        return load_feature_columns(str(baseline_path))

    raise FileNotFoundError(
        "No feature column list found. Run `python scripts/train_baseline_models.py` or `python scripts/train_improved_models.py` first."
    )


def get_probability_dict_from_model(model, X_row: pd.DataFrame) -> dict[str, float]:
    """Return probability dict aligned to target classes [0, 1, 2]."""
    probabilities = {label: 0.0 for label in RESULT_LABELS.values()}
    if not hasattr(model, "predict_proba"):
        return probabilities

    proba = model.predict_proba(X_row)[0]
    class_to_prob = {int(cls): float(prob) for cls, prob in zip(model.classes_, proba)}
    for cls in TARGET_CLASS_ORDER:
        probabilities[RESULT_LABELS[cls]] = class_to_prob.get(cls, 0.0)
    return probabilities


def _probability_payload(model, row_df: pd.DataFrame) -> dict[str, float]:
    return get_probability_dict_from_model(model, row_df)


def predict_from_feature_row(
    feature_row: pd.Series | dict | pd.DataFrame,
    model_path: str | None = None,
    feature_columns_path: str | None = None,
    prefer_ranking: bool = True,
    prefer_improved: bool = True,
) -> dict:
    """Predict probabilities from a pre-computed feature row."""
    if model_path:
        model = load_baseline_model(model_path=model_path)
        model_type = "baseline"
    else:
        model, model_type = load_best_available_model(
            prefer_ranking=prefer_ranking,
            prefer_improved=prefer_improved,
        )

    if feature_columns_path:
        feature_columns = _load_feature_columns(feature_columns_path)
    else:
        feature_columns = load_best_available_feature_columns(
            prefer_ranking=prefer_ranking,
            prefer_improved=prefer_improved,
        )

    if isinstance(feature_row, pd.DataFrame):
        if feature_row.empty:
            raise ValueError("feature_row DataFrame is empty.")
        row_df = feature_row.iloc[[0]].copy()
    else:
        row_df = pd.DataFrame([feature_row])

    row_df = row_df.reindex(columns=feature_columns)
    probabilities = _probability_payload(model, row_df)
    predicted_label = max(probabilities, key=probabilities.get)
    predicted_class = {value: key for key, value in RESULT_LABELS.items()}[predicted_label]

    return {
        "model_type": model_type,
        "predicted_class": predicted_class,
        "predicted_label": predicted_label,
        "probabilities": probabilities,
    }


def predict_future_match(
    team_a: str,
    team_b: str,
    match_date: str = DEFAULT_FUTURE_MATCH_DATE,
    tournament: str = DEFAULT_FUTURE_TOURNAMENT,
    city: str = DEFAULT_FUTURE_CITY,
    country: str = DEFAULT_FUTURE_COUNTRY,
    neutral: int = DEFAULT_FUTURE_NEUTRAL,
    prefer_ranking: bool = True,
    prefer_improved: bool = True,
) -> dict:
    """Generate features for an arbitrary future match and predict outcome."""
    feature_row = generate_future_match_feature_row(
        team_a=team_a,
        team_b=team_b,
        match_date=match_date,
        tournament=tournament,
        city=city,
        country=country,
        neutral=neutral,
    )

    try:
        model, model_type = load_best_available_model(
            prefer_ranking=prefer_ranking,
            prefer_improved=prefer_improved,
        )
        feature_columns = load_best_available_feature_columns(
            prefer_ranking=prefer_ranking,
            prefer_improved=prefer_improved,
        )
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            "No trained model artifacts found. Run `python scripts/train_ranking_enhanced_model.py` first."
        ) from exc

    X_row = feature_row.reindex(columns=feature_columns)
    probabilities = get_probability_dict_from_model(model, X_row)
    predicted_label = max(probabilities, key=probabilities.get)
    predicted_class = {value: key for key, value in RESULT_LABELS.items()}[predicted_label]
    confidence = get_prediction_confidence(probabilities)

    notes: list[str] = []
    if "team_a_has_fifa_ranking" in feature_row.columns and int(feature_row.iloc[0]["team_a_has_fifa_ranking"]) == 0:
        notes.append("FIFA ranking snapshot missing for team_a.")
    if "team_b_has_fifa_ranking" in feature_row.columns and int(feature_row.iloc[0]["team_b_has_fifa_ranking"]) == 0:
        notes.append("FIFA ranking snapshot missing for team_b.")
    if "team_a_has_elo" in feature_row.columns and int(feature_row.iloc[0]["team_a_has_elo"]) == 0:
        notes.append("Elo snapshot missing for team_a.")
    if "team_b_has_elo" in feature_row.columns and int(feature_row.iloc[0]["team_b_has_elo"]) == 0:
        notes.append("Elo snapshot missing for team_b.")

    preview_columns = list(PREDICTION_EXPLANATION_COLUMNS)
    feature_preview = {
        column: feature_row.iloc[0].get(column)
        for column in preview_columns
        if column in feature_row.columns
    }

    row = feature_row.iloc[0]
    match_date_value = pd.to_datetime(row.get("date"), errors="coerce")

    return {
        "team_a": str(row.get("team_a", team_a)),
        "team_b": str(row.get("team_b", team_b)),
        "match_date": str(match_date_value.date()) if pd.notna(match_date_value) else str(match_date),
        "tournament": row.get("tournament", tournament),
        "city": row.get("city", city),
        "country": row.get("country", country),
        "neutral": int(pd.to_numeric(row.get("neutral", neutral), errors="coerce") if pd.notna(row.get("neutral", neutral)) else neutral),
        "model_type": model_type,
        "predicted_class": predicted_class,
        "predicted_label": predicted_label,
        "probabilities": probabilities,
        "confidence": confidence,
        "features_used": feature_columns,
        "feature_preview": feature_preview,
        "notes": notes,
        "feature_row": feature_row,
    }


def predict_match_result(team_a: str, team_b: str) -> dict:
    """Backward-compatible wrapper for default future match prediction."""
    try:
        return predict_future_match(team_a=team_a, team_b=team_b)
    except (FileNotFoundError, ValueError) as exc:
        return {
            "team_a": team_a,
            "team_b": team_b,
            "error": str(exc),
            "message": (
                "Future prediction failed. Run `python scripts/train_ranking_enhanced_model.py` first "
                "and ensure input teams/date are valid."
            ),
        }


def predict_existing_match_by_id(match_id: str | int) -> dict:
    """Predict the result for an existing engineered match row."""
    ranking_model_path = Path(RANKING_ENHANCED_MODEL_DIR) / BEST_RANKING_ENHANCED_MODEL_FILE
    ranking_real_path = PROCESSED_DATA_DIR / RANKING_FEATURE_DATASET_FILE
    ranking_sample_path = PROCESSED_DATA_DIR / RANKING_FEATURE_DATASET_SAMPLE_FILE

    if ranking_model_path.is_file() and ranking_real_path.is_file():
        feature_df = pd.read_csv(ranking_real_path, parse_dates=["date"])
    elif ranking_model_path.is_file() and ranking_sample_path.is_file():
        feature_df = pd.read_csv(ranking_sample_path, parse_dates=["date"])
    else:
        feature_df = load_feature_dataset()

    if "match_id" not in feature_df.columns:
        raise ValueError("The feature dataset does not contain a 'match_id' column.")

    matches = feature_df.loc[feature_df["match_id"].astype(str) == str(match_id)]
    if matches.empty and (ranking_model_path.is_file() and (ranking_real_path.is_file() or ranking_sample_path.is_file())):
        fallback_df = load_feature_dataset()
        if "match_id" not in fallback_df.columns:
            raise ValueError("The feature dataset does not contain a 'match_id' column.")
        matches = fallback_df.loc[fallback_df["match_id"].astype(str) == str(match_id)]

    if matches.empty:
        raise ValueError(f"Match id '{match_id}' was not found in the feature dataset.")

    row = matches.iloc[0]
    prediction = predict_from_feature_row(
        row,
        prefer_ranking=True,
        prefer_improved=True,
    )
    prediction.update(
        {
            "match_id": row.get("match_id"),
            "date": str(row.get("date")) if pd.notna(row.get("date")) else None,
            "team_a": row.get("team_a"),
            "team_b": row.get("team_b"),
            "actual_label": row.get("result_label"),
        }
    )
    return prediction
