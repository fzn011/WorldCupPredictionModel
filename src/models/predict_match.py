"""Baseline match-result prediction helpers."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from src.models.model_features import load_feature_columns, load_feature_dataset
from src.utils.constants import (
    BEST_BASELINE_MODEL_FILE,
    BASELINE_MODEL_DIR,
    FEATURE_COLUMNS_FILE,
    RESULT_LABELS,
    TARGET_CLASS_ORDER,
)


def load_baseline_model(model_path: str | None = None):
    """Load the saved best baseline model."""
    path = Path(model_path) if model_path else Path(BASELINE_MODEL_DIR) / BEST_BASELINE_MODEL_FILE
    if not path.is_file():
        raise FileNotFoundError(
            f"Baseline model not found at {path}. Run `python scripts/train_baseline_models.py` first."
        )
    return joblib.load(path)


def _load_feature_columns(feature_columns_path: str | None = None) -> list[str]:
    path = Path(feature_columns_path) if feature_columns_path else Path(BASELINE_MODEL_DIR) / FEATURE_COLUMNS_FILE
    if not path.is_file():
        raise FileNotFoundError(
            f"Feature column list not found at {path}. Run `python scripts/train_baseline_models.py` first."
        )
    return load_feature_columns(str(path))


def _probability_payload(model, row_df: pd.DataFrame) -> dict[str, float]:
    probabilities = {label: 0.0 for label in RESULT_LABELS.values()}
    if not hasattr(model, "predict_proba"):
        return probabilities

    proba = model.predict_proba(row_df)[0]
    class_to_prob = {int(cls): float(prob) for cls, prob in zip(model.classes_, proba)}
    for cls in TARGET_CLASS_ORDER:
        probabilities[RESULT_LABELS[cls]] = class_to_prob.get(cls, 0.0)
    return probabilities


def predict_from_feature_row(
    feature_row: pd.Series | dict,
    model_path: str | None = None,
    feature_columns_path: str | None = None,
) -> dict:
    """Predict probabilities from a pre-computed feature row."""
    model = load_baseline_model(model_path=model_path)
    feature_columns = _load_feature_columns(feature_columns_path)

    row_df = pd.DataFrame([feature_row]).reindex(columns=feature_columns)
    probabilities = _probability_payload(model, row_df)
    predicted_label = max(probabilities, key=probabilities.get)
    predicted_class = {value: key for key, value in RESULT_LABELS.items()}[predicted_label]

    return {
        "predicted_class": predicted_class,
        "predicted_label": predicted_label,
        "probabilities": probabilities,
    }


def predict_match_result(team_a: str, team_b: str) -> dict:
    """Placeholder for future arbitrary-team predictions.

    Step 5 only supports predicting rows that already exist in the feature
    dataset. Arbitrary team-name prediction will arrive after Step 6/7 once the
    app can generate live pre-match features.
    """
    return {
        "team_a": team_a,
        "team_b": team_b,
        "message": (
            "Future match prediction from team names will be implemented after "
            "Step 6/7, when the app can generate live pre-match features for "
            "arbitrary teams."
        ),
    }


def predict_existing_match_by_id(match_id: str | int) -> dict:
    """Predict the result for an existing engineered match row."""
    feature_df = load_feature_dataset()
    if "match_id" not in feature_df.columns:
        raise ValueError("The feature dataset does not contain a 'match_id' column.")

    matches = feature_df.loc[feature_df["match_id"].astype(str) == str(match_id)]
    if matches.empty:
        raise ValueError(f"Match id '{match_id}' was not found in the feature dataset.")

    row = matches.iloc[0]
    prediction = predict_from_feature_row(row)
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
