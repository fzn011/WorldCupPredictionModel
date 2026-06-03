"""Inspect Step 7 ranking-enhanced model outputs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import src.utils.constants as C  # noqa: E402

RANKING_ENHANCED_MODEL_METRICS_FILE = getattr(
    C, "RANKING_ENHANCED_MODEL_METRICS_FILE", "ranking_enhanced_model_metrics.csv"
)
RANKING_VS_PREVIOUS_METRICS_FILE = getattr(C, "RANKING_VS_PREVIOUS_METRICS_FILE", "ranking_vs_previous_metrics.csv")
RANKING_FEATURE_IMPORTANCE_FILE = getattr(C, "RANKING_FEATURE_IMPORTANCE_FILE", "ranking_feature_importance.csv")
RANKING_MODEL_SUMMARY_FILE = getattr(C, "RANKING_MODEL_SUMMARY_FILE", "ranking_model_summary.json")


def main() -> None:
    reports_dir = Path("reports")
    hint = "Run `python scripts/train_ranking_enhanced_model.py` first."

    metrics_path = reports_dir / RANKING_ENHANCED_MODEL_METRICS_FILE
    if metrics_path.is_file():
        metrics_df = pd.read_csv(metrics_path)
        if "log_loss" in metrics_df.columns:
            metrics_df = metrics_df.sort_values("log_loss", ascending=True)
        print("=== Ranking-Enhanced Model Metrics ===")
        print(metrics_df.to_string(index=False))
    else:
        print(f"[info] Missing {metrics_path}. {hint}")

    comparison_path = reports_dir / RANKING_VS_PREVIOUS_METRICS_FILE
    if comparison_path.is_file():
        print("\n=== Ranking vs Previous Model Metrics ===")
        print(pd.read_csv(comparison_path).to_string(index=False))
    else:
        print(f"\n[info] Missing {comparison_path}. {hint}")

    importance_path = reports_dir / RANKING_FEATURE_IMPORTANCE_FILE
    if importance_path.is_file():
        print("\n=== Ranking Feature Importance (Top 30) ===")
        print(pd.read_csv(importance_path).head(30).to_string(index=False))
    else:
        print(f"\n[info] Missing {importance_path}. {hint}")

    summary_path = reports_dir / RANKING_MODEL_SUMMARY_FILE
    if summary_path.is_file():
        summary = json.loads(summary_path.read_text())
        print("\n=== Ranking Model Summary ===")
        print(json.dumps(summary, indent=2))
        print("\nSnapshot ranking limitation note:")
        for note in summary.get("notes", []):
            print(f"- {note}")
    else:
        print(f"\n[info] Missing {summary_path}. {hint}")


if __name__ == "__main__":
    main()
