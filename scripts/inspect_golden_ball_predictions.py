"""Compatibility alias for Golden Ball inspection within the broader awards predictor."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import src.utils.constants as C

PROJECT_ROOT = getattr(C, "PROJECT_ROOT", Path(__file__).resolve().parents[1])
PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", PROJECT_ROOT / "data" / "processed")
REPORTS_DIR = PROJECT_ROOT / "reports"

GOLDEN_BALL_PREDICTIONS_FILE = getattr(C, "GOLDEN_BALL_PREDICTIONS_FILE", "golden_ball_predictions.csv")
WORLD_CUP_AWARDS_SUMMARY_FILE = getattr(C, "WORLD_CUP_AWARDS_SUMMARY_FILE", "world_cup_awards_summary.json")
WORLD_CUP_AWARDS_VALIDATION_REPORT_FILE = getattr(C, "WORLD_CUP_AWARDS_VALIDATION_REPORT_FILE", "world_cup_awards_validation_report.csv")
WORLD_CUP_AWARDS_REPORT_FILE = getattr(C, "WORLD_CUP_AWARDS_REPORT_FILE", "world_cup_awards_report.md")


def main() -> int:
    print("Golden Ball is now part of the broader World Cup Awards Predictor.")
    predictions_path = PROCESSED_DATA_DIR / GOLDEN_BALL_PREDICTIONS_FILE
    summary_path = PROCESSED_DATA_DIR / WORLD_CUP_AWARDS_SUMMARY_FILE
    validation_path = PROCESSED_DATA_DIR / WORLD_CUP_AWARDS_VALIDATION_REPORT_FILE
    report_path = REPORTS_DIR / WORLD_CUP_AWARDS_REPORT_FILE

    if not predictions_path.is_file() or not summary_path.is_file():
        print("Run python scripts/generate_world_cup_awards.py first.")
        return 0

    predictions_df = pd.read_csv(predictions_path)
    with summary_path.open("r", encoding="utf-8") as f:
        summary = json.load(f)

    validation_df = pd.read_csv(validation_path) if validation_path.is_file() else pd.DataFrame()
    report_lines = report_path.read_text(encoding="utf-8").splitlines() if report_path.is_file() else []

    print("=== Step 17 Golden Ball Inspection (Compatibility View) ===")
    print("summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    print("\nTop 20 candidates:")
    top20 = predictions_df.head(20)
    if top20.empty:
        print("No predictions found.")
    else:
        show_cols = [col for col in ["golden_ball_rank", "player", "team", "position", "golden_ball_probability", "award_podium"] if col in top20.columns]
        print(top20[show_cols].to_string(index=False))

    print("\nPosition distribution:")
    if "position" in predictions_df.columns and not predictions_df.empty:
        print(predictions_df["position"].value_counts().to_string())
    else:
        print("No position column found.")

    print("\nTeam distribution among top 20:")
    if "team" in top20.columns and not top20.empty:
        print(top20["team"].value_counts().to_string())
    else:
        print("No team information found.")

    print("\nValidation report preview:")
    if validation_df.empty:
        print("No validation report found.")
    else:
        print(validation_df.head(20).to_string(index=False))

    print("\nWorld Cup awards markdown report preview (first 40 lines):")
    if not report_lines:
        print("No report found.")
    else:
        for line in report_lines[:40]:
            print(line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
