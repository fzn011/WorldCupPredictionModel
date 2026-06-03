"""Train Step 7 ranking-enhanced model(s)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.models.train_ranking_enhanced_model import train_ranking_enhanced_model  # noqa: E402


def main() -> None:
    summary = train_ranking_enhanced_model()
    print("=== Step 7 Ranking-Enhanced Model Training Summary ===")
    print(f"Status: {summary.get('status')}")
    print(f"Train rows: {summary.get('train_rows')}")
    print(f"Test rows: {summary.get('test_rows')}")
    print(f"Feature count: {summary.get('feature_count')}")
    print(f"Trained models: {summary.get('trained_models')}")
    print(f"Skipped models: {summary.get('skipped_models')}")
    print(f"Best model: {summary.get('best_model_name')}")
    print(f"Best model path: {summary.get('best_model_path')}")
    print(f"Metrics path: {summary.get('ranking_metrics_path')}")
    print(f"Comparison path: {summary.get('ranking_vs_previous_path')}")
    print(f"Notes: {summary.get('notes')}")


if __name__ == "__main__":
    main()
