"""Preparation pipeline for Step 7 ranking + Elo feature integration."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.data.load_data import load_elo_ratings, load_fifa_rankings
from src.features.prepare_features import prepare_step4_features
from src.features.ranking_features import (
    add_ranking_features_to_matches,
    build_team_strength_snapshot,
    create_ranking_feature_summary,
    create_ranking_merge_report,
)
import src.utils.constants as C

FEATURE_DATASET_FILE = getattr(C, "FEATURE_DATASET_FILE", "feature_dataset.csv")
FEATURE_DATASET_SAMPLE_FILE = getattr(C, "FEATURE_DATASET_SAMPLE_FILE", "feature_dataset_sample.csv")
PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")

RANKING_FEATURE_DATASET_FILE = getattr(C, "RANKING_FEATURE_DATASET_FILE", "ranking_feature_dataset.csv")
RANKING_FEATURE_DATASET_SAMPLE_FILE = getattr(
    C, "RANKING_FEATURE_DATASET_SAMPLE_FILE", "ranking_feature_dataset_sample.csv"
)
RANKING_MERGE_REPORT_FILE = getattr(C, "RANKING_MERGE_REPORT_FILE", "ranking_merge_report.csv")
RANKING_FEATURE_SUMMARY_FILE = getattr(C, "RANKING_FEATURE_SUMMARY_FILE", "ranking_feature_summary.json")
TEAM_STRENGTH_SNAPSHOT_FILE = getattr(C, "TEAM_STRENGTH_SNAPSHOT_FILE", "team_strength_snapshot.csv")

RANKING_SNAPSHOT_MODE = getattr(C, "RANKING_SNAPSHOT_MODE", "snapshot")


def _load_feature_dataset_for_step7() -> tuple[pd.DataFrame, Path, bool]:
    real_path = PROCESSED_DATA_DIR / FEATURE_DATASET_FILE
    sample_path = PROCESSED_DATA_DIR / FEATURE_DATASET_SAMPLE_FILE

    if real_path.is_file():
        return pd.read_csv(real_path, parse_dates=["date"]), real_path, True
    if sample_path.is_file():
        return pd.read_csv(sample_path, parse_dates=["date"]), sample_path, False

    prepare_step4_features()
    if real_path.is_file():
        return pd.read_csv(real_path, parse_dates=["date"]), real_path, True
    if sample_path.is_file():
        return pd.read_csv(sample_path, parse_dates=["date"]), sample_path, False

    raise FileNotFoundError("No Step 4 feature dataset could be loaded or generated.")


def prepare_step7_ranking_features(mode: str = RANKING_SNAPSHOT_MODE) -> dict:
    """Build ranking-enhanced match features and save Step 7 artifacts."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    feature_df, source_feature_path, source_is_real = _load_feature_dataset_for_step7()
    fifa_df = load_fifa_rankings()
    elo_df = load_elo_ratings()

    team_strength_df = build_team_strength_snapshot(fifa_df=fifa_df, elo_df=elo_df)
    ranking_feature_df = add_ranking_features_to_matches(feature_df=feature_df, team_strength_df=team_strength_df)

    merge_report_df = create_ranking_merge_report(ranking_feature_df)
    summary = create_ranking_feature_summary(ranking_feature_df, mode=mode)

    ranking_output_name = (
        RANKING_FEATURE_DATASET_FILE if source_is_real else RANKING_FEATURE_DATASET_SAMPLE_FILE
    )
    ranking_output_path = PROCESSED_DATA_DIR / ranking_output_name
    merge_report_path = PROCESSED_DATA_DIR / RANKING_MERGE_REPORT_FILE
    team_strength_path = PROCESSED_DATA_DIR / TEAM_STRENGTH_SNAPSHOT_FILE
    summary_path = PROCESSED_DATA_DIR / RANKING_FEATURE_SUMMARY_FILE

    ranking_feature_df.to_csv(ranking_output_path, index=False)
    team_strength_df.to_csv(team_strength_path, index=False)
    merge_report_df.to_csv(merge_report_path, index=False)
    summary_path.write_text(json.dumps(summary, indent=2, default=str))

    return {
        "status": summary.get("status", "ok"),
        "mode": mode,
        "source_feature_path": str(source_feature_path),
        "output_path": str(ranking_output_path),
        "rows": int(summary.get("rows", len(ranking_feature_df))),
        "columns": int(summary.get("columns", len(ranking_feature_df.columns))),
        "unique_teams": int(summary.get("unique_teams", 0)),
        "team_strength_rows": int(len(team_strength_df)),
        "ranking_merge_report_path": str(merge_report_path),
        "team_strength_snapshot_path": str(team_strength_path),
        "notes": summary.get("notes", []),
    }


if __name__ == "__main__":
    summary = prepare_step7_ranking_features()
    print(summary)
