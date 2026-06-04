"""Streamlit homepage for the FIFA World Cup 2026 AI Predictor."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.data_sources import DATA_SOURCES  # noqa: E402
import src.utils.constants as C  # noqa: E402

CANONICAL_MATCHES_FILE = getattr(C, "CANONICAL_MATCHES_FILE", "canonical_matches.csv")
CANONICAL_MATCHES_SAMPLE_FILE = getattr(
    C, "CANONICAL_MATCHES_SAMPLE_FILE", "canonical_matches_sample.csv"
)
CLEANING_SUMMARY_FILE = getattr(C, "CLEANING_SUMMARY_FILE", "cleaning_summary.json")
DATA_QUALITY_REPORT_FILE = getattr(C, "DATA_QUALITY_REPORT_FILE", "data_quality_report.csv")
BEST_BASELINE_MODEL_FILE = getattr(C, "BEST_BASELINE_MODEL_FILE", "best_baseline_model.joblib")
BASELINE_MODEL_DIR = getattr(C, "BASELINE_MODEL_DIR", "models/baseline")
FEATURE_DATASET_FILE = getattr(C, "FEATURE_DATASET_FILE", "feature_dataset.csv")
FEATURE_DATASET_SAMPLE_FILE = getattr(
    C, "FEATURE_DATASET_SAMPLE_FILE", "feature_dataset_sample.csv"
)
FEATURE_QUALITY_REPORT_FILE = getattr(C, "FEATURE_QUALITY_REPORT_FILE", "feature_quality_report.csv")
FEATURE_SUMMARY_FILE = getattr(C, "FEATURE_SUMMARY_FILE", "feature_summary.json")
FEATURE_COLUMNS_FILE = getattr(C, "FEATURE_COLUMNS_FILE", "feature_columns.json")
MODEL_METRICS_FILE = getattr(C, "MODEL_METRICS_FILE", "model_metrics.csv")
FEATURE_IMPORTANCE_RF_FILE = getattr(
    C, "FEATURE_IMPORTANCE_RF_FILE", "feature_importance_random_forest.csv"
)
IMPROVED_MODEL_DIR = getattr(C, "IMPROVED_MODEL_DIR", "models/improved")
BEST_IMPROVED_MODEL_FILE = getattr(C, "BEST_IMPROVED_MODEL_FILE", "best_improved_model.joblib")
IMPROVED_FEATURE_COLUMNS_FILE = getattr(C, "IMPROVED_FEATURE_COLUMNS_FILE", "improved_feature_columns.json")
IMPROVED_MODEL_METRICS_FILE = getattr(C, "IMPROVED_MODEL_METRICS_FILE", "improved_model_metrics.csv")
BASELINE_VS_IMPROVED_METRICS_FILE = getattr(
    C, "BASELINE_VS_IMPROVED_METRICS_FILE", "baseline_vs_improved_metrics.csv"
)
TEMPORAL_BACKTEST_RESULTS_FILE = getattr(C, "TEMPORAL_BACKTEST_RESULTS_FILE", "temporal_backtest_results.csv")
PROBABILITY_QUALITY_REPORT_FILE = getattr(
    C, "PROBABILITY_QUALITY_REPORT_FILE", "probability_quality_report.csv"
)
RANKING_FEATURE_DATASET_FILE = getattr(C, "RANKING_FEATURE_DATASET_FILE", "ranking_feature_dataset.csv")
TEAM_STRENGTH_SNAPSHOT_FILE = getattr(C, "TEAM_STRENGTH_SNAPSHOT_FILE", "team_strength_snapshot.csv")
RANKING_MERGE_REPORT_FILE = getattr(C, "RANKING_MERGE_REPORT_FILE", "ranking_merge_report.csv")
RANKING_ENHANCED_MODEL_DIR = getattr(C, "RANKING_ENHANCED_MODEL_DIR", "models/ranking_enhanced")
BEST_RANKING_ENHANCED_MODEL_FILE = getattr(
    C, "BEST_RANKING_ENHANCED_MODEL_FILE", "best_ranking_enhanced_model.joblib"
)
RANKING_ENHANCED_MODEL_METRICS_FILE = getattr(
    C, "RANKING_ENHANCED_MODEL_METRICS_FILE", "ranking_enhanced_model_metrics.csv"
)
RANKING_VS_PREVIOUS_METRICS_FILE = getattr(
    C, "RANKING_VS_PREVIOUS_METRICS_FILE", "ranking_vs_previous_metrics.csv"
)
FUTURE_PREDICTION_LOG_FILE = getattr(C, "FUTURE_PREDICTION_LOG_FILE", "future_prediction_log.csv")
EXPLANATION_REPORT_FILE = getattr(C, "EXPLANATION_REPORT_FILE", "prediction_explanation_report.csv")
EXPLANATION_HISTORY_FILE = getattr(C, "EXPLANATION_HISTORY_FILE", "prediction_explanation_history.csv")
GLOBAL_EXPLANATION_REPORT_FILE = getattr(C, "GLOBAL_EXPLANATION_REPORT_FILE", "global_model_explanation.csv")
TOURNAMENT_GROUPS_FILE = getattr(C, "TOURNAMENT_GROUPS_FILE", "tournament_groups.csv")
TOURNAMENT_FIXTURES_FILE = getattr(C, "TOURNAMENT_FIXTURES_FILE", "tournament_fixtures.csv")
KNOCKOUT_PLACEHOLDER_FILE = getattr(C, "KNOCKOUT_PLACEHOLDER_FILE", "knockout_placeholders.csv")
KNOCKOUT_BRACKET_FILLED_FILE = getattr(C, "KNOCKOUT_BRACKET_FILLED_FILE", "knockout_bracket_filled.csv")
KNOCKOUT_SIMULATED_MATCHES_FILE = getattr(C, "KNOCKOUT_SIMULATED_MATCHES_FILE", "knockout_simulated_matches.csv")
SINGLE_TOURNAMENT_RESULT_FILE = getattr(C, "SINGLE_TOURNAMENT_RESULT_FILE", "single_tournament_result.json")
KNOCKOUT_SIMULATION_SUMMARY_FILE = getattr(C, "KNOCKOUT_SIMULATION_SUMMARY_FILE", "knockout_simulation_summary.json")
KNOCKOUT_SIMULATION_VALIDATION_REPORT_FILE = getattr(
    C,
    "KNOCKOUT_SIMULATION_VALIDATION_REPORT_FILE",
    "knockout_simulation_validation_report.csv",
)
TOURNAMENT_STRUCTURE_FILE = getattr(C, "TOURNAMENT_STRUCTURE_FILE", "tournament_structure.json")
TOURNAMENT_VALIDATION_REPORT_FILE = getattr(
    C, "TOURNAMENT_VALIDATION_REPORT_FILE", "tournament_validation_report.csv"
)
GROUP_STAGE_SIMULATED_MATCHES_FILE = getattr(C, "GROUP_STAGE_SIMULATED_MATCHES_FILE", "group_stage_simulated_matches.csv")
GROUP_STAGE_TABLES_FILE = getattr(C, "GROUP_STAGE_TABLES_FILE", "group_stage_tables.csv")
GROUP_STAGE_RANKINGS_FILE = getattr(C, "GROUP_STAGE_RANKINGS_FILE", "group_stage_rankings.csv")
BEST_THIRD_PLACED_TEAMS_FILE = getattr(C, "BEST_THIRD_PLACED_TEAMS_FILE", "best_third_placed_teams.csv")
ROUND_OF_32_QUALIFIERS_FILE = getattr(C, "ROUND_OF_32_QUALIFIERS_FILE", "round_of_32_qualifiers.csv")
GROUP_STAGE_SIMULATION_SUMMARY_FILE = getattr(
    C, "GROUP_STAGE_SIMULATION_SUMMARY_FILE", "group_stage_simulation_summary.json"
)
PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")
SHOOTOUT_OUTCOMES_FILE = getattr(C, "SHOOTOUT_OUTCOMES_FILE", "shootout_outcomes.csv")
TEAM_REGISTRY_FILE = getattr(C, "TEAM_REGISTRY_FILE", "team_registry.csv")

st.set_page_config(
    page_title="FIFA World Cup 2026 AI Predictor",
    page_icon="⚽",
    layout="wide",
)

st.title("FIFA World Cup 2026 AI Predictor")

st.markdown(
    """
    Welcome to the **FIFA World Cup 2026 AI Predictor** — a machine learning
    and simulation-based dashboard for forecasting the 2026 tournament.
    """
)

st.subheader("Current Project Status")
st.success(
    "Step 1: Foundation completed.\n\n"
    "Step 2: Dataset setup completed.\n\n"
    "Step 3: Data cleaning and canonical dataset completed.\n\n"
    "Step 4: Feature engineering completed.\n\n"
    "Step 5: Baseline model completed.\n\n"
    "Step 6: Improved model completed.\n\n"
    "Step 7: FIFA rankings and Elo integration completed.\n\n"
    "Step 8: Future match prediction completed.\n\n"
    "Step 9: Predictor UI and API polishing completed.\n\n"
    "Step 10: Prediction explainability completed.\n\n"
    "Step 11: Tournament fixture and group setup completed.\n\n"
    "Step 12: Group-stage simulation completed.\n\n"
    "Step 13: Knockout simulation completed."
)
st.caption(
    "The project includes baseline + improved + ranking-enhanced classifiers, plus real arbitrary future match predictions from generated pre-match features."
)

st.subheader("Step 3: Processed Outputs")
processed_files = [
    CANONICAL_MATCHES_FILE,
    CANONICAL_MATCHES_SAMPLE_FILE,
    TEAM_REGISTRY_FILE,
    SHOOTOUT_OUTCOMES_FILE,
    DATA_QUALITY_REPORT_FILE,
    CLEANING_SUMMARY_FILE,
]
processed_rows = []
for name in processed_files:
    path = PROCESSED_DATA_DIR / name
    processed_rows.append(
        {
            "file": name,
            "path": str(path),
            "present": path.is_file(),
        }
    )
st.dataframe(pd.DataFrame(processed_rows), use_container_width=True)
st.caption(
    "Run `python main.py` to (re)generate the cleaned canonical dataset and "
    "team registry under `data/processed/`."
)

st.subheader("Step 4: Feature Outputs")
feature_files = [
    FEATURE_DATASET_FILE,
    FEATURE_DATASET_SAMPLE_FILE,
    FEATURE_QUALITY_REPORT_FILE,
    FEATURE_SUMMARY_FILE,
]
feature_rows = []
for name in feature_files:
    path = PROCESSED_DATA_DIR / name
    feature_rows.append(
        {
            "file": name,
            "path": str(path),
            "present": path.is_file(),
        }
    )
st.dataframe(pd.DataFrame(feature_rows), use_container_width=True)
st.caption(
    "The feature dataset is leakage-safe: each row uses only matches before the current match date."
)

st.subheader("Step 5: Baseline Model Outputs")
baseline_rows = [
    {
        "file": BEST_BASELINE_MODEL_FILE,
        "path": str(Path(BASELINE_MODEL_DIR) / BEST_BASELINE_MODEL_FILE),
        "present": (Path(BASELINE_MODEL_DIR) / BEST_BASELINE_MODEL_FILE).is_file(),
    },
    {
        "file": FEATURE_COLUMNS_FILE,
        "path": str(Path(BASELINE_MODEL_DIR) / FEATURE_COLUMNS_FILE),
        "present": (Path(BASELINE_MODEL_DIR) / FEATURE_COLUMNS_FILE).is_file(),
    },
    {
        "file": MODEL_METRICS_FILE,
        "path": str(Path("reports") / MODEL_METRICS_FILE),
        "present": (Path("reports") / MODEL_METRICS_FILE).is_file(),
    },
    {
        "file": FEATURE_IMPORTANCE_RF_FILE,
        "path": str(Path("reports") / FEATURE_IMPORTANCE_RF_FILE),
        "present": (Path("reports") / FEATURE_IMPORTANCE_RF_FILE).is_file(),
    },
]
st.dataframe(pd.DataFrame(baseline_rows), use_container_width=True)
st.caption(
    "The baseline model artifacts live under `models/baseline/` and the evaluation reports live under `reports/`."
)

st.subheader("Step 6: Improved Model Outputs")
improved_rows = [
    {
        "file": BEST_IMPROVED_MODEL_FILE,
        "path": str(Path(IMPROVED_MODEL_DIR) / BEST_IMPROVED_MODEL_FILE),
        "present": (Path(IMPROVED_MODEL_DIR) / BEST_IMPROVED_MODEL_FILE).is_file(),
    },
    {
        "file": IMPROVED_FEATURE_COLUMNS_FILE,
        "path": str(Path(IMPROVED_MODEL_DIR) / IMPROVED_FEATURE_COLUMNS_FILE),
        "present": (Path(IMPROVED_MODEL_DIR) / IMPROVED_FEATURE_COLUMNS_FILE).is_file(),
    },
    {
        "file": IMPROVED_MODEL_METRICS_FILE,
        "path": str(Path("reports") / IMPROVED_MODEL_METRICS_FILE),
        "present": (Path("reports") / IMPROVED_MODEL_METRICS_FILE).is_file(),
    },
    {
        "file": BASELINE_VS_IMPROVED_METRICS_FILE,
        "path": str(Path("reports") / BASELINE_VS_IMPROVED_METRICS_FILE),
        "present": (Path("reports") / BASELINE_VS_IMPROVED_METRICS_FILE).is_file(),
    },
    {
        "file": TEMPORAL_BACKTEST_RESULTS_FILE,
        "path": str(Path("reports") / TEMPORAL_BACKTEST_RESULTS_FILE),
        "present": (Path("reports") / TEMPORAL_BACKTEST_RESULTS_FILE).is_file(),
    },
    {
        "file": PROBABILITY_QUALITY_REPORT_FILE,
        "path": str(Path("reports") / PROBABILITY_QUALITY_REPORT_FILE),
        "present": (Path("reports") / PROBABILITY_QUALITY_REPORT_FILE).is_file(),
    },
]
st.dataframe(pd.DataFrame(improved_rows), use_container_width=True)
st.caption("Step 6 adds optional XGBoost/LightGBM, calibrated probabilities, and temporal backtesting.")

st.subheader("Step 7: Ranking + Elo Outputs")
step7_rows = [
    {
        "file": RANKING_FEATURE_DATASET_FILE,
        "path": str(PROCESSED_DATA_DIR / RANKING_FEATURE_DATASET_FILE),
        "present": (PROCESSED_DATA_DIR / RANKING_FEATURE_DATASET_FILE).is_file(),
    },
    {
        "file": TEAM_STRENGTH_SNAPSHOT_FILE,
        "path": str(PROCESSED_DATA_DIR / TEAM_STRENGTH_SNAPSHOT_FILE),
        "present": (PROCESSED_DATA_DIR / TEAM_STRENGTH_SNAPSHOT_FILE).is_file(),
    },
    {
        "file": RANKING_MERGE_REPORT_FILE,
        "path": str(PROCESSED_DATA_DIR / RANKING_MERGE_REPORT_FILE),
        "present": (PROCESSED_DATA_DIR / RANKING_MERGE_REPORT_FILE).is_file(),
    },
    {
        "file": BEST_RANKING_ENHANCED_MODEL_FILE,
        "path": str(Path(RANKING_ENHANCED_MODEL_DIR) / BEST_RANKING_ENHANCED_MODEL_FILE),
        "present": (Path(RANKING_ENHANCED_MODEL_DIR) / BEST_RANKING_ENHANCED_MODEL_FILE).is_file(),
    },
    {
        "file": RANKING_ENHANCED_MODEL_METRICS_FILE,
        "path": str(Path("reports") / RANKING_ENHANCED_MODEL_METRICS_FILE),
        "present": (Path("reports") / RANKING_ENHANCED_MODEL_METRICS_FILE).is_file(),
    },
    {
        "file": RANKING_VS_PREVIOUS_METRICS_FILE,
        "path": str(Path("reports") / RANKING_VS_PREVIOUS_METRICS_FILE),
        "present": (Path("reports") / RANKING_VS_PREVIOUS_METRICS_FILE).is_file(),
    },
]
st.dataframe(pd.DataFrame(step7_rows), use_container_width=True)
st.caption(
    "Step 7 adds snapshot FIFA/Elo team-strength signals. For strict historical backtesting, date-aware historical ranking joins are recommended."
)

st.subheader("Step 8: Future Match Prediction Outputs")
step8_rows = [
    {
        "file": FUTURE_PREDICTION_LOG_FILE,
        "path": str(Path("reports") / FUTURE_PREDICTION_LOG_FILE),
        "present": (Path("reports") / FUTURE_PREDICTION_LOG_FILE).is_file(),
    },
]
st.dataframe(pd.DataFrame(step8_rows), use_container_width=True)
st.caption("Step 8 supports real arbitrary future match predictions and logs them under `reports/`.")

st.subheader("Step 10: Explainability Outputs")
step10_rows = [
    {
        "file": EXPLANATION_REPORT_FILE,
        "path": str(Path("reports") / EXPLANATION_REPORT_FILE),
        "present": (Path("reports") / EXPLANATION_REPORT_FILE).is_file(),
    },
    {
        "file": EXPLANATION_HISTORY_FILE,
        "path": str(Path("reports") / EXPLANATION_HISTORY_FILE),
        "present": (Path("reports") / EXPLANATION_HISTORY_FILE).is_file(),
    },
    {
        "file": GLOBAL_EXPLANATION_REPORT_FILE,
        "path": str(Path("reports") / GLOBAL_EXPLANATION_REPORT_FILE),
        "present": (Path("reports") / GLOBAL_EXPLANATION_REPORT_FILE).is_file(),
    },
]
st.dataframe(pd.DataFrame(step10_rows), use_container_width=True)

st.subheader("Step 11: Tournament Setup Outputs")
step11_rows = [
    {
        "file": TOURNAMENT_GROUPS_FILE,
        "path": str(PROCESSED_DATA_DIR / TOURNAMENT_GROUPS_FILE),
        "present": (PROCESSED_DATA_DIR / TOURNAMENT_GROUPS_FILE).is_file(),
    },
    {
        "file": TOURNAMENT_FIXTURES_FILE,
        "path": str(PROCESSED_DATA_DIR / TOURNAMENT_FIXTURES_FILE),
        "present": (PROCESSED_DATA_DIR / TOURNAMENT_FIXTURES_FILE).is_file(),
    },
    {
        "file": KNOCKOUT_PLACEHOLDER_FILE,
        "path": str(PROCESSED_DATA_DIR / KNOCKOUT_PLACEHOLDER_FILE),
        "present": (PROCESSED_DATA_DIR / KNOCKOUT_PLACEHOLDER_FILE).is_file(),
    },
    {
        "file": TOURNAMENT_STRUCTURE_FILE,
        "path": str(PROCESSED_DATA_DIR / TOURNAMENT_STRUCTURE_FILE),
        "present": (PROCESSED_DATA_DIR / TOURNAMENT_STRUCTURE_FILE).is_file(),
    },
    {
        "file": TOURNAMENT_VALIDATION_REPORT_FILE,
        "path": str(PROCESSED_DATA_DIR / TOURNAMENT_VALIDATION_REPORT_FILE),
        "present": (PROCESSED_DATA_DIR / TOURNAMENT_VALIDATION_REPORT_FILE).is_file(),
    },
]
st.dataframe(pd.DataFrame(step11_rows), use_container_width=True)
st.caption("Step 11 prepares validated group/fixture/knockout structure only (no outcome simulation yet).")

st.subheader("Step 12: Group-Stage Simulation Outputs")
step12_rows = [
    {
        "file": GROUP_STAGE_SIMULATED_MATCHES_FILE,
        "path": str(PROCESSED_DATA_DIR / GROUP_STAGE_SIMULATED_MATCHES_FILE),
        "present": (PROCESSED_DATA_DIR / GROUP_STAGE_SIMULATED_MATCHES_FILE).is_file(),
    },
    {
        "file": GROUP_STAGE_TABLES_FILE,
        "path": str(PROCESSED_DATA_DIR / GROUP_STAGE_TABLES_FILE),
        "present": (PROCESSED_DATA_DIR / GROUP_STAGE_TABLES_FILE).is_file(),
    },
    {
        "file": GROUP_STAGE_RANKINGS_FILE,
        "path": str(PROCESSED_DATA_DIR / GROUP_STAGE_RANKINGS_FILE),
        "present": (PROCESSED_DATA_DIR / GROUP_STAGE_RANKINGS_FILE).is_file(),
    },
    {
        "file": BEST_THIRD_PLACED_TEAMS_FILE,
        "path": str(PROCESSED_DATA_DIR / BEST_THIRD_PLACED_TEAMS_FILE),
        "present": (PROCESSED_DATA_DIR / BEST_THIRD_PLACED_TEAMS_FILE).is_file(),
    },
    {
        "file": ROUND_OF_32_QUALIFIERS_FILE,
        "path": str(PROCESSED_DATA_DIR / ROUND_OF_32_QUALIFIERS_FILE),
        "present": (PROCESSED_DATA_DIR / ROUND_OF_32_QUALIFIERS_FILE).is_file(),
    },
    {
        "file": GROUP_STAGE_SIMULATION_SUMMARY_FILE,
        "path": str(PROCESSED_DATA_DIR / GROUP_STAGE_SIMULATION_SUMMARY_FILE),
        "present": (PROCESSED_DATA_DIR / GROUP_STAGE_SIMULATION_SUMMARY_FILE).is_file(),
    },
]
st.dataframe(pd.DataFrame(step12_rows), use_container_width=True)
st.caption("Step 12 simulates group stage only and prepares Round-of-32 qualifiers.")

st.subheader("Step 13: Knockout Simulation Outputs")
step13_rows = [
    {
        "file": KNOCKOUT_BRACKET_FILLED_FILE,
        "path": str(PROCESSED_DATA_DIR / KNOCKOUT_BRACKET_FILLED_FILE),
        "present": (PROCESSED_DATA_DIR / KNOCKOUT_BRACKET_FILLED_FILE).is_file(),
    },
    {
        "file": KNOCKOUT_SIMULATED_MATCHES_FILE,
        "path": str(PROCESSED_DATA_DIR / KNOCKOUT_SIMULATED_MATCHES_FILE),
        "present": (PROCESSED_DATA_DIR / KNOCKOUT_SIMULATED_MATCHES_FILE).is_file(),
    },
    {
        "file": SINGLE_TOURNAMENT_RESULT_FILE,
        "path": str(PROCESSED_DATA_DIR / SINGLE_TOURNAMENT_RESULT_FILE),
        "present": (PROCESSED_DATA_DIR / SINGLE_TOURNAMENT_RESULT_FILE).is_file(),
    },
    {
        "file": KNOCKOUT_SIMULATION_SUMMARY_FILE,
        "path": str(PROCESSED_DATA_DIR / KNOCKOUT_SIMULATION_SUMMARY_FILE),
        "present": (PROCESSED_DATA_DIR / KNOCKOUT_SIMULATION_SUMMARY_FILE).is_file(),
    },
    {
        "file": KNOCKOUT_SIMULATION_VALIDATION_REPORT_FILE,
        "path": str(PROCESSED_DATA_DIR / KNOCKOUT_SIMULATION_VALIDATION_REPORT_FILE),
        "present": (PROCESSED_DATA_DIR / KNOCKOUT_SIMULATION_VALIDATION_REPORT_FILE).is_file(),
    },
]
st.dataframe(pd.DataFrame(step13_rows), use_container_width=True)
st.caption("Step 13 simulates one knockout bracket only and saves the full path plus validation report.")

st.subheader("Planned Datasets")
rows = []
for key, cfg in DATA_SOURCES.items():
    real_present = cfg.expected_path.is_file()
    rows.append(
        {
            "dataset": cfg.name,
            "expected_real_path": str(cfg.expected_path),
            "sample_fallback": str(cfg.sample_path),
            "real_file_present": real_present,
            "source": "real" if real_present else "sample",
        }
    )
st.dataframe(pd.DataFrame(rows), use_container_width=True)
st.caption(
    "Real datasets can be added manually to `data/raw/`. "
    "Sample fallback data is used when real files are missing."
)

st.subheader("Planned Modules")
st.markdown(
    """
    - **Match Predictor** — real arbitrary future-match probabilities from generated pre-match features.
    - **Knockout Simulation** — single-bracket knockout path and bracket path reporting.
    - **Tournament Orchestrator** — full single-run tournament flow from groups to champion.
    - **Tournament Simulator** — Monte Carlo simulation of the full World Cup.
    - **Golden Ball Predictor** — best-player candidates and probabilities.
    - **Model Explanation** — feature importance, SHAP values, calibration.
    """
)

st.info("Use the sidebar to navigate between the placeholder module pages.")

st.caption(
    "Disclaimer: This is an educational sports-analytics project. "
    "It is not betting advice."
)
