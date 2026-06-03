"""Entry point for the FIFA World Cup 2026 AI Predictor pipeline.

Step 6: train improved match-result models (advanced + calibrated), run
temporal backtesting, and persist comparison artifacts.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.models.train_improved_model import train_improved_models


def main() -> None:
    """Run the Step 6 improved-model training pipeline."""
    print("Training Step 6 improved models...\n")
    summary = train_improved_models()

    print("\n=== Step 6 Improved Model Summary ===")
    print(f"Status: {summary.get('status')}")
    print(f"Train rows:         {summary.get('train_rows')}")
    print(f"Calibration rows:   {summary.get('calibration_rows')}")
    print(f"Test rows:          {summary.get('test_rows')}")
    print(f"Feature count:      {summary.get('feature_count')}")
    print(f"Trained models:     {summary.get('trained_models')}")
    print(f"Skipped models:     {summary.get('skipped_models')}")
    print(f"Best model name:    {summary.get('best_model_name')}")
    print(f"Best model path:    {summary.get('best_model_path')}")
    print(f"Improved metrics:   {summary.get('improved_metrics_path')}")
    print(f"Backtest path:      {summary.get('backtest_results_path')}")

    metrics_path = Path(summary["improved_metrics_path"])
    if metrics_path.is_file():
        metrics_df = pd.read_csv(metrics_path)
        print("\nImproved model metrics:")
        print(metrics_df.to_string(index=False))


if __name__ == "__main__":
    main()
