"""Utilities for prediction confidence, flattening, history, and explanation views."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import src.utils.constants as C

HIGH_CONFIDENCE_THRESHOLD = getattr(C, "HIGH_CONFIDENCE_THRESHOLD", 0.60)
MEDIUM_CONFIDENCE_THRESHOLD = getattr(C, "MEDIUM_CONFIDENCE_THRESHOLD", 0.45)
PREDICTION_HISTORY_FILE = getattr(C, "PREDICTION_HISTORY_FILE", "future_prediction_log.csv")
LATEST_PREDICTION_REPORT_FILE = getattr(C, "LATEST_PREDICTION_REPORT_FILE", "latest_prediction_report.csv")
PREDICTION_EXPLANATION_COLUMNS = getattr(C, "PREDICTION_EXPLANATION_COLUMNS", [])



def get_prediction_confidence(probabilities: dict) -> dict:
    """Return max probability and confidence label for a prediction."""
    values = [float(v) for v in (probabilities or {}).values()] if probabilities else [0.0]
    max_probability = max(values) if values else 0.0

    if max_probability >= HIGH_CONFIDENCE_THRESHOLD:
        label = "High"
    elif max_probability >= MEDIUM_CONFIDENCE_THRESHOLD:
        label = "Medium"
    else:
        label = "Low"

    return {
        "max_probability": float(max_probability),
        "confidence_label": label,
    }



def format_probability(value: float) -> str:
    """Format probability value as percentage string with two decimals."""
    return f"{float(value) * 100:.2f}%"



def flatten_prediction_result(prediction_result: dict) -> dict:
    """Flatten a nested prediction payload into a CSV-friendly one-row dict."""
    result = prediction_result or {}
    probabilities = result.get("probabilities", {}) or {}
    confidence = result.get("confidence") or get_prediction_confidence(probabilities)
    notes = result.get("notes", [])

    return {
        "prediction_timestamp": pd.Timestamp.now("UTC").isoformat(),
        "team_a": result.get("team_a"),
        "team_b": result.get("team_b"),
        "match_date": result.get("match_date"),
        "tournament": result.get("tournament"),
        "city": result.get("city"),
        "country": result.get("country"),
        "neutral": result.get("neutral"),
        "model_type": result.get("model_type"),
        "predicted_class": result.get("predicted_class"),
        "predicted_label": result.get("predicted_label"),
        "team_a_loss_probability": float(probabilities.get("team_a_loss", 0.0)),
        "draw_probability": float(probabilities.get("draw", 0.0)),
        "team_a_win_probability": float(probabilities.get("team_a_win", 0.0)),
        "confidence_label": confidence.get("confidence_label"),
        "max_probability": float(confidence.get("max_probability", 0.0)),
        "notes": " | ".join(str(note) for note in notes) if isinstance(notes, list) else str(notes or ""),
    }



def append_prediction_history(prediction_result: dict, output_path: str | None = None) -> str:
    """Append one flattened prediction row into history CSV and return path."""
    path = Path(output_path) if output_path else Path("reports") / PREDICTION_HISTORY_FILE
    path.parent.mkdir(parents=True, exist_ok=True)

    row_df = pd.DataFrame([flatten_prediction_result(prediction_result)])
    if path.is_file():
        existing = pd.read_csv(path)
        out = pd.concat([existing, row_df], ignore_index=True)
    else:
        out = row_df

    out.to_csv(path, index=False)
    return str(path)



def save_latest_prediction_report(prediction_result: dict, output_path: str | None = None) -> str:
    """Save latest prediction as single-row report CSV and return path."""
    path = Path(output_path) if output_path else Path("reports") / LATEST_PREDICTION_REPORT_FILE
    path.parent.mkdir(parents=True, exist_ok=True)

    row_df = pd.DataFrame([flatten_prediction_result(prediction_result)])
    row_df.to_csv(path, index=False)
    return str(path)



def load_prediction_history(path: str | None = None) -> pd.DataFrame:
    """Load prediction history CSV; return empty DataFrame if missing/unreadable."""
    target = Path(path) if path else Path("reports") / PREDICTION_HISTORY_FILE
    if not target.is_file():
        return pd.DataFrame()

    try:
        return pd.read_csv(target)
    except Exception:
        return pd.DataFrame()



def extract_prediction_explanation_features(feature_row: pd.DataFrame | pd.Series) -> pd.DataFrame:
    """Extract explanation feature/value pairs for display."""
    if isinstance(feature_row, pd.Series):
        row = feature_row
    elif isinstance(feature_row, pd.DataFrame):
        if feature_row.empty:
            row = pd.Series(dtype=object)
        else:
            row = feature_row.iloc[0]
    else:
        row = pd.Series(dtype=object)

    records = []
    for column in PREDICTION_EXPLANATION_COLUMNS:
        records.append({
            "feature": column,
            "value": row.get(column, None),
        })

    return pd.DataFrame(records)
