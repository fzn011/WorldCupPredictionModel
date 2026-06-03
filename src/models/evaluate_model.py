"""Model evaluation utilities for the Step 5 baseline models."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    log_loss,
)

from src.utils.constants import RESULT_LABELS, TARGET_CLASS_ORDER


def multiclass_brier_score(y_true, y_proba, classes: list[int]) -> float:
    """Compute the multiclass Brier score averaged across classes."""
    y_true = np.asarray(y_true)
    y_proba = np.asarray(y_proba)
    total = 0.0
    for idx, cls in enumerate(classes):
        y_one_hot = (y_true == cls).astype(float)
        total += np.mean((y_proba[:, idx] - y_one_hot) ** 2)
    return float(total / len(classes))


def evaluate_classifier(
    model,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    model_name: str,
    class_order: list[int] | None = None,
) -> dict:
    """Evaluate a classifier and return a metrics dictionary."""
    class_order = class_order or TARGET_CLASS_ORDER
    y_pred = model.predict(X_test)

    metrics = {
        "model_name": model_name,
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "macro_f1": float(f1_score(y_test, y_pred, average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(y_test, y_pred, average="weighted", zero_division=0)),
    }

    y_proba = None
    if hasattr(model, "predict_proba"):
        try:
            y_proba = model.predict_proba(X_test)
        except Exception:  # pragma: no cover - defensive
            y_proba = None

    if y_proba is not None:
        metrics["log_loss"] = float(log_loss(y_test, y_proba, labels=class_order))
        metrics["multiclass_brier_score"] = float(
            multiclass_brier_score(y_test, y_proba, class_order)
        )
    else:
        metrics["log_loss"] = np.nan
        metrics["multiclass_brier_score"] = np.nan

    return metrics


def classification_report_to_dataframe(y_true, y_pred) -> pd.DataFrame:
    """Convert sklearn's classification report to a DataFrame."""
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    return pd.DataFrame(report).T


def confusion_matrix_to_dataframe(
    y_true,
    y_pred,
    labels: list[int],
) -> pd.DataFrame:
    """Return a labeled confusion matrix DataFrame."""
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    names = [RESULT_LABELS[label] for label in labels]
    return pd.DataFrame(matrix, index=names, columns=names)


def choose_best_model(metrics_df: pd.DataFrame) -> str:
    """Pick the best model using log loss, falling back to macro F1."""
    if metrics_df.empty:
        raise ValueError("metrics_df is empty")

    if "log_loss" in metrics_df.columns and metrics_df["log_loss"].notna().any():
        best_row = metrics_df.loc[metrics_df["log_loss"].astype(float).idxmin()]
        return str(best_row["model_name"])

    if "macro_f1" in metrics_df.columns and metrics_df["macro_f1"].notna().any():
        best_row = metrics_df.loc[metrics_df["macro_f1"].astype(float).idxmax()]
        return str(best_row["model_name"])

    raise ValueError("metrics_df does not contain usable log_loss or macro_f1 values")
