"""Streamlit page: Model explanation and metrics."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

for _path in (Path(__file__).resolve().parents[2], Path(__file__).resolve().parents[1]):
    _entry = str(_path)
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

from app.page_bootstrap import setup_streamlit_paths
from app.components.ui import render_data_table, render_empty_state, render_hero, render_info_panel, render_section_header

ROOT, _ = setup_streamlit_paths(__file__)

import src.utils.constants as C

IMPROVED_MODEL_METRICS_FILE = getattr(C, "IMPROVED_MODEL_METRICS_FILE", "improved_model_metrics.csv")
BASELINE_VS_IMPROVED_METRICS_FILE = getattr(
    C, "BASELINE_VS_IMPROVED_METRICS_FILE", "baseline_vs_improved_metrics.csv"
)
TEMPORAL_BACKTEST_RESULTS_FILE = getattr(C, "TEMPORAL_BACKTEST_RESULTS_FILE", "temporal_backtest_results.csv")
PROBABILITY_QUALITY_REPORT_FILE = getattr(C, "PROBABILITY_QUALITY_REPORT_FILE", "probability_quality_report.csv")
RANKING_ENHANCED_MODEL_METRICS_FILE = getattr(
    C, "RANKING_ENHANCED_MODEL_METRICS_FILE", "ranking_enhanced_model_metrics.csv"
)
RANKING_VS_PREVIOUS_METRICS_FILE = getattr(C, "RANKING_VS_PREVIOUS_METRICS_FILE", "ranking_vs_previous_metrics.csv")
RANKING_FEATURE_IMPORTANCE_FILE = getattr(C, "RANKING_FEATURE_IMPORTANCE_FILE", "ranking_feature_importance.csv")
GLOBAL_EXPLANATION_REPORT_FILE = getattr(C, "GLOBAL_EXPLANATION_REPORT_FILE", "global_model_explanation.csv")

def render_page() -> None:
    render_hero(
        "Model Explanation",
        "Compare model metrics, probability quality, and local/global prediction explanations.",
        eyebrow="Model analytics",
    )

    render_info_panel(
        "Log loss and Brier score matter more than raw accuracy for tournament simulation "
        "because the simulator needs reliable probabilities."
    )

    reports_dir = ROOT / "reports"

    report_paths = [
        reports_dir / BASELINE_VS_IMPROVED_METRICS_FILE,
        reports_dir / IMPROVED_MODEL_METRICS_FILE,
        reports_dir / TEMPORAL_BACKTEST_RESULTS_FILE,
        reports_dir / PROBABILITY_QUALITY_REPORT_FILE,
        reports_dir / RANKING_ENHANCED_MODEL_METRICS_FILE,
        reports_dir / RANKING_VS_PREVIOUS_METRICS_FILE,
        reports_dir / RANKING_FEATURE_IMPORTANCE_FILE,
        reports_dir / GLOBAL_EXPLANATION_REPORT_FILE,
    ]
    if not any(path.is_file() for path in report_paths):
        render_empty_state(
            "No model reports yet",
            "Train models first, then return here for metrics and explanations.",
        )
        st.code(
            "python scripts/train_improved_models.py\n"
            "python scripts/train_ranking_enhanced_model.py\n"
            "python scripts/inspect_global_explanation.py",
            language="bash",
        )
        return

    comparison_path = report_paths[0]
    if comparison_path.is_file():
        render_section_header("Baseline vs improved metrics")
        comparison_df = pd.read_csv(comparison_path)
        render_data_table(comparison_df, use_container_width=True)

    improved_metrics_path = report_paths[1]
    if improved_metrics_path.is_file():
        render_section_header("Improved model metrics")
        improved_df = pd.read_csv(improved_metrics_path)
        if "log_loss" in improved_df.columns:
            improved_df = improved_df.sort_values("log_loss", ascending=True)
        render_data_table(improved_df, use_container_width=True)

    backtest_path = report_paths[2]
    if backtest_path.is_file():
        render_section_header("Temporal backtesting")
        backtest_df = pd.read_csv(backtest_path)
        render_data_table(backtest_df, use_container_width=True)

    probability_quality_path = report_paths[3]
    if probability_quality_path.is_file():
        render_section_header("Probability quality ranking")
        quality_df = pd.read_csv(probability_quality_path)
        render_data_table(quality_df, use_container_width=True)

    ranking_metrics_path = report_paths[4]
    if ranking_metrics_path.is_file():
        render_section_header("Ranking-enhanced model metrics")
        ranking_df = pd.read_csv(ranking_metrics_path)
        if "log_loss" in ranking_df.columns:
            ranking_df = ranking_df.sort_values("log_loss", ascending=True)
        render_data_table(ranking_df, use_container_width=True)

    ranking_vs_previous_path = report_paths[5]
    if ranking_vs_previous_path.is_file():
        render_section_header("Ranking vs previous model")
        render_data_table(pd.read_csv(ranking_vs_previous_path), use_container_width=True)

    ranking_importance_path = report_paths[6]
    if ranking_importance_path.is_file():
        render_section_header("Ranking feature importance")
        render_data_table(pd.read_csv(ranking_importance_path).head(30), use_container_width=True)

    render_section_header("Local prediction explanation")
    st.markdown(
        "- Prediction explanations use **SHAP** when available.\n"
        "- Otherwise the app uses a **model-agnostic local sensitivity** fallback.\n"
        "- Explanations are approximate — use for interpretation, not certainty."
    )

    global_explanation_path = report_paths[7]
    if global_explanation_path.is_file():
        render_section_header("Global model explanation")
        global_df = pd.read_csv(global_explanation_path)
        render_data_table(global_df.head(30), use_container_width=True)
    else:
        st.info(
            "No global explanation report found yet. "
            "Run `python scripts/inspect_global_explanation.py` to generate it."
        )

    render_info_panel(
        "Ranking snapshot note: the latest available FIFA/Elo snapshot is used across historical rows. "
        "Date-aware historical ranking joins can be added in a later refinement."
    )

    if not any(
        path.is_file()
        for path in report_paths[:7]
    ):
        st.info(
            "Partial reports loaded. Run training scripts to populate remaining metrics."
        )
