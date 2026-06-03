"""Step 7 ranking-enhanced model training pipeline."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import joblib
import pandas as pd

from src.features.prepare_ranking_features import prepare_step7_ranking_features
from src.models.advanced_models import build_advanced_models
from src.models.evaluate_model import choose_best_model, evaluate_classifier
from src.models.model_features import save_feature_columns, select_model_features
from src.models.split_data import chronological_train_test_split
import src.utils.constants as C

PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")
REPORTS_DIR = Path("reports")

RANKING_FEATURE_DATASET_FILE = getattr(C, "RANKING_FEATURE_DATASET_FILE", "ranking_feature_dataset.csv")
RANKING_FEATURE_DATASET_SAMPLE_FILE = getattr(
    C, "RANKING_FEATURE_DATASET_SAMPLE_FILE", "ranking_feature_dataset_sample.csv"
)

RANKING_ENHANCED_MODEL_DIR = getattr(C, "RANKING_ENHANCED_MODEL_DIR", "models/ranking_enhanced")
RANKING_ENHANCED_MODEL_FILE = getattr(C, "RANKING_ENHANCED_MODEL_FILE", "ranking_enhanced_model.joblib")
BEST_RANKING_ENHANCED_MODEL_FILE = getattr(
    C, "BEST_RANKING_ENHANCED_MODEL_FILE", "best_ranking_enhanced_model.joblib"
)
RANKING_FEATURE_COLUMNS_FILE = getattr(C, "RANKING_FEATURE_COLUMNS_FILE", "ranking_feature_columns.json")
RANKING_MODEL_METADATA_FILE = getattr(C, "RANKING_MODEL_METADATA_FILE", "ranking_model_metadata.json")

RANKING_ENHANCED_MODEL_METRICS_FILE = getattr(
    C, "RANKING_ENHANCED_MODEL_METRICS_FILE", "ranking_enhanced_model_metrics.csv"
)
RANKING_VS_PREVIOUS_METRICS_FILE = getattr(C, "RANKING_VS_PREVIOUS_METRICS_FILE", "ranking_vs_previous_metrics.csv")
RANKING_FEATURE_IMPORTANCE_FILE = getattr(C, "RANKING_FEATURE_IMPORTANCE_FILE", "ranking_feature_importance.csv")
RANKING_MODEL_SUMMARY_FILE = getattr(C, "RANKING_MODEL_SUMMARY_FILE", "ranking_model_summary.json")

IMPROVED_MODEL_METRICS_FILE = getattr(C, "IMPROVED_MODEL_METRICS_FILE", "improved_model_metrics.csv")
DEFAULT_TEST_START_DATE = getattr(C, "DEFAULT_TEST_START_DATE", "2022-01-01")
RANDOM_SEED = getattr(C, "RANDOM_SEED", 42)
TARGET_CLASS_ORDER = getattr(C, "TARGET_CLASS_ORDER", [0, 1, 2])

MODEL_FILE_MAP = {
    "hist_gradient_boosting": "hist_gradient_boosting",
    "xgboost": "xgboost",
    "lightgbm": "lightgbm",
}


def _load_ranking_feature_dataset() -> tuple[pd.DataFrame, Path]:
    real_path = PROCESSED_DATA_DIR / RANKING_FEATURE_DATASET_FILE
    sample_path = PROCESSED_DATA_DIR / RANKING_FEATURE_DATASET_SAMPLE_FILE

    if real_path.is_file():
        return pd.read_csv(real_path, parse_dates=["date"]), real_path
    if sample_path.is_file():
        return pd.read_csv(sample_path, parse_dates=["date"]), sample_path

    prepare_step7_ranking_features()
    if real_path.is_file():
        return pd.read_csv(real_path, parse_dates=["date"]), real_path
    if sample_path.is_file():
        return pd.read_csv(sample_path, parse_dates=["date"]), sample_path

    raise FileNotFoundError("No Step 7 ranking feature dataset could be loaded or generated.")


def _align_test_features(test_df: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    return test_df.reindex(columns=feature_columns)


def _extract_feature_importance(model, feature_columns: list[str]) -> pd.DataFrame:
    classifier = getattr(model, "named_steps", {}).get("classifier") if hasattr(model, "named_steps") else model
    if classifier is None or not hasattr(classifier, "feature_importances_"):
        return pd.DataFrame(columns=["feature", "importance"])
    return (
        pd.DataFrame({"feature": feature_columns, "importance": classifier.feature_importances_})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )


def train_ranking_enhanced_model(
    ranking_feature_df: pd.DataFrame | None = None,
    test_start_date: str = DEFAULT_TEST_START_DATE,
    random_state: int = RANDOM_SEED,
) -> dict:
    """Train Step 7 ranking-enhanced models and persist outputs."""
    if ranking_feature_df is None:
        ranking_feature_df, ranking_source_path = _load_ranking_feature_dataset()
    else:
        ranking_source_path = Path("in_memory")

    train_df, test_df = chronological_train_test_split(ranking_feature_df, test_start_date=test_start_date)
    X_train, y_train, feature_columns = select_model_features(train_df)
    X_test_base, y_test, _ = select_model_features(test_df)
    X_test = _align_test_features(X_test_base, feature_columns)

    ranking_model_dir = Path(RANKING_ENHANCED_MODEL_DIR)
    ranking_model_dir.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    save_feature_columns(feature_columns, str(ranking_model_dir / RANKING_FEATURE_COLUMNS_FILE))

    models = build_advanced_models(random_state=random_state)
    trained_models: list[str] = []
    skipped_models: list[str] = []
    metrics_rows: list[dict] = []
    fitted_models: dict[str, object] = {}

    for model_name, model in models.items():
        if model is None:
            skipped_models.append(model_name)
            continue
        try:
            model.fit(X_train, y_train)
            trained_models.append(model_name)
            fitted_models[model_name] = model
            metrics = evaluate_classifier(
                model,
                X_test,
                y_test,
                model_name=model_name,
                class_order=TARGET_CLASS_ORDER,
            )
            metrics_rows.append(metrics)
        except Exception as exc:
            skipped_models.append(f"{model_name} ({exc})")

    metrics_df = pd.DataFrame(metrics_rows)
    ranking_metrics_path = REPORTS_DIR / RANKING_ENHANCED_MODEL_METRICS_FILE
    metrics_df.to_csv(ranking_metrics_path, index=False)

    best_model_name = choose_best_model(metrics_df)
    best_model = fitted_models[best_model_name]
    ranking_model_path = ranking_model_dir / RANKING_ENHANCED_MODEL_FILE
    best_model_path = ranking_model_dir / BEST_RANKING_ENHANCED_MODEL_FILE
    joblib.dump(best_model, ranking_model_path)
    shutil.copyfile(ranking_model_path, best_model_path)

    ranking_vs_previous_path = REPORTS_DIR / RANKING_VS_PREVIOUS_METRICS_FILE
    previous_path = REPORTS_DIR / IMPROVED_MODEL_METRICS_FILE
    if previous_path.is_file():
        previous_df = pd.read_csv(previous_path)
        previous_df["model_group"] = "previous_improved"
        now_df = metrics_df.copy()
        now_df["model_group"] = "ranking_enhanced"
        pd.concat([previous_df, now_df], ignore_index=True, sort=False).to_csv(
            ranking_vs_previous_path, index=False
        )

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

    ranking_feature_importance_path = REPORTS_DIR / RANKING_FEATURE_IMPORTANCE_FILE
    importance_df.to_csv(ranking_feature_importance_path, index=False)

    limitation_note = (
        "Snapshot ranking experiment: latest available FIFA/Elo tables are applied across historical rows. "
        "For strict historical backtesting, add date-aware historical ranking joins in a later refinement."
    )

    metadata = {
        "status": "ok",
        "source_feature_path": str(ranking_source_path),
        "test_start_date": test_start_date,
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "feature_count": int(len(feature_columns)),
        "trained_models": trained_models,
        "skipped_models": skipped_models,
        "best_model_name": best_model_name,
        "best_model_path": str(best_model_path),
        "ranking_metrics_path": str(ranking_metrics_path),
        "ranking_vs_previous_path": str(ranking_vs_previous_path),
        "notes": [limitation_note],
    }

    (ranking_model_dir / RANKING_MODEL_METADATA_FILE).write_text(json.dumps(metadata, indent=2))
    (REPORTS_DIR / RANKING_MODEL_SUMMARY_FILE).write_text(json.dumps(metadata, indent=2))

    return {
        "status": "ok",
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "feature_count": int(len(feature_columns)),
        "trained_models": trained_models,
        "skipped_models": skipped_models,
        "best_model_name": best_model_name,
        "best_model_path": str(best_model_path),
        "ranking_metrics_path": str(ranking_metrics_path),
        "ranking_vs_previous_path": str(ranking_vs_previous_path),
        "notes": [limitation_note],
    }


if __name__ == "__main__":
    summary = train_ranking_enhanced_model()
    print(summary)
