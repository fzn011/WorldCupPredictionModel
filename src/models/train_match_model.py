"""Baseline match-result model training for Step 5."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import joblib
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.models.evaluate_model import (
    classification_report_to_dataframe,
    choose_best_model,
    confusion_matrix_to_dataframe,
    evaluate_classifier,
)
from src.models.model_features import (
    load_feature_dataset,
    save_feature_columns,
    select_model_features,
)
from src.models.split_data import chronological_train_test_split, summarize_split
from src.utils.constants import (
    BASELINE_MODEL_DIR,
    BEST_BASELINE_MODEL_FILE,
    CLASSIFICATION_REPORT_DUMMY_FILE,
    CLASSIFICATION_REPORT_LOGISTIC_FILE,
    CLASSIFICATION_REPORT_RF_FILE,
    CONFUSION_MATRIX_DUMMY_FILE,
    CONFUSION_MATRIX_LOGISTIC_FILE,
    CONFUSION_MATRIX_RF_FILE,
    DEFAULT_TEST_START_DATE,
    DUMMY_MODEL_FILE,
    FEATURE_COLUMNS_FILE,
    FEATURE_IMPORTANCE_RF_FILE,
    LOGISTIC_REGRESSION_MODEL_FILE,
    MODEL_METADATA_FILE,
    MODEL_METRICS_FILE,
    RANDOM_SEED,
    RANDOM_FOREST_MODEL_FILE,
    TARGET_CLASS_ORDER,
)

# The reports directory already exists in the repo; keeping a local helper here
# avoids adding another global constant just for Step 5.
REPORTS_DIR = Path("reports")


def build_preprocessing_pipeline() -> Pipeline:
    """Return the preprocessing pipeline used by the Logistic Regression baseline."""
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )


def _build_dummy_model() -> Pipeline:
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("classifier", DummyClassifier(strategy="most_frequent")),
        ]
    )


def _build_logistic_model(random_state: int = RANDOM_SEED) -> Pipeline:
    return Pipeline(
        steps=[
            ("preprocess", build_preprocessing_pipeline()),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=random_state,
                ),
            ),
        ]
    )


def _build_random_forest_model(random_state: int = RANDOM_SEED) -> Pipeline:
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=300,
                    max_depth=None,
                    min_samples_leaf=2,
                    class_weight="balanced_subsample",
                    random_state=random_state,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def build_baseline_models(random_state: int = RANDOM_SEED) -> dict:
    """Build the baseline classifier objects used in Step 5."""
    return {
        "dummy": _build_dummy_model(),
        "logistic_regression": _build_logistic_model(random_state=random_state),
        "random_forest": _build_random_forest_model(random_state=random_state),
    }


def _align_test_features(
    test_df: pd.DataFrame,
    feature_columns: list[str],
) -> pd.DataFrame:
    """Align test columns to the training feature list, preserving order."""
    aligned = test_df.reindex(columns=feature_columns)
    return aligned


def get_random_forest_feature_importance(
    model,
    feature_columns: list[str],
) -> pd.DataFrame:
    """Extract feature importances from a fitted RandomForest pipeline."""
    classifier = None
    if hasattr(model, "named_steps"):
        classifier = model.named_steps.get("classifier")
    elif hasattr(model, "feature_importances_"):
        classifier = model

    if classifier is None or not hasattr(classifier, "feature_importances_"):
        return pd.DataFrame(columns=["feature", "importance"])

    importance = pd.DataFrame(
        {
            "feature": feature_columns,
            "importance": classifier.feature_importances_,
        }
    ).sort_values("importance", ascending=False)
    return importance.reset_index(drop=True)


def train_baseline_models(
    feature_df: pd.DataFrame | None = None,
    test_start_date: str = DEFAULT_TEST_START_DATE,
) -> dict:
    """Train the Step 5 baseline models and persist all artifacts."""
    if feature_df is None:
        feature_df = load_feature_dataset()

    train_df, test_df = chronological_train_test_split(
        feature_df,
        test_start_date=test_start_date,
    )
    split_summary = summarize_split(train_df, test_df)

    X_train, y_train, feature_columns = select_model_features(train_df)
    X_test_base, y_test, _ = select_model_features(test_df)
    X_test = _align_test_features(X_test_base, feature_columns)

    baseline_models = build_baseline_models()

    baseline_model_dir = Path(BASELINE_MODEL_DIR)
    baseline_model_dir.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    save_feature_columns(feature_columns, str(baseline_model_dir / FEATURE_COLUMNS_FILE))

    trained_models: dict[str, object] = {}
    metrics_rows: list[dict] = []

    for model_name, model in baseline_models.items():
        model.fit(X_train, y_train)
        trained_models[model_name] = model

        metrics = evaluate_classifier(
            model,
            X_test,
            y_test,
            model_name=model_name,
            class_order=TARGET_CLASS_ORDER,
        )
        metrics_rows.append(metrics)

        y_pred = model.predict(X_test)
        classification_report_to_dataframe(y_test, y_pred).to_csv(
            REPORTS_DIR
            / {
                "dummy": CLASSIFICATION_REPORT_DUMMY_FILE,
                "logistic_regression": CLASSIFICATION_REPORT_LOGISTIC_FILE,
                "random_forest": CLASSIFICATION_REPORT_RF_FILE,
            }[model_name],
            index=True,
        )
        confusion_matrix_to_dataframe(y_test, y_pred, TARGET_CLASS_ORDER).to_csv(
            REPORTS_DIR
            / {
                "dummy": CONFUSION_MATRIX_DUMMY_FILE,
                "logistic_regression": CONFUSION_MATRIX_LOGISTIC_FILE,
                "random_forest": CONFUSION_MATRIX_RF_FILE,
            }[model_name],
            index=True,
        )

        artifact_path = baseline_model_dir / {
            "dummy": DUMMY_MODEL_FILE,
            "logistic_regression": LOGISTIC_REGRESSION_MODEL_FILE,
            "random_forest": RANDOM_FOREST_MODEL_FILE,
        }[model_name]
        joblib.dump(model, artifact_path)

    metrics_df = pd.DataFrame(metrics_rows)
    metrics_path = REPORTS_DIR / MODEL_METRICS_FILE
    metrics_df.to_csv(metrics_path, index=False)

    best_model_name = choose_best_model(metrics_df)
    best_model_path = baseline_model_dir / BEST_BASELINE_MODEL_FILE
    shutil.copyfile(
        baseline_model_dir
        / {
            "dummy": DUMMY_MODEL_FILE,
            "logistic_regression": LOGISTIC_REGRESSION_MODEL_FILE,
            "random_forest": RANDOM_FOREST_MODEL_FILE,
        }[best_model_name],
        best_model_path,
    )

    rf_importance = get_random_forest_feature_importance(
        trained_models["random_forest"], feature_columns
    )
    if not rf_importance.empty:
        rf_importance.to_csv(REPORTS_DIR / FEATURE_IMPORTANCE_RF_FILE, index=False)

    metadata = {
        "status": "ok",
        "test_start_date": test_start_date,
        "train_rows": split_summary["train_rows"],
        "test_rows": split_summary["test_rows"],
        "feature_count": len(feature_columns),
        "best_model_name": best_model_name,
        "feature_columns_path": str(baseline_model_dir / FEATURE_COLUMNS_FILE),
        "best_model_path": str(best_model_path),
        "metrics_path": str(metrics_path),
        "class_order": TARGET_CLASS_ORDER,
    }
    (baseline_model_dir / MODEL_METADATA_FILE).write_text(
        json.dumps(metadata, indent=2)
    )

    return {
        "status": "ok",
        "train_rows": split_summary["train_rows"],
        "test_rows": split_summary["test_rows"],
        "feature_count": len(feature_columns),
        "model_metrics_path": str(metrics_path),
        "best_model_name": best_model_name,
        "best_model_path": str(best_model_path),
        "feature_columns_path": str(baseline_model_dir / FEATURE_COLUMNS_FILE),
        "split_summary": split_summary,
    }


if __name__ == "__main__":
    summary = train_baseline_models()
    print(summary)
