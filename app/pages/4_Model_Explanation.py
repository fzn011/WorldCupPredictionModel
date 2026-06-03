"""Streamlit page: model comparison and probability quality."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

import src.utils.constants as C

IMPROVED_MODEL_METRICS_FILE = getattr(C, "IMPROVED_MODEL_METRICS_FILE", "improved_model_metrics.csv")
BASELINE_VS_IMPROVED_METRICS_FILE = getattr(
    C, "BASELINE_VS_IMPROVED_METRICS_FILE", "baseline_vs_improved_metrics.csv"
)
TEMPORAL_BACKTEST_RESULTS_FILE = getattr(C, "TEMPORAL_BACKTEST_RESULTS_FILE", "temporal_backtest_results.csv")
PROBABILITY_QUALITY_REPORT_FILE = getattr(C, "PROBABILITY_QUALITY_REPORT_FILE", "probability_quality_report.csv")

st.title("Model Explanation")

st.caption(
    "Accuracy is useful, but log loss and Brier score matter more for the tournament simulator because it needs reliable probabilities."
)

reports_dir = Path("reports")

comparison_path = reports_dir / BASELINE_VS_IMPROVED_METRICS_FILE
if comparison_path.is_file():
    st.subheader("Baseline vs Improved Metrics")
    comparison_df = pd.read_csv(comparison_path)
    st.dataframe(comparison_df, use_container_width=True)

improved_metrics_path = reports_dir / IMPROVED_MODEL_METRICS_FILE
if improved_metrics_path.is_file():
    st.subheader("Improved Model Metrics")
    improved_df = pd.read_csv(improved_metrics_path)
    if "log_loss" in improved_df.columns:
        improved_df = improved_df.sort_values("log_loss", ascending=True)
    st.dataframe(improved_df, use_container_width=True)

backtest_path = reports_dir / TEMPORAL_BACKTEST_RESULTS_FILE
if backtest_path.is_file():
    st.subheader("Temporal Backtesting")
    backtest_df = pd.read_csv(backtest_path)
    st.dataframe(backtest_df, use_container_width=True)

probability_quality_path = reports_dir / PROBABILITY_QUALITY_REPORT_FILE
if probability_quality_path.is_file():
    st.subheader("Probability Quality Ranking")
    quality_df = pd.read_csv(probability_quality_path)
    st.dataframe(quality_df, use_container_width=True)

if not any(
    path.is_file()
    for path in [comparison_path, improved_metrics_path, backtest_path, probability_quality_path]
):
    st.info("No Step 6 reports found yet. Run `python scripts/train_improved_models.py` first.")
