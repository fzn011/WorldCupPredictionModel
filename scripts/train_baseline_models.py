"""Train the Step 5 baseline match-result models."""

from __future__ import annotations

import sys
from pathlib import Path

# Make `src` importable when running this script directly.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.models.train_match_model import train_baseline_models  # noqa: E402


def main() -> None:
    """Train the baseline models and print a readable summary."""
    summary = train_baseline_models()
    print("=== Step 5 Training Summary ===")
    print(f"Status: {summary.get('status')}")
    print(f"Train rows: {summary.get('train_rows')}")
    print(f"Test rows: {summary.get('test_rows')}")
    print(f"Feature count: {summary.get('feature_count')}")
    print(f"Best model: {summary.get('best_model_name')}")
    print(f"Best model path: {summary.get('best_model_path')}")
    print(f"Metrics path: {summary.get('model_metrics_path')}")
    print(f"Feature columns path: {summary.get('feature_columns_path')}")


if __name__ == "__main__":
    main()
