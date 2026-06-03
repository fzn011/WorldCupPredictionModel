"""Entry point for the FIFA World Cup 2026 AI Predictor pipeline.

Step 7: prepare ranking-enhanced features and train ranking+Elo enhanced
match-result models.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.features.prepare_ranking_features import prepare_step7_ranking_features
from src.models.train_ranking_enhanced_model import train_ranking_enhanced_model


def main() -> None:
    """Run the Step 7 ranking + Elo integration pipeline."""
    print("Preparing Step 7 ranking features...\n")
    feature_summary = prepare_step7_ranking_features()

    print("Training Step 7 ranking-enhanced models...\n")
    model_summary = train_ranking_enhanced_model()

    print("\n=== Step 7 Ranking + Elo Integration Summary ===")
    print(f"Ranking feature output path: {feature_summary.get('output_path')}")
    print(f"Ranking feature rows:        {feature_summary.get('rows')}")
    print(f"Ranking feature columns:     {feature_summary.get('columns')}")
    print(f"Team strength rows:          {feature_summary.get('team_strength_rows')}")

    print(f"Train rows:                  {model_summary.get('train_rows')}")
    print(f"Test rows:                   {model_summary.get('test_rows')}")
    print(f"Feature count:               {model_summary.get('feature_count')}")
    print(f"Best model name:             {model_summary.get('best_model_name')}")
    print(f"Best model path:             {model_summary.get('best_model_path')}")
    print(f"Metrics path:                {model_summary.get('ranking_metrics_path')}")
    print(f"Comparison path:             {model_summary.get('ranking_vs_previous_path')}")

    notes = model_summary.get("notes", [])
    if notes:
        print("Snapshot-mode limitation note:")
        for note in notes:
            print(f"- {note}")

    metrics_path = Path(model_summary["ranking_metrics_path"])
    if metrics_path.is_file():
        metrics_df = pd.read_csv(metrics_path)
        print("\nRanking-enhanced model metrics:")
        print(metrics_df.to_string(index=False))


if __name__ == "__main__":
    main()
