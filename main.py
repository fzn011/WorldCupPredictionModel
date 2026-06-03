"""Entry point for the FIFA World Cup 2026 AI Predictor pipeline.

Step 5: train the first baseline match-result models on the feature dataset
and save model artifacts under ``models/baseline/``.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.models.train_match_model import train_baseline_models


def main() -> None:
    """Run the Step 5 baseline-model training pipeline."""
    print("Training Step 5 baseline models...\n")
    summary = train_baseline_models()

    print("\n=== Step 5 Baseline Model Summary ===")
    print(f"Status: {summary.get('status')}")
    print(f"Train rows:         {summary.get('train_rows')}")
    print(f"Test rows:          {summary.get('test_rows')}")
    print(f"Feature count:      {summary.get('feature_count')}")
    print(f"Best model name:    {summary.get('best_model_name')}")
    print(f"Best model path:    {summary.get('best_model_path')}")
    print(f"Metrics path:       {summary.get('model_metrics_path')}")

    metrics_path = Path(summary["model_metrics_path"])
    if metrics_path.is_file():
        metrics_df = pd.read_csv(metrics_path)
        print("\nModel metrics:")
        print(metrics_df.to_string(index=False))

    feature_columns_path = Path(summary["feature_columns_path"])
    if feature_columns_path.is_file():
        print(f"\nFeature columns saved to: {feature_columns_path}")


if __name__ == "__main__":
    main()
