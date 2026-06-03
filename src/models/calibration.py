"""Probability calibration utilities for Step 6."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV


def split_train_calibration(
    train_df: pd.DataFrame,
    calibration_fraction: float = 0.2,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split a training frame chronologically into train/calibration slices."""
    if train_df is None or train_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    working = train_df.copy()
    if "date" in working.columns:
        working["date"] = pd.to_datetime(working["date"], errors="coerce")
        working = working.sort_values("date").reset_index(drop=True)

    n_rows = len(working)
    if n_rows < 5:
        split_idx = max(1, n_rows - 1)
    else:
        calibration_rows = max(1, int(round(n_rows * calibration_fraction)))
        split_idx = max(1, n_rows - calibration_rows)
        split_idx = min(split_idx, n_rows - 1)

    model_train_df = working.iloc[:split_idx].copy().reset_index(drop=True)
    calibration_df = working.iloc[split_idx:].copy().reset_index(drop=True)
    return model_train_df, calibration_df


def calibrate_fitted_model(
    fitted_model: Any,
    X_calibration: pd.DataFrame,
    y_calibration: pd.Series,
    method: str = "sigmoid",
):
    """Calibrate a fitted model and return (model, warning_or_none)."""
    if X_calibration is None or X_calibration.empty or y_calibration is None or y_calibration.empty:
        return fitted_model, "Calibration skipped: empty calibration dataset."

    try:
        calibrator = CalibratedClassifierCV(estimator=fitted_model, method=method, cv="prefit")
        calibrator.fit(X_calibration, y_calibration)
        return calibrator, None
    except Exception as exc:
        try:
            from sklearn.frozen import FrozenEstimator

            frozen = FrozenEstimator(fitted_model)
            calibrator = CalibratedClassifierCV(estimator=frozen, method=method, cv=None)
            calibrator.fit(X_calibration, y_calibration)
            return calibrator, None
        except Exception:
            return fitted_model, f"Calibration failed: {exc}"


def create_calibration_report(
    model_name: str,
    y_true: pd.Series,
    y_proba,
    class_order: list[int],
) -> pd.DataFrame:
    """Create per-class calibration summary statistics for one model."""
    y_true_arr = np.asarray(y_true)
    y_proba_arr = np.asarray(y_proba)

    rows: list[dict] = []
    for idx, cls in enumerate(class_order):
        mean_pred = float(np.mean(y_proba_arr[:, idx])) if y_proba_arr.size else 0.0
        observed = float(np.mean((y_true_arr == cls).astype(float))) if y_true_arr.size else 0.0
        rows.append(
            {
                "model_name": model_name,
                "class_label": int(cls),
                "mean_predicted_probability": mean_pred,
                "observed_frequency": observed,
                "absolute_gap": abs(mean_pred - observed),
            }
        )

    return pd.DataFrame(rows)


def create_probability_quality_report(metrics_df: pd.DataFrame) -> pd.DataFrame:
    """Rank models by probability quality (log loss first, then Brier)."""
    if metrics_df is None or metrics_df.empty:
        return pd.DataFrame(
            columns=["model_name", "log_loss", "multiclass_brier_score", "probability_quality_rank"]
        )

    required = ["model_name", "log_loss", "multiclass_brier_score"]
    available = metrics_df.copy()
    for col in required:
        if col not in available.columns:
            available[col] = np.nan

    ranked = available[required].copy()
    ranked["log_loss"] = pd.to_numeric(ranked["log_loss"], errors="coerce")
    ranked["multiclass_brier_score"] = pd.to_numeric(ranked["multiclass_brier_score"], errors="coerce")
    ranked = ranked.sort_values(["log_loss", "multiclass_brier_score"], ascending=[True, True]).reset_index(drop=True)
    ranked["probability_quality_rank"] = ranked.index + 1
    return ranked
