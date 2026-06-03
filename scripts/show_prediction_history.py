"""Show future prediction history summary from reports/future_prediction_log.csv."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.models.prediction_utils import load_prediction_history



def main() -> int:
    history_df = load_prediction_history()

    if history_df.empty:
        print("No prediction history exists yet.")
        return 0

    print("=== Prediction History Summary ===")
    print(f"Total predictions: {len(history_df)}")

    time_col = "prediction_timestamp" if "prediction_timestamp" in history_df.columns else None
    if time_col:
        preview_df = history_df.sort_values(time_col, ascending=False).head(10)
    else:
        preview_df = history_df.tail(10)

    show_columns = [
        "prediction_timestamp",
        "team_a",
        "team_b",
        "match_date",
        "tournament",
        "model_type",
        "predicted_label",
        "team_a_loss_probability",
        "draw_probability",
        "team_a_win_probability",
    ]
    show_columns = [column for column in show_columns if column in preview_df.columns]

    print("\nMost recent 10 predictions:")
    print(preview_df[show_columns].to_string(index=False))

    if "predicted_label" in history_df.columns:
        print("\nPredicted label distribution:")
        print(history_df["predicted_label"].value_counts(dropna=False).to_string())

    if "model_type" in history_df.columns:
        print("\nModel type distribution:")
        print(history_df["model_type"].value_counts(dropna=False).to_string())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
