"""Inspect Step 6 improved-model artifacts and reports."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import src.utils.constants as C  # noqa: E402

IMPROVED_MODEL_METRICS_FILE = getattr(C, "IMPROVED_MODEL_METRICS_FILE", "improved_model_metrics.csv")
BASELINE_VS_IMPROVED_METRICS_FILE = getattr(
    C, "BASELINE_VS_IMPROVED_METRICS_FILE", "baseline_vs_improved_metrics.csv"
)
TEMPORAL_BACKTEST_RESULTS_FILE = getattr(C, "TEMPORAL_BACKTEST_RESULTS_FILE", "temporal_backtest_results.csv")
PROBABILITY_QUALITY_REPORT_FILE = getattr(C, "PROBABILITY_QUALITY_REPORT_FILE", "probability_quality_report.csv")
MODEL_COMPARISON_SUMMARY_FILE = getattr(C, "MODEL_COMPARISON_SUMMARY_FILE", "model_comparison_summary.json")


def main() -> None:
    reports_dir = Path("reports")
    train_hint = "Run `python scripts/train_improved_models.py` first."

    improved_metrics_path = reports_dir / IMPROVED_MODEL_METRICS_FILE
    if improved_metrics_path.is_file():
        improved_df = pd.read_csv(improved_metrics_path)
        if "log_loss" in improved_df.columns:
            improved_df = improved_df.sort_values("log_loss", ascending=True)
        print("=== Improved Model Metrics ===")
        print(improved_df.to_string(index=False))
    else:
        print(f"[info] Missing {improved_metrics_path}. {train_hint}")

    comparison_path = reports_dir / BASELINE_VS_IMPROVED_METRICS_FILE
    if comparison_path.is_file():
        print("\n=== Baseline vs Improved Metrics ===")
        print(pd.read_csv(comparison_path).to_string(index=False))
    else:
        print(f"\n[info] Missing {comparison_path}. {train_hint}")

    backtest_path = reports_dir / TEMPORAL_BACKTEST_RESULTS_FILE
    if backtest_path.is_file():
        backtest_df = pd.read_csv(backtest_path)
        ok_df = backtest_df.loc[backtest_df.get("status", "ok") == "ok"].copy()
        print("\n=== Temporal Backtesting Results ===")
        print(backtest_df.to_string(index=False))
        if not ok_df.empty:
            agg = (
                ok_df.groupby("model_name", dropna=False)[["accuracy", "macro_f1", "log_loss", "multiclass_brier_score"]]
                .mean(numeric_only=True)
                .reset_index()
            )
            print("\n=== Average Backtest Performance by Model ===")
            print(agg.to_string(index=False))
    else:
        print(f"\n[info] Missing {backtest_path}. {train_hint}")

    quality_path = reports_dir / PROBABILITY_QUALITY_REPORT_FILE
    if quality_path.is_file():
        print("\n=== Probability Quality Ranking ===")
        print(pd.read_csv(quality_path).to_string(index=False))
    else:
        print(f"\n[info] Missing {quality_path}. {train_hint}")

    summary_path = reports_dir / MODEL_COMPARISON_SUMMARY_FILE
    if summary_path.is_file():
        summary = json.loads(summary_path.read_text())
        print("\n=== Best Improved Model ===")
        print(summary.get("best_model_name"))
        print(summary.get("best_model_path"))
    else:
        print(f"\n[info] Missing {summary_path}. {train_hint}")


if __name__ == "__main__":
    main()
