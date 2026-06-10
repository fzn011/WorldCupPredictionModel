"""Inspect Step 17 World Cup awards analytics artifacts."""

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

WORLD_CUP_AWARDS_PREDICTIONS_FILE = getattr(C, "WORLD_CUP_AWARDS_PREDICTIONS_FILE", "world_cup_awards_predictions.csv")
GOLDEN_BALL_PREDICTIONS_FILE = getattr(C, "GOLDEN_BALL_PREDICTIONS_FILE", "golden_ball_predictions.csv")
GOLDEN_BOOT_PREDICTIONS_FILE = getattr(C, "GOLDEN_BOOT_PREDICTIONS_FILE", "golden_boot_predictions.csv")
GOLDEN_GLOVE_PREDICTIONS_FILE = getattr(C, "GOLDEN_GLOVE_PREDICTIONS_FILE", "golden_glove_predictions.csv")
YOUNG_PLAYER_PREDICTIONS_FILE = getattr(C, "YOUNG_PLAYER_PREDICTIONS_FILE", "young_player_predictions.csv")
FAIR_PLAY_PREDICTIONS_FILE = getattr(C, "FAIR_PLAY_PREDICTIONS_FILE", "fair_play_predictions.csv")
MOST_ENTERTAINING_TEAM_PREDICTIONS_FILE = getattr(C, "MOST_ENTERTAINING_TEAM_PREDICTIONS_FILE", "most_entertaining_team_predictions.csv")
TEAM_OF_THE_TOURNAMENT_FILE = getattr(C, "TEAM_OF_THE_TOURNAMENT_FILE", "team_of_the_tournament.csv")
WORLD_CUP_AWARDS_SUMMARY_FILE = getattr(C, "WORLD_CUP_AWARDS_SUMMARY_FILE", "world_cup_awards_summary.json")
WORLD_CUP_AWARDS_VALIDATION_REPORT_FILE = getattr(C, "WORLD_CUP_AWARDS_VALIDATION_REPORT_FILE", "world_cup_awards_validation_report.csv")
WORLD_CUP_AWARDS_REPORT_FILE = getattr(C, "WORLD_CUP_AWARDS_REPORT_FILE", "world_cup_awards_report.md")


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.is_file() else pd.DataFrame()


def _print_top(title: str, df: pd.DataFrame, columns: list[str], top_n: int = 10) -> None:
    print(f"\n{title}:")
    if df.empty:
        print("No data available.")
        return
    show_cols = [col for col in columns if col in df.columns]
    print(df[show_cols].head(top_n).to_string(index=False))


def main() -> int:
    combined_path = PROCESSED_DATA_DIR / WORLD_CUP_AWARDS_PREDICTIONS_FILE
    summary_path = PROCESSED_DATA_DIR / WORLD_CUP_AWARDS_SUMMARY_FILE
    report_path = REPORTS_DIR / WORLD_CUP_AWARDS_REPORT_FILE
    validation_path = PROCESSED_DATA_DIR / WORLD_CUP_AWARDS_VALIDATION_REPORT_FILE

    if not combined_path.is_file() or not summary_path.is_file():
        print("Run python scripts/generate_world_cup_awards.py first.")
        return 0

    with summary_path.open("r", encoding="utf-8") as f:
        summary = json.load(f)

    print("=== Step 18 World Cup Awards Inspection ===")
    print("summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    _print_top(
        "Golden Ball top 10",
        _read_csv(PROCESSED_DATA_DIR / GOLDEN_BALL_PREDICTIONS_FILE),
        ["golden_ball_rank", "player", "team", "position", "golden_ball_probability", "award_podium"],
    )
    _print_top(
        "Golden Boot top 10",
        _read_csv(PROCESSED_DATA_DIR / GOLDEN_BOOT_PREDICTIONS_FILE),
        ["golden_boot_rank", "player", "team", "position", "expected_goals_score", "boot_podium"],
    )
    _print_top(
        "Golden Glove top 10",
        _read_csv(PROCESSED_DATA_DIR / GOLDEN_GLOVE_PREDICTIONS_FILE),
        ["golden_glove_rank", "player", "team", "golden_glove_probability", "award"],
    )
    _print_top(
        "Young Player top 10",
        _read_csv(PROCESSED_DATA_DIR / YOUNG_PLAYER_PREDICTIONS_FILE),
        ["young_player_rank", "player", "team", "position", "young_player_probability", "award"],
    )
    _print_top(
        "Fair Play top 10",
        _read_csv(PROCESSED_DATA_DIR / FAIR_PLAY_PREDICTIONS_FILE),
        ["fair_play_rank", "team", "fair_play_probability", "award"],
    )
    _print_top(
        "Most Entertaining Team top 10",
        _read_csv(PROCESSED_DATA_DIR / MOST_ENTERTAINING_TEAM_PREDICTIONS_FILE),
        ["most_entertaining_rank", "team", "most_entertaining_probability", "award"],
    )
    _print_top(
        "Team of the Tournament",
        _read_csv(PROCESSED_DATA_DIR / TEAM_OF_THE_TOURNAMENT_FILE),
        ["formation_slot", "player", "team", "position"],
        top_n=20,
    )

    print("\nValidation report preview:")
    validation_df = _read_csv(validation_path)
    if validation_df.empty:
        print("No validation report available.")
    else:
        print(validation_df.head(20).to_string(index=False))

    print("\nWorld Cup awards markdown report preview (first 40 lines):")
    if not report_path.is_file():
        print("No report found.")
    else:
        for line in report_path.read_text(encoding="utf-8").splitlines()[:40]:
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
