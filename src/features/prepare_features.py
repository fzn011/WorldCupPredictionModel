"""Preparation pipeline for Step 4 feature engineering."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.data.prepare_datasets import prepare_step3_clean_datasets
from src.features.build_features import (
    build_feature_dataset,
    create_feature_quality_report,
    create_feature_summary,
)
import src.utils.constants as C

CANONICAL_MATCHES_FILE = getattr(C, "CANONICAL_MATCHES_FILE", "canonical_matches.csv")
CANONICAL_MATCHES_SAMPLE_FILE = getattr(
    C, "CANONICAL_MATCHES_SAMPLE_FILE", "canonical_matches_sample.csv"
)
FEATURE_DATASET_FILE = getattr(C, "FEATURE_DATASET_FILE", "feature_dataset.csv")
FEATURE_DATASET_SAMPLE_FILE = getattr(
    C, "FEATURE_DATASET_SAMPLE_FILE", "feature_dataset_sample.csv"
)
FEATURE_QUALITY_REPORT_FILE = getattr(C, "FEATURE_QUALITY_REPORT_FILE", "feature_quality_report.csv")
FEATURE_SUMMARY_FILE = getattr(C, "FEATURE_SUMMARY_FILE", "feature_summary.json")
PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")


def _load_canonical_matches() -> tuple[pd.DataFrame, Path, bool]:
    """Load the preferred canonical dataset, falling back to the sample copy."""
    real_path = PROCESSED_DATA_DIR / CANONICAL_MATCHES_FILE
    sample_path = PROCESSED_DATA_DIR / CANONICAL_MATCHES_SAMPLE_FILE

    if real_path.is_file():
        return pd.read_csv(real_path, parse_dates=["date"]), real_path, True
    if sample_path.is_file():
        return pd.read_csv(sample_path, parse_dates=["date"]), sample_path, False

    prepare_step3_clean_datasets()
    if real_path.is_file():
        return pd.read_csv(real_path, parse_dates=["date"]), real_path, True
    if sample_path.is_file():
        return pd.read_csv(sample_path, parse_dates=["date"]), sample_path, False

    raise FileNotFoundError(
        "No canonical dataset could be found or generated."
    )


def prepare_step4_features(min_year: int = 1990) -> dict:
    """Build and save the Step 4 feature dataset.

    The function prefers real canonical matches, falls back to the sample copy,
    and only generates rows from ``min_year`` onward while still using older
    matches for history.
    """
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    canonical_df, canonical_path, used_real = _load_canonical_matches()
    feature_df = build_feature_dataset(canonical_df, min_year=min_year)
    quality_report_df = create_feature_quality_report(feature_df)
    summary = create_feature_summary(feature_df)

    feature_output_name = (
        FEATURE_DATASET_FILE if used_real else FEATURE_DATASET_SAMPLE_FILE
    )
    feature_output_path = PROCESSED_DATA_DIR / feature_output_name
    quality_report_path = PROCESSED_DATA_DIR / FEATURE_QUALITY_REPORT_FILE
    feature_summary_path = PROCESSED_DATA_DIR / FEATURE_SUMMARY_FILE

    feature_df.to_csv(feature_output_path, index=False)
    quality_report_df.to_csv(quality_report_path, index=False)
    feature_summary_path.write_text(json.dumps(summary, indent=2, default=str))

    result = {
        "status": summary["status"],
        "source_canonical_path": str(canonical_path),
        "feature_output_path": str(feature_output_path),
        "feature_rows": summary["rows"],
        "feature_columns": summary["columns"],
        "date_min": summary["date_min"],
        "date_max": summary["date_max"],
        "unique_teams": summary["unique_teams"],
        "missing_values_total": summary["missing_values_total"],
        "feature_quality_report_path": str(quality_report_path),
        "feature_summary_path": str(feature_summary_path),
    }
    return result


if __name__ == "__main__":
    summary = prepare_step4_features()
    print(summary)
