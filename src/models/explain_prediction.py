"""Local prediction explainability utilities for future match predictions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.models.predict_match import (
    load_best_available_feature_columns,
    load_best_available_model,
    predict_future_match,
)
from src.models.prediction_utils import (
    format_explanation_table_for_display,
    get_prediction_confidence,
)
import src.utils.constants as C

READABLE_FEATURE_NAMES = getattr(C, "READABLE_FEATURE_NAMES", {})
TOP_EXPLANATION_FEATURES = getattr(C, "TOP_EXPLANATION_FEATURES", 10)
EXPLANATION_METHOD_SHAP = getattr(C, "EXPLANATION_METHOD_SHAP", "shap")
EXPLANATION_METHOD_PERMUTATION = getattr(C, "EXPLANATION_METHOD_PERMUTATION", "permutation")
EXPLANATION_METHOD_FEATURE_IMPORTANCE = getattr(C, "EXPLANATION_METHOD_FEATURE_IMPORTANCE", "feature_importance")
EXPLANATION_METHOD_FALLBACK = getattr(C, "EXPLANATION_METHOD_FALLBACK", "fallback")
EXPLANATION_REPORT_FILE = getattr(C, "EXPLANATION_REPORT_FILE", "prediction_explanation_report.csv")
EXPLANATION_HISTORY_FILE = getattr(C, "EXPLANATION_HISTORY_FILE", "prediction_explanation_history.csv")

RESULT_LABEL_TO_CLASS = {"team_a_loss": 0, "draw": 1, "team_a_win": 2}


def is_shap_available() -> bool:
    """Return True when SHAP can be imported, False otherwise."""
    try:
        import shap  # noqa: F401

        return True
    except Exception:
        return False


def load_best_model_and_features_for_explanation() -> tuple[Any, str, list[str]]:
    """Load best available model and its feature-column list."""
    model, model_type = load_best_available_model(prefer_ranking=True, prefer_improved=True)
    feature_columns = load_best_available_feature_columns(prefer_ranking=True, prefer_improved=True)
    return model, model_type, feature_columns


def align_feature_row_for_explanation(feature_row: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    """Align one-row feature DataFrame to model training columns in exact order."""
    if feature_row is None or feature_row.empty:
        raise ValueError("feature_row must be a non-empty DataFrame.")

    row = feature_row.iloc[[0]].copy()
    for col in feature_columns:
        if col not in row.columns:
            row[col] = np.nan

    aligned = row.reindex(columns=feature_columns)
    return aligned


def _readable_name(feature: str) -> str:
    return READABLE_FEATURE_NAMES.get(feature, feature.replace("_", " ").strip().title())


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def get_model_probability_change_explanation(
    model,
    X_row: pd.DataFrame,
    feature_columns: list[str],
    target_class_index: int,
    top_n: int = 10,
) -> pd.DataFrame:
    """Model-agnostic local sensitivity explanation using per-feature perturbation."""
    if not hasattr(model, "predict_proba"):
        raise ValueError("Model does not expose predict_proba for probability-change explanation.")

    aligned = align_feature_row_for_explanation(X_row, feature_columns)
    original_proba = model.predict_proba(aligned)[0]

    class_position = list(model.classes_).index(target_class_index)
    original_target_probability = _safe_float(original_proba[class_position])

    rows: list[dict[str, Any]] = []
    for feature in feature_columns:
        value = aligned.iloc[0][feature]
        numeric_value = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]

        perturbed = aligned.copy()
        if pd.notna(numeric_value):
            neutral_value = 0.0
        else:
            neutral_value = np.nan

        perturbed.at[aligned.index[0], feature] = neutral_value

        try:
            new_proba = model.predict_proba(perturbed)[0]
            new_target_probability = _safe_float(new_proba[class_position])
            contribution = original_target_probability - new_target_probability
        except Exception:
            contribution = 0.0

        direction = "supports" if contribution > 0 else "opposes" if contribution < 0 else "neutral"
        rows.append(
            {
                "feature": feature,
                "readable_feature": _readable_name(feature),
                "feature_value": value,
                "contribution": contribution,
                "direction": direction,
                "method": EXPLANATION_METHOD_PERMUTATION,
            }
        )

    explanation_df = pd.DataFrame(rows)
    if explanation_df.empty:
        return explanation_df

    explanation_df = explanation_df.sort_values("contribution", ascending=False)
    return explanation_df.head(max(1, int(top_n))).reset_index(drop=True)


def _shap_local_explanation(
    model,
    X_row: pd.DataFrame,
    feature_columns: list[str],
    target_class_index: int,
    top_n: int,
) -> pd.DataFrame:
    import shap

    aligned = align_feature_row_for_explanation(X_row, feature_columns)
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(aligned)

    if isinstance(shap_values, list):
        class_position = list(model.classes_).index(target_class_index)
        values = np.asarray(shap_values[class_position])[0]
    else:
        values_array = np.asarray(shap_values)
        if values_array.ndim == 3:
            class_position = list(model.classes_).index(target_class_index)
            values = values_array[0, :, class_position]
        elif values_array.ndim == 2:
            values = values_array[0]
        else:
            values = np.zeros(len(feature_columns), dtype=float)

    rows = []
    for idx, feature in enumerate(feature_columns):
        value = values[idx] if idx < len(values) else 0.0
        direction = "supports" if value > 0 else "opposes" if value < 0 else "neutral"
        rows.append(
            {
                "feature": feature,
                "readable_feature": _readable_name(feature),
                "feature_value": aligned.iloc[0][feature],
                "shap_value": float(value),
                "contribution": float(value),
                "direction": direction,
                "method": EXPLANATION_METHOD_SHAP,
            }
        )

    explanation_df = pd.DataFrame(rows)
    explanation_df = explanation_df.sort_values("shap_value", ascending=False)
    return explanation_df.head(max(1, int(top_n))).reset_index(drop=True)


def _feature_importance_fallback(model, X_row: pd.DataFrame, feature_columns: list[str], top_n: int) -> pd.DataFrame:
    if not hasattr(model, "feature_importances_"):
        return pd.DataFrame()

    aligned = align_feature_row_for_explanation(X_row, feature_columns)
    importances = np.asarray(getattr(model, "feature_importances_", np.zeros(len(feature_columns))))

    rows: list[dict[str, Any]] = []
    for idx, feature in enumerate(feature_columns):
        importance = float(importances[idx]) if idx < len(importances) else 0.0
        rows.append(
            {
                "feature": feature,
                "readable_feature": _readable_name(feature),
                "feature_value": aligned.iloc[0][feature],
                "importance": importance,
                "contribution": importance,
                "direction": "supports" if importance > 0 else "neutral",
                "method": EXPLANATION_METHOD_FEATURE_IMPORTANCE,
            }
        )

    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out = out.sort_values("importance", ascending=False)
    return out.head(max(1, int(top_n))).reset_index(drop=True)


def create_natural_language_explanation(
    explanation_df: pd.DataFrame,
    prediction_payload: dict[str, Any],
    max_points: int = 3,
) -> str:
    """Generate an honest, concise explanation sentence block from local factors."""
    if explanation_df is None or explanation_df.empty:
        return (
            "The model appears to favor this outcome based on the available pre-match signals. "
            "This is an analytics estimate, not a certainty."
        )

    top_support = explanation_df.loc[explanation_df["direction"] == "supports"].head(max_points)
    top_oppose = explanation_df.loc[explanation_df["direction"] == "opposes"].head(max_points)

    predicted_label = prediction_payload.get("predicted_label", "the predicted outcome")
    confidence_label, confidence_score = get_prediction_confidence(prediction_payload.get("probabilities", {}))

    support_bits = [str(row["readable_feature"]) for _, row in top_support.iterrows()]
    oppose_bits = [str(row["readable_feature"]) for _, row in top_oppose.iterrows()]

    lines = [
        (
            f"The model appears to favor '{predicted_label}' with {confidence_label.lower()} confidence "
            f"({confidence_score:.3f} max probability)."
        )
    ]

    if support_bits:
        lines.append("The strongest available signals are: " + ", ".join(support_bits) + ".")
    if oppose_bits:
        lines.append("Signals pulling in the opposite direction include: " + ", ".join(oppose_bits) + ".")

    lines.append("This is an analytics estimate, not a certainty.")
    return " ".join(lines)


def explain_future_match_prediction(
    team_a: str,
    team_b: str,
    match_date: str,
    tournament: str,
    city: str,
    country: str,
    neutral: int,
    top_n: int = TOP_EXPLANATION_FEATURES,
) -> dict[str, Any]:
    """Generate prediction + local explanation for one future match."""
    prediction = predict_future_match(
        team_a=team_a,
        team_b=team_b,
        match_date=match_date,
        tournament=tournament,
        city=city,
        country=country,
        neutral=neutral,
    )

    model, model_type, feature_columns = load_best_model_and_features_for_explanation()
    X_row = align_feature_row_for_explanation(prediction["feature_row"], feature_columns)

    target_class_index = RESULT_LABEL_TO_CLASS.get(prediction.get("predicted_label", "draw"), 1)

    explanation_df = pd.DataFrame()
    method = EXPLANATION_METHOD_FALLBACK

    if is_shap_available():
        try:
            explanation_df = _shap_local_explanation(
                model=model,
                X_row=X_row,
                feature_columns=feature_columns,
                target_class_index=target_class_index,
                top_n=top_n,
            )
            method = EXPLANATION_METHOD_SHAP
        except Exception:
            explanation_df = pd.DataFrame()

    if explanation_df.empty:
        try:
            explanation_df = get_model_probability_change_explanation(
                model=model,
                X_row=X_row,
                feature_columns=feature_columns,
                target_class_index=target_class_index,
                top_n=top_n,
            )
            method = EXPLANATION_METHOD_PERMUTATION
        except Exception:
            explanation_df = pd.DataFrame()

    if explanation_df.empty:
        explanation_df = _feature_importance_fallback(model, X_row, feature_columns, top_n=top_n)
        if not explanation_df.empty:
            method = EXPLANATION_METHOD_FEATURE_IMPORTANCE

    if explanation_df.empty:
        explanation_df = pd.DataFrame(
            columns=["feature", "readable_feature", "feature_value", "contribution", "direction", "method"]
        )
        method = EXPLANATION_METHOD_FALLBACK

    explanation_df["method"] = method
    explanation_df = format_explanation_table_for_display(explanation_df)

    supporting = explanation_df.loc[explanation_df["direction"] == "supports"].head(max(1, top_n // 2)).copy()
    opposing = explanation_df.loc[explanation_df["direction"] == "opposes"].head(max(1, top_n // 2)).copy()

    natural_language = create_natural_language_explanation(explanation_df, prediction)

    result = {
        "team_a": prediction.get("team_a", team_a),
        "team_b": prediction.get("team_b", team_b),
        "match_date": prediction.get("match_date", match_date),
        "prediction": {k: v for k, v in prediction.items() if k != "feature_row"},
        "explanation_method": method,
        "explanation_table": explanation_df,
        "top_supporting_factors": supporting,
        "top_opposing_factors": opposing,
        "natural_language_explanation": natural_language,
    }

    report_path = save_explanation_report(result)
    result["report_path"] = str(report_path)
    return result


def save_explanation_report(explanation_result: dict[str, Any], output_path: str | None = None) -> Path:
    """Save local explanation table and append summary history row."""
    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    table_path = Path(output_path) if output_path else reports_dir / EXPLANATION_REPORT_FILE
    table_df = explanation_result.get("explanation_table", pd.DataFrame())
    if isinstance(table_df, pd.DataFrame):
        table_df.to_csv(table_path, index=False)

    history_path = reports_dir / EXPLANATION_HISTORY_FILE
    prediction = explanation_result.get("prediction", {}) or {}

    support = explanation_result.get("top_supporting_factors", pd.DataFrame())
    oppose = explanation_result.get("top_opposing_factors", pd.DataFrame())

    support_names = []
    if isinstance(support, pd.DataFrame) and not support.empty:
        support_names = support.get("readable_feature", pd.Series(dtype=object)).astype(str).head(3).tolist()

    oppose_names = []
    if isinstance(oppose, pd.DataFrame) and not oppose.empty:
        oppose_names = oppose.get("readable_feature", pd.Series(dtype=object)).astype(str).head(3).tolist()

    summary_row = pd.DataFrame(
        [
            {
                "team_a": explanation_result.get("team_a"),
                "team_b": explanation_result.get("team_b"),
                "match_date": explanation_result.get("match_date"),
                "predicted_label": prediction.get("predicted_label"),
                "model_type": prediction.get("model_type"),
                "explanation_method": explanation_result.get("explanation_method"),
                "top_supporting_factors": " | ".join(support_names),
                "top_opposing_factors": " | ".join(oppose_names),
            }
        ]
    )

    if history_path.is_file():
        existing = pd.read_csv(history_path)
        summary = pd.concat([existing, summary_row], ignore_index=True)
    else:
        summary = summary_row

    summary.to_csv(history_path, index=False)
    return table_path
