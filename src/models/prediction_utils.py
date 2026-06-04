"""Prediction utility helpers for confidence, reporting, and display formatting."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C

HIGH_CONFIDENCE_THRESHOLD = getattr(C, "HIGH_CONFIDENCE_THRESHOLD", 0.60)
MEDIUM_CONFIDENCE_THRESHOLD = getattr(C, "MEDIUM_CONFIDENCE_THRESHOLD", 0.45)
PREDICTION_HISTORY_FILE = getattr(C, "PREDICTION_HISTORY_FILE", "prediction_history.csv")
LATEST_PREDICTION_REPORT_FILE = getattr(C, "LATEST_PREDICTION_REPORT_FILE", "latest_prediction_report.csv")


def get_prediction_confidence(probabilities: dict[str, float]) -> tuple[str, float]:
    """Return confidence label and max probability."""
    if not probabilities:
        return "Low", 0.0

    max_probability = float(max(probabilities.values()))
    if max_probability >= HIGH_CONFIDENCE_THRESHOLD:
        return "High", max_probability
    if max_probability >= MEDIUM_CONFIDENCE_THRESHOLD:
        return "Medium", max_probability
    return "Low", max_probability


def format_probability(value: float | int | None) -> str:
    """Format probability as percentage string."""
    if value is None:
        return "N/A"
    try:
        return f"{float(value) * 100:.1f}%"
    except (TypeError, ValueError):
        return "N/A"


def flatten_prediction_result(result: dict[str, Any]) -> dict[str, Any]:
    """Flatten prediction payload into one CSV-friendly row dict."""
    probabilities = result.get("probabilities", {}) or {}
    confidence_label, confidence_score = get_prediction_confidence(probabilities)

    row = {
        "team_a": result.get("team_a"),
        "team_b": result.get("team_b"),
        "match_date": result.get("match_date"),
        "tournament": result.get("tournament"),
        "model_type": result.get("model_type"),
        "predicted_label": result.get("predicted_label"),
        "confidence_label": confidence_label,
        "confidence_score": confidence_score,
        "prob_team_a_loss": probabilities.get("team_a_loss"),
        "prob_draw": probabilities.get("draw"),
        "prob_team_a_win": probabilities.get("team_a_win"),
    }

    notes = result.get("notes", [])
    row["notes"] = " | ".join(str(n) for n in notes) if isinstance(notes, list) else str(notes)
    return row


def append_prediction_history(result: dict[str, Any], output_path: str | None = None) -> Path:
    """Append one flattened prediction row to history CSV."""
    path = Path(output_path) if output_path else Path("reports") / PREDICTION_HISTORY_FILE
    path.parent.mkdir(parents=True, exist_ok=True)

    new_row = pd.DataFrame([flatten_prediction_result(result)])
    if path.is_file():
        existing = pd.read_csv(path)
        combined = pd.concat([existing, new_row], ignore_index=True)
    else:
        combined = new_row

    combined.to_csv(path, index=False)
    return path


def save_latest_prediction_report(result: dict[str, Any], output_path: str | None = None) -> Path:
    """Save latest (single-row) prediction report."""
    path = Path(output_path) if output_path else Path("reports") / LATEST_PREDICTION_REPORT_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([flatten_prediction_result(result)]).to_csv(path, index=False)
    return path


def load_prediction_history(path: str | None = None) -> pd.DataFrame:
    """Load prediction history CSV if available; otherwise empty DataFrame."""
    csv_path = Path(path) if path else Path("reports") / PREDICTION_HISTORY_FILE
    if not csv_path.is_file():
        return pd.DataFrame()
    return pd.read_csv(csv_path)


def extract_prediction_explanation_features(result: dict[str, Any], top_n: int = 5) -> dict[str, Any]:
    """Return a compact top-N preview from feature preview in result payload."""
    preview = result.get("feature_preview", {}) or {}
    if not isinstance(preview, dict) or not preview:
        return {}
    keys = list(preview.keys())[: max(1, int(top_n))]
    return {k: preview.get(k) for k in keys}


def format_explanation_table_for_display(df: pd.DataFrame) -> pd.DataFrame:
    """Format explanation table for UI/API display readability."""
    if df is None or df.empty:
        return pd.DataFrame()

    out = df.copy()
    numeric_cols = out.select_dtypes(include=["number"]).columns.tolist()
    for col in numeric_cols:
        out[col] = out[col].round(4)

    sort_cols = [col for col in ["contribution", "shap_value", "importance"] if col in out.columns]
    if sort_cols:
        score_col = sort_cols[0]
        out["_abs_sort"] = out[score_col].abs()
        out = out.sort_values("_abs_sort", ascending=False).drop(columns=["_abs_sort"])

    return out.reset_index(drop=True)
