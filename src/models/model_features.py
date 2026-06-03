"""Helpers for selecting safe model features from the Step 4 dataset."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.features.prepare_features import prepare_step4_features
from src.utils.constants import (
    FEATURE_DATASET_FILE,
    FEATURE_DATASET_SAMPLE_FILE,
    LEAKAGE_COLUMNS,
    NON_FEATURE_COLUMNS,
    PROCESSED_DATA_DIR,
    TARGET_CLASS_ORDER,
    TARGET_COLUMN,
)


def load_feature_dataset() -> pd.DataFrame:
    """Load the preferred feature dataset, falling back to the sample copy.

    If neither file exists, Step 4 is executed to generate the dataset.
    """
    real_path = PROCESSED_DATA_DIR / FEATURE_DATASET_FILE
    sample_path = PROCESSED_DATA_DIR / FEATURE_DATASET_SAMPLE_FILE

    if real_path.is_file():
        return pd.read_csv(real_path, parse_dates=["date"])
    if sample_path.is_file():
        return pd.read_csv(sample_path, parse_dates=["date"])

    # Generate Step 4 outputs if they are missing.
    prepare_step4_features()
    if real_path.is_file():
        return pd.read_csv(real_path, parse_dates=["date"])
    if sample_path.is_file():
        return pd.read_csv(sample_path, parse_dates=["date"])

    raise FileNotFoundError(
        "No feature dataset found. Run `python main.py` to generate Step 4 outputs."
    )


def get_leakage_columns() -> list[str]:
    """Return the columns that must not be used as model inputs."""
    return list(LEAKAGE_COLUMNS)


def get_non_feature_columns() -> list[str]:
    """Return the identity columns excluded from model inputs."""
    return list(NON_FEATURE_COLUMNS)


def select_model_features(
    df: pd.DataFrame,
    target_column: str = TARGET_COLUMN,
) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """Select leakage-safe numeric model features and the target column.

    The returned X contains only numeric and boolean columns, with entirely
    missing columns removed. Missing values are left as NaN for the pipeline
    imputer to handle later.
    """
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' is missing from the DataFrame.")

    working = df.copy()
    y = pd.to_numeric(working[target_column], errors="coerce")
    valid_mask = y.isin(TARGET_CLASS_ORDER)
    working = working.loc[valid_mask].copy()
    y = y.loc[valid_mask].astype(int)

    if working.empty or y.empty:
        raise ValueError("No rows with valid target classes 0, 1, 2 remain after filtering.")

    excluded = set(get_leakage_columns()) | set(get_non_feature_columns()) | {target_column}
    candidate = working[[column for column in working.columns if column not in excluded]]
    candidate = candidate.dropna(axis=1, how="all")

    feature_columns: list[str] = []
    for column in candidate.columns:
        dtype = candidate[column].dtype
        if pd.api.types.is_numeric_dtype(dtype) or pd.api.types.is_bool_dtype(dtype):
            feature_columns.append(column)

    if not feature_columns:
        raise ValueError("No numeric or boolean model features remain after filtering.")

    X = candidate[feature_columns].copy()
    X = X.reset_index(drop=True)
    y = y.reset_index(drop=True)
    return X, y, feature_columns


def save_feature_columns(feature_columns: list[str], output_path: str) -> None:
    """Save the selected feature column names as JSON."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(feature_columns, indent=2))


def load_feature_columns(path: str) -> list[str]:
    """Load a JSON feature-column list."""
    return json.loads(Path(path).read_text())
