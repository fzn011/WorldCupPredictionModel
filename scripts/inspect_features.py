"""Inspect the Step 4 feature dataset and print a concise report."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

# Make `src` importable when running this script directly.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.constants import (  # noqa: E402
    FEATURE_DATASET_FILE,
    FEATURE_DATASET_SAMPLE_FILE,
    PROCESSED_DATA_DIR,
)


def _resolve_feature_path() -> Path | None:
    """Prefer the real feature dataset, then the sample fallback."""
    real_path = PROCESSED_DATA_DIR / FEATURE_DATASET_FILE
    sample_path = PROCESSED_DATA_DIR / FEATURE_DATASET_SAMPLE_FILE
    if real_path.is_file():
        return real_path
    if sample_path.is_file():
        return sample_path
    return None


def _warn_missing(df: pd.DataFrame, columns: list[str]) -> None:
    for column in columns:
        if column not in df.columns:
            print(f"[warn] Missing expected column: {column}")


def main() -> None:
    """Print a readable inspection report for the feature dataset."""
    feature_path = _resolve_feature_path()
    if feature_path is None:
        print(
            "No feature dataset found. Run `python main.py` first to build the Step 4 features."
        )
        return

    columns = pd.read_csv(feature_path, nrows=0).columns
    if "date" in columns:
        df = pd.read_csv(feature_path, parse_dates=["date"])
    else:
        df = pd.read_csv(feature_path)
    print("=" * 60)
    print(f"Feature dataset file: {feature_path}")
    print("=" * 60)
    print(f"Rows:    {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    if "date" in df.columns:
        date_series = pd.to_datetime(df["date"], errors="coerce")
        if date_series.notna().any():
            print(f"Date range: {date_series.min().date()} -> {date_series.max().date()}")
    else:
        print("[warn] No date column available.")

    if {"team_a", "team_b"}.issubset(df.columns):
        unique_teams = pd.unique(df[["team_a", "team_b"]].values.ravel("K"))
        print(f"Unique teams: {len(unique_teams)}")
    else:
        print("[warn] Cannot compute unique teams; team columns are missing.")

    if "result_label" in df.columns:
        print("\nResult distribution:")
        print(df["result_label"].value_counts().to_string())
    else:
        print("[warn] Missing result_label column.")

    print(f"\nMissing values total: {int(df.isna().sum().sum())}")
    print("\nTop 20 columns with missing values:")
    missing = df.isna().sum().sort_values(ascending=False).head(20)
    print(missing.to_string())

    numeric_feature_count = int(df.select_dtypes(include="number").shape[1])
    print(f"\nNumeric feature count: {numeric_feature_count}")

    print("\nSample feature rows:")
    print(df.head().to_string(index=False))

    key_columns = [
        "team_a_last_5_win_rate",
        "team_b_last_5_win_rate",
        "diff_last_5_win_rate",
        "team_a_points_per_match_before",
        "team_b_points_per_match_before",
        "diff_points_per_match_before",
    ]
    _warn_missing(df, key_columns)
    present = [column for column in key_columns if column in df.columns]
    if present:
        print("\nDescriptive statistics for key features:")
        print(df[present].describe().to_string())


if __name__ == "__main__":
    main()
