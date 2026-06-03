"""Step 6 improved model training pipeline."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.models.advanced_models import build_advanced_models
from src.models.backtesting import run_temporal_backtests
from src.models.calibration import (
    calibrate_fitted_model,
    create_calibration_report,
    create_probability_quality_report,
    split_train_calibration,
)
from src.models.evaluate_model import choose_best_model, evaluate_classifier
from src.models.model_features import (
    load_feature_dataset,
    save_feature_columns,
    select_model_features,
)
from src.models.split_data import chronological_train_test_split
import src.utils.constants as C

BASELINE_MODEL_DIR = getattr(C, "BASELINE_MODEL_DIR", "models/baseline")
RANDOM_FOREST_MODEL_FILE = getattr(C, "RANDOM_FOREST_MODEL_FILE", "random_forest.joblib")
MODEL_METRICS_FILE = getattr(C, "MODEL_METRICS_FILE", "model_metrics.csv")

IMPROVED_MODEL_DIR = getattr(C, "IMPROVED_MODEL_DIR", "models/improved")
XGBOOST_MODEL_FILE = getattr(C, "XGBOOST_MODEL_FILE", "xgboost_model.joblib")
LIGHTGBM_MODEL_FILE = getattr(C, "LIGHTGBM_MODEL_FILE", "lightgbm_model.joblib")
HIST_GRADIENT_BOOSTING_MODEL_FILE = getattr(
    C, "HIST_GRADIENT_BOOSTING_MODEL_FILE", "hist_gradient_boosting_model.joblib"
)
CALIBRATED_RANDOM_FOREST_FILE = getattr(C, "CALIBRATED_RANDOM_FOREST_FILE", "calibrated_random_forest.joblib")
CALIBRATED_XGBOOST_FILE = getattr(C, "CALIBRATED_XGBOOST_FILE", "calibrated_xgboost.joblib")
CALIBRATED_LIGHTGBM_FILE = getattr(C, "CALIBRATED_LIGHTGBM_FILE", "calibrated_lightgbm.joblib")
CALIBRATED_HIST_GB_FILE = getattr(
    C, "CALIBRATED_HIST_GB_FILE", "calibrated_hist_gradient_boosting.joblib"
)
BEST_IMPROVED_MODEL_FILE = getattr(C, "BEST_IMPROVED_MODEL_FILE", "best_improved_model.joblib")
IMPROVED_FEATURE_COLUMNS_FILE = getattr(C, "IMPROVED_FEATURE_COLUMNS_FILE", "improved_feature_columns.json")
IMPROVED_MODEL_METADATA_FILE = getattr(C, "IMPROVED_MODEL_METADATA_FILE", "improved_model_metadata.json")

IMPROVED_MODEL_METRICS_FILE = getattr(C, "IMPROVED_MODEL_METRICS_FILE", "improved_model_metrics.csv")
BASELINE_VS_IMPROVED_METRICS_FILE = getattr(
    C, "BASELINE_VS_IMPROVED_METRICS_FILE", "baseline_vs_improved_metrics.csv"
)
TEMPORAL_BACKTEST_RESULTS_FILE = getattr(C, "TEMPORAL_BACKTEST_RESULTS_FILE", "temporal_backtest_results.csv")
CALIBRATION_REPORT_FILE = getattr(C, "CALIBRATION_REPORT_FILE", "calibration_report.csv")
PROBABILITY_QUALITY_REPORT_FILE = getattr(C, "PROBABILITY_QUALITY_REPORT_FILE", "probability_quality_report.csv")
IMPROVED_FEATURE_IMPORTANCE_FILE = getattr(C, "IMPROVED_FEATURE_IMPORTANCE_FILE", "improved_feature_importance.csv")
MODEL_COMPARISON_SUMMARY_FILE = getattr(C, "MODEL_COMPARISON_SUMMARY_FILE", "model_comparison_summary.json")

DEFAULT_TEST_START_DATE = getattr(C, "DEFAULT_TEST_START_DATE", "2022-01-01")
RANDOM_SEED = getattr(C, "RANDOM_SEED", 42)
TARGET_COLUMN = getattr(C, "TARGET_COLUMN", "result")
TARGET_CLASS_ORDER = getattr(C, "TARGET_CLASS_ORDER", [0, 1, 2])
BACKTEST_WINDOWS = getattr(C, "BACKTEST_WINDOWS", [{"name": "test_2022_onward", "test_start_date": "2022-01-01"}])
DEFAULT_CALIBRATION_METHOD = getattr(C, "DEFAULT_CALIBRATION_METHOD", "sigmoid")

REPORTS_DIR = Path("reports")

MODEL_FILE_MAP = {
    "hist_gradient_boosting": HIST_GRADIENT_BOOSTING_MODEL_FILE,
    "xgboost": XGBOOST_MODEL_FILE,
    "lightgbm": LIGHTGBM_MODEL_FILE,
    "random_forest": RANDOM_FOREST_MODEL_FILE,
}

CALIBRATED_FILE_MAP = {
    "hist_gradient_boosting": CALIBRATED_HIST_GB_FILE,
    "xgboost": CALIBRATED_XGBOOST_FILE,
    "lightgbm": CALIBRATED_LIGHTGBM_FILE,
    "random_forest": CALIBRATED_RANDOM_FOREST_FILE,
}


def _align_X_y(df: pd.DataFrame, feature_columns: list[str]) -> tuple[pd.DataFrame, pd.Series]:
    y = pd.to_numeric(df[TARGET_COLUMN], errors="coerce")
    valid_mask = y.isin(TARGET_CLASS_ORDER)
    filtered = df.loc[valid_mask].copy()
    y = y.loc[valid_mask].astype(int).reset_index(drop=True)
    X = filtered.reindex(columns=feature_columns).reset_index(drop=True)
    return X, y


def _supports_predict_proba(model) -> bool:
    return hasattr(model, "predict_proba")


def _extract_feature_importance(model, feature_columns: list[str]) -> pd.DataFrame:
    classifier = getattr(model, "named_steps", {}).get("classifier") if hasattr(model, "named_steps") else model
    if classifier is None or not hasattr(classifier, "feature_importances_"):
        return pd.DataFrame(columns=["feature", "importance"])

    return (
        pd.DataFrame({"feature": feature_columns, "importance": classifier.feature_importances_})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )


def _is_calibration_better(base_metrics: dict, calibrated_metrics: dict) -> bool:
    base_log = base_metrics.get("log_loss")
    cal_log = calibrated_metrics.get("log_loss")
    base_brier = base_metrics.get("multiclass_brier_score")
    cal_brier = calibrated_metrics.get("multiclass_brier_score")

    better_log = pd.notna(cal_log) and (pd.isna(base_log) or float(cal_log) < float(base_log))
    better_brier = pd.notna(cal_brier) and (pd.isna(base_brier) or float(cal_brier) < float(base_brier))
    return bool(better_log or better_brier)


def train_improved_models(
    feature_df: pd.DataFrame | None = None,
    test_start_date: str = DEFAULT_TEST_START_DATE,
    random_state: int = RANDOM_SEED,
) -> dict:
    """Train Step 6 improved models and persist artifacts/reports."""
    if feature_df is None:
        feature_df = load_feature_dataset()

    train_df, test_df = chronological_train_test_split(feature_df, test_start_date=test_start_date)
    model_train_df, calibration_df = split_train_calibration(train_df, calibration_fraction=0.2)

    X_model_train, y_model_train, feature_columns = select_model_features(model_train_df)
    X_calibration, y_calibration = _align_X_y(calibration_df, feature_columns)
    X_test, y_test = _align_X_y(test_df, feature_columns)

    improved_dir = Path(IMPROVED_MODEL_DIR)
    improved_dir.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    save_feature_columns(feature_columns, str(improved_dir / IMPROVED_FEATURE_COLUMNS_FILE))

    model_builders = build_advanced_models(random_state=random_state)
    skipped_models: list[str] = []
    trained_models: list[str] = []

    fitted_models: dict[str, object] = {}
    metrics_rows: list[dict] = []
    calibration_rows: list[pd.DataFrame] = []

    for model_name, model in model_builders.items():
        if model is None:
            skipped_models.append(model_name)
            continue

        try:
            model.fit(X_model_train, y_model_train)
            fitted_models[model_name] = model
            trained_models.append(model_name)
            joblib.dump(model, improved_dir / MODEL_FILE_MAP[model_name])

            base_metrics = evaluate_classifier(
                model,
                X_test,
                y_test,
                model_name=model_name,
                class_order=TARGET_CLASS_ORDER,
            )
            base_metrics["model_group"] = "improved"
            base_metrics["is_calibrated"] = False
            base_metrics["eligible_for_best"] = True
            metrics_rows.append(base_metrics)

            if _supports_predict_proba(model):
                calibration_rows.append(
                    create_calibration_report(
                        model_name=model_name,
                        y_true=y_test,
                        y_proba=model.predict_proba(X_test),
                        class_order=TARGET_CLASS_ORDER,
                    )
                )

            calibrated_model, warning = calibrate_fitted_model(
                fitted_model=model,
                X_calibration=X_calibration,
                y_calibration=y_calibration,
                method=DEFAULT_CALIBRATION_METHOD,
            )
            calibrated_name = f"calibrated_{model_name}"

            if warning is None:
                joblib.dump(calibrated_model, improved_dir / CALIBRATED_FILE_MAP[model_name])
                calibrated_metrics = evaluate_classifier(
                    calibrated_model,
                    X_test,
                    y_test,
                    model_name=calibrated_name,
                    class_order=TARGET_CLASS_ORDER,
                )
                calibrated_metrics["model_group"] = "improved"
                calibrated_metrics["is_calibrated"] = True
                calibrated_metrics["eligible_for_best"] = _is_calibration_better(base_metrics, calibrated_metrics)
                metrics_rows.append(calibrated_metrics)

                if _supports_predict_proba(calibrated_model):
                    calibration_rows.append(
                        create_calibration_report(
                            model_name=calibrated_name,
                            y_true=y_test,
                            y_proba=calibrated_model.predict_proba(X_test),
                            class_order=TARGET_CLASS_ORDER,
                        )
                    )
            else:
                skipped_models.append(calibrated_name)
        except Exception as exc:
            skipped_models.append(f"{model_name} ({exc})")

    rf_path = Path(BASELINE_MODEL_DIR) / RANDOM_FOREST_MODEL_FILE
    if rf_path.is_file():
        try:
            baseline_rf = joblib.load(rf_path)
            calibrated_rf, warning = calibrate_fitted_model(
                fitted_model=baseline_rf,
                X_calibration=X_calibration,
                y_calibration=y_calibration,
                method=DEFAULT_CALIBRATION_METHOD,
            )
            if warning is None:
                joblib.dump(calibrated_rf, improved_dir / CALIBRATED_RANDOM_FOREST_FILE)
                rf_metrics = evaluate_classifier(
                    calibrated_rf,
                    X_test,
                    y_test,
                    model_name="calibrated_random_forest",
                    class_order=TARGET_CLASS_ORDER,
                )
                rf_metrics["model_group"] = "improved"
                rf_metrics["is_calibrated"] = True
                rf_metrics["eligible_for_best"] = True
                metrics_rows.append(rf_metrics)

                if _supports_predict_proba(calibrated_rf):
                    calibration_rows.append(
                        create_calibration_report(
                            model_name="calibrated_random_forest",
                            y_true=y_test,
                            y_proba=calibrated_rf.predict_proba(X_test),
                            class_order=TARGET_CLASS_ORDER,
                        )
                    )
            else:
                skipped_models.append("calibrated_random_forest")
        except Exception as exc:
            skipped_models.append(f"calibrated_random_forest ({exc})")
    else:
        skipped_models.append("calibrated_random_forest (baseline RF artifact missing)")

    metrics_df = pd.DataFrame(metrics_rows)
    improved_metrics_path = REPORTS_DIR / IMPROVED_MODEL_METRICS_FILE
    metrics_df.to_csv(improved_metrics_path, index=False)

    if "eligible_for_best" in metrics_df.columns:
        eligible_df = metrics_df.loc[metrics_df["eligible_for_best"] == True].copy()
    else:
        eligible_df = metrics_df.copy()
    if eligible_df.empty:
        eligible_df = metrics_df.copy()
    best_model_name = choose_best_model(eligible_df)

    best_source_path = None
    if best_model_name.startswith("calibrated_"):
        base_name = best_model_name.replace("calibrated_", "", 1)
        best_source_path = improved_dir / CALIBRATED_FILE_MAP.get(base_name, BEST_IMPROVED_MODEL_FILE)
    else:
        best_source_path = improved_dir / MODEL_FILE_MAP.get(best_model_name, BEST_IMPROVED_MODEL_FILE)

    best_output_path = improved_dir / BEST_IMPROVED_MODEL_FILE
    if best_source_path.is_file() and best_source_path != best_output_path:
        shutil.copyfile(best_source_path, best_output_path)

    baseline_metrics_path = REPORTS_DIR / MODEL_METRICS_FILE
    baseline_vs_improved_path = REPORTS_DIR / BASELINE_VS_IMPROVED_METRICS_FILE
    if baseline_metrics_path.is_file():
        baseline_df = pd.read_csv(baseline_metrics_path)
        baseline_df["model_group"] = "baseline"
        combined = pd.concat([baseline_df, metrics_df], ignore_index=True, sort=False)
        combined.to_csv(baseline_vs_improved_path, index=False)

    calibration_report_df = (
        pd.concat(calibration_rows, ignore_index=True, sort=False)
        if calibration_rows
        else pd.DataFrame(
            columns=[
                "model_name",
                "class_label",
                "mean_predicted_probability",
                "observed_frequency",
                "absolute_gap",
            ]
        )
    )
    calibration_report_path = REPORTS_DIR / CALIBRATION_REPORT_FILE
    calibration_report_df.to_csv(calibration_report_path, index=False)

    probability_quality_df = create_probability_quality_report(metrics_df)
    probability_quality_path = REPORTS_DIR / PROBABILITY_QUALITY_REPORT_FILE
    probability_quality_df.to_csv(probability_quality_path, index=False)

    backtest_builders = {
        "hist_gradient_boosting": lambda: build_advanced_models(random_state=random_state)["hist_gradient_boosting"],
    }
    if "xgboost" in model_builders:
        backtest_builders["xgboost"] = lambda: build_advanced_models(random_state=random_state).get("xgboost")
    if "lightgbm" in model_builders:
        backtest_builders["lightgbm"] = lambda: build_advanced_models(random_state=random_state).get("lightgbm")

    backtest_df = run_temporal_backtests(
        feature_df=feature_df,
        model_builders=backtest_builders,
        backtest_windows=BACKTEST_WINDOWS,
    )
    backtest_results_path = REPORTS_DIR / TEMPORAL_BACKTEST_RESULTS_FILE
    backtest_df.to_csv(backtest_results_path, index=False)

    importance_df = pd.DataFrame(columns=["feature", "importance"])
    for name in ("xgboost", "lightgbm", "hist_gradient_boosting"):
        model = fitted_models.get(name)
        if model is None:
            continue
        candidate = _extract_feature_importance(model, feature_columns)
        if not candidate.empty:
            candidate.insert(0, "model_name", name)
            importance_df = candidate
            break

    improved_feature_importance_path = REPORTS_DIR / IMPROVED_FEATURE_IMPORTANCE_FILE
    importance_df.to_csv(improved_feature_importance_path, index=False)

    comparison_summary = {
        "status": "ok",
        "best_model_name": best_model_name,
        "best_model_path": str(best_output_path),
        "trained_models": trained_models,
        "skipped_models": skipped_models,
        "train_rows": int(len(model_train_df)),
        "calibration_rows": int(len(calibration_df)),
        "test_rows": int(len(test_df)),
        "feature_count": int(len(feature_columns)),
    }
    model_comparison_summary_path = REPORTS_DIR / MODEL_COMPARISON_SUMMARY_FILE
    model_comparison_summary_path.write_text(json.dumps(comparison_summary, indent=2))

    metadata = {
        **comparison_summary,
        "test_start_date": test_start_date,
        "class_order": TARGET_CLASS_ORDER,
        "improved_metrics_path": str(improved_metrics_path),
        "baseline_vs_improved_path": str(baseline_vs_improved_path),
        "backtest_results_path": str(backtest_results_path),
        "probability_quality_report_path": str(probability_quality_path),
    }
    (improved_dir / IMPROVED_MODEL_METADATA_FILE).write_text(json.dumps(metadata, indent=2))

    return {
        "status": "ok",
        "train_rows": int(len(model_train_df)),
        "calibration_rows": int(len(calibration_df)),
        "test_rows": int(len(test_df)),
        "feature_count": int(len(feature_columns)),
        "trained_models": trained_models,
        "skipped_models": skipped_models,
        "best_model_name": best_model_name,
        "best_model_path": str(best_output_path),
        "improved_metrics_path": str(improved_metrics_path),
        "baseline_vs_improved_path": str(baseline_vs_improved_path),
        "backtest_results_path": str(backtest_results_path),
        "probability_quality_report_path": str(probability_quality_path),
    }


if __name__ == "__main__":
    summary = train_improved_models()
    print(summary)
