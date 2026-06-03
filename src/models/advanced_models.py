"""Advanced and optional model builders for Step 6."""

from __future__ import annotations

import importlib.util

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

import src.utils.constants as C

RANDOM_SEED = getattr(C, "RANDOM_SEED", 42)


def is_package_available(package_name: str) -> bool:
    """Return True when a package can be imported."""
    return importlib.util.find_spec(package_name) is not None


def build_hist_gradient_boosting_model(random_state: int = RANDOM_SEED):
    """Build the always-available sklearn HistGradientBoosting pipeline."""
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            (
                "classifier",
                HistGradientBoostingClassifier(
                    learning_rate=0.05,
                    max_iter=300,
                    l2_regularization=0.1,
                    random_state=random_state,
                ),
            ),
        ]
    )


def build_xgboost_model(random_state: int = RANDOM_SEED):
    """Build an optional XGBoost pipeline, or return None if unavailable."""
    if not is_package_available("xgboost"):
        return None

    try:
        from xgboost import XGBClassifier
    except Exception:
        return None

    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            (
                "classifier",
                XGBClassifier(
                    objective="multi:softprob",
                    num_class=3,
                    eval_metric="mlogloss",
                    n_estimators=300,
                    learning_rate=0.05,
                    max_depth=4,
                    subsample=0.9,
                    colsample_bytree=0.9,
                    random_state=random_state,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def build_lightgbm_model(random_state: int = RANDOM_SEED):
    """Build an optional LightGBM pipeline, or return None if unavailable."""
    if not is_package_available("lightgbm"):
        return None

    try:
        from lightgbm import LGBMClassifier
    except Exception:
        return None

    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            (
                "classifier",
                LGBMClassifier(
                    n_estimators=300,
                    learning_rate=0.05,
                    num_leaves=31,
                    subsample=0.9,
                    colsample_bytree=0.9,
                    objective="multiclass",
                    class_weight="balanced",
                    random_state=random_state,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def build_advanced_models(random_state: int = RANDOM_SEED) -> dict[str, object]:
    """Build Step 6 model set with graceful optional dependency handling."""
    models: dict[str, object] = {
        "hist_gradient_boosting": build_hist_gradient_boosting_model(random_state=random_state),
    }

    xgb_model = build_xgboost_model(random_state=random_state)
    if xgb_model is not None:
        models["xgboost"] = xgb_model
    else:
        print("[step6] xgboost unavailable; skipping XGBoost model.")

    lgbm_model = build_lightgbm_model(random_state=random_state)
    if lgbm_model is not None:
        models["lightgbm"] = lgbm_model
    else:
        print("[step6] lightgbm unavailable; skipping LightGBM model.")

    return models
