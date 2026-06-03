"""Inspect Step 7 ranking-enhanced feature artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import src.utils.constants as C  # noqa: E402

PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")
RANKING_FEATURE_DATASET_FILE = getattr(C, "RANKING_FEATURE_DATASET_FILE", "ranking_feature_dataset.csv")
RANKING_FEATURE_DATASET_SAMPLE_FILE = getattr(
    C, "RANKING_FEATURE_DATASET_SAMPLE_FILE", "ranking_feature_dataset_sample.csv"
)
TEAM_STRENGTH_SNAPSHOT_FILE = getattr(C, "TEAM_STRENGTH_SNAPSHOT_FILE", "team_strength_snapshot.csv")
RANKING_MERGE_REPORT_FILE = getattr(C, "RANKING_MERGE_REPORT_FILE", "ranking_merge_report.csv")


def main() -> None:
    ranking_real = PROCESSED_DATA_DIR / RANKING_FEATURE_DATASET_FILE
    ranking_sample = PROCESSED_DATA_DIR / RANKING_FEATURE_DATASET_SAMPLE_FILE
    dataset_path = ranking_real if ranking_real.is_file() else ranking_sample

    if not dataset_path.is_file():
        print("No Step 7 ranking dataset found. Run `python scripts/prepare_ranking_features.py` first.")
        return

    df = pd.read_csv(dataset_path, parse_dates=["date"])
    print("=== Ranking Feature Dataset Overview ===")
    print(f"Path: {dataset_path}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    if "date" in df.columns and not df.empty:
        print(f"Date range: {df['date'].min()} -> {df['date'].max()}")
    if {"team_a", "team_b"}.issubset(df.columns):
        print(f"Unique teams: {len(pd.unique(df[['team_a', 'team_b']].values.ravel('K')))}")

    ranking_cols = [
        "team_a_fifa_rank", "team_b_fifa_rank", "diff_fifa_rank",
        "team_a_fifa_points", "team_b_fifa_points", "diff_fifa_points",
        "team_a_elo", "team_b_elo", "diff_elo",
        "team_a_strength_score", "team_b_strength_score", "diff_strength_score",
    ]
    present_ranking_cols = [c for c in ranking_cols if c in df.columns]
    print(f"Ranking feature columns present: {present_ranking_cols}")

    missing_a_rank = int(df.get("team_a_fifa_rank", pd.Series(dtype=float)).isna().sum())
    missing_b_rank = int(df.get("team_b_fifa_rank", pd.Series(dtype=float)).isna().sum())
    missing_a_elo = int(df.get("team_a_elo", pd.Series(dtype=float)).isna().sum())
    missing_b_elo = int(df.get("team_b_elo", pd.Series(dtype=float)).isna().sum())
    print(f"Missing team_a_fifa_rank: {missing_a_rank}")
    print(f"Missing team_b_fifa_rank: {missing_b_rank}")
    print(f"Missing team_a_elo: {missing_a_elo}")
    print(f"Missing team_b_elo: {missing_b_elo}")

    strength_path = PROCESSED_DATA_DIR / TEAM_STRENGTH_SNAPSHOT_FILE
    if strength_path.is_file():
        strength_df = pd.read_csv(strength_path)
        print("\n=== Team Strength Snapshot (Top 20) ===")
        print(
            strength_df.sort_values("team_strength_score", ascending=False)
            .head(20)
            .to_string(index=False)
        )
    else:
        print(f"\n[info] Missing {strength_path}")

    merge_report_path = PROCESSED_DATA_DIR / RANKING_MERGE_REPORT_FILE
    if merge_report_path.is_file():
        print("\n=== Ranking Merge Report ===")
        print(pd.read_csv(merge_report_path).to_string(index=False))
    else:
        print(f"\n[info] Missing {merge_report_path}")

    sample_cols = [
        col for col in [
            "date", "team_a", "team_b", "team_a_fifa_rank", "team_b_fifa_rank", "diff_fifa_rank",
            "team_a_elo", "team_b_elo", "diff_elo", "diff_strength_score",
        ] if col in df.columns
    ]
    print("\n=== Sample Ranking Feature Rows ===")
    print(df[sample_cols].head(20).to_string(index=False))


if __name__ == "__main__":
    main()
