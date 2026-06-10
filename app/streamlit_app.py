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

PROJECT_ROOT = getattr(C, "PROJECT_ROOT", ROOT)

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
FULL_TOURNAMENT_SIMULATED_MATCHES_FILE = getattr(C, "FULL_TOURNAMENT_SIMULATED_MATCHES_FILE", "full_tournament_simulated_matches.csv")
FULL_TOURNAMENT_GROUP_TABLES_FILE = getattr(C, "FULL_TOURNAMENT_GROUP_TABLES_FILE", "full_tournament_group_tables.csv")
FULL_TOURNAMENT_KNOCKOUT_MATCHES_FILE = getattr(C, "FULL_TOURNAMENT_KNOCKOUT_MATCHES_FILE", "full_tournament_knockout_matches.csv")
FULL_TOURNAMENT_STAGE_RESULTS_FILE = getattr(C, "FULL_TOURNAMENT_STAGE_RESULTS_FILE", "full_tournament_stage_results.csv")
FULL_TOURNAMENT_PATH_REPORT_FILE = getattr(C, "FULL_TOURNAMENT_PATH_REPORT_FILE", "full_tournament_path_report.csv")
FULL_TOURNAMENT_RESULT_FILE = getattr(C, "FULL_TOURNAMENT_RESULT_FILE", "single_world_cup_result.json")
FULL_TOURNAMENT_SUMMARY_FILE = getattr(C, "FULL_TOURNAMENT_SUMMARY_FILE", "full_tournament_summary.json")
FULL_TOURNAMENT_VALIDATION_REPORT_FILE = getattr(
    C,
    "FULL_TOURNAMENT_VALIDATION_REPORT_FILE",
    "full_tournament_validation_report.csv",
)
MONTE_CARLO_SIMULATION_RESULTS_FILE = getattr(C, "MONTE_CARLO_SIMULATION_RESULTS_FILE", "monte_carlo_simulation_results.csv")
MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE = getattr(C, "MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE", "monte_carlo_team_stage_probabilities.csv")
MONTE_CARLO_CHAMPION_PROBABILITIES_FILE = getattr(C, "MONTE_CARLO_CHAMPION_PROBABILITIES_FILE", "monte_carlo_champion_probabilities.csv")
MONTE_CARLO_FINALISTS_FILE = getattr(C, "MONTE_CARLO_FINALISTS_FILE", "monte_carlo_finalists.csv")
MONTE_CARLO_SEMIFINALISTS_FILE = getattr(C, "MONTE_CARLO_SEMIFINALISTS_FILE", "monte_carlo_semifinalists.csv")
MONTE_CARLO_SUMMARY_FILE = getattr(C, "MONTE_CARLO_SUMMARY_FILE", "monte_carlo_summary.json")
MONTE_CARLO_VALIDATION_REPORT_FILE = getattr(C, "MONTE_CARLO_VALIDATION_REPORT_FILE", "monte_carlo_validation_report.csv")
MONTE_CARLO_REPORT_MD_FILE = getattr(C, "MONTE_CARLO_REPORT_MD_FILE", "monte_carlo_report.md")
MONTE_CARLO_SUMMARY_CARDS_FILE = getattr(C, "MONTE_CARLO_SUMMARY_CARDS_FILE", "monte_carlo_summary_cards.csv")
MONTE_CARLO_DASHBOARD_EXPORT_FILE = getattr(C, "MONTE_CARLO_DASHBOARD_EXPORT_FILE", "monte_carlo_dashboard_export.csv")
MONTE_CARLO_CHAMPION_CHART_FILE = getattr(C, "MONTE_CARLO_CHAMPION_CHART_FILE", "monte_carlo_champion_probabilities.png")
MONTE_CARLO_STAGE_HEATMAP_FILE = getattr(C, "MONTE_CARLO_STAGE_HEATMAP_FILE", "monte_carlo_stage_heatmap.png")
WORLD_CUP_AWARDS_PREDICTIONS_FILE = getattr(C, "WORLD_CUP_AWARDS_PREDICTIONS_FILE", "world_cup_awards_predictions.csv")
GOLDEN_BALL_PREDICTIONS_FILE = getattr(C, "GOLDEN_BALL_PREDICTIONS_FILE", "golden_ball_predictions.csv")
GOLDEN_BOOT_PREDICTIONS_FILE = getattr(C, "GOLDEN_BOOT_PREDICTIONS_FILE", "golden_boot_predictions.csv")
GOLDEN_GLOVE_PREDICTIONS_FILE = getattr(C, "GOLDEN_GLOVE_PREDICTIONS_FILE", "golden_glove_predictions.csv")
YOUNG_PLAYER_PREDICTIONS_FILE = getattr(C, "YOUNG_PLAYER_PREDICTIONS_FILE", "young_player_predictions.csv")
FAIR_PLAY_PREDICTIONS_FILE = getattr(C, "FAIR_PLAY_PREDICTIONS_FILE", "fair_play_predictions.csv")
MOST_ENTERTAINING_TEAM_PREDICTIONS_FILE = getattr(C, "MOST_ENTERTAINING_TEAM_PREDICTIONS_FILE", "most_entertaining_team_predictions.csv")
TEAM_OF_THE_TOURNAMENT_FILE = getattr(C, "TEAM_OF_THE_TOURNAMENT_FILE", "team_of_the_tournament.csv")
WORLD_CUP_AWARDS_SUMMARY_FILE = getattr(C, "WORLD_CUP_AWARDS_SUMMARY_FILE", "world_cup_awards_summary.json")
WORLD_CUP_AWARDS_VALIDATION_REPORT_FILE = getattr(
    C,
    "WORLD_CUP_AWARDS_VALIDATION_REPORT_FILE",
    "world_cup_awards_validation_report.csv",
)
WORLD_CUP_AWARDS_REPORT_FILE = getattr(C, "WORLD_CUP_AWARDS_REPORT_FILE", "world_cup_awards_report.md")
OFFICIAL_DATA_DIR = PROJECT_ROOT / str(getattr(C, "OFFICIAL_DATA_DIR", "data/official"))
OFFICIAL_PROCESSED_DIR = PROJECT_ROOT / str(getattr(C, "OFFICIAL_PROCESSED_DIR", "data/official/processed"))
OFFICIAL_TEAMS_FILE = getattr(C, "OFFICIAL_TEAMS_FILE", "official_teams.csv")
OFFICIAL_GROUPS_FILE = getattr(C, "OFFICIAL_GROUPS_FILE", "official_groups.csv")
OFFICIAL_FIXTURES_FILE = getattr(C, "OFFICIAL_FIXTURES_FILE", "official_fixtures.csv")
OFFICIAL_VENUES_FILE = getattr(C, "OFFICIAL_VENUES_FILE", "official_venues.csv")
OFFICIAL_MATCH_CALENDAR_FILE = getattr(C, "OFFICIAL_MATCH_CALENDAR_FILE", "official_match_calendar.csv")
OFFICIAL_DATA_SUMMARY_FILE = getattr(C, "OFFICIAL_DATA_SUMMARY_FILE", "official_data_summary.json")
OFFICIAL_DATA_VALIDATION_REPORT_FILE = getattr(C, "OFFICIAL_DATA_VALIDATION_REPORT_FILE", "official_data_validation_report.csv")
OFFICIAL_SOURCE_MANIFEST_FILE = getattr(C, "OFFICIAL_SOURCE_MANIFEST_FILE", "source_manifest.json")
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
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
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
    "Step 13: Knockout simulation completed.\n\n"
    "Step 14: Full tournament single-run completed.\n\n"
    "Step 15: Monte Carlo simulator completed.\n\n"
    "Step 16: Monte Carlo dashboard and report polish completed.\n\n"
    "Step 17A: Official World Cup 2026 data lock completed.\n\n"
    "Step 17B: Official squads and player priors merge completed.\n\n"
    "Step 17C: Official final readiness workflow completed.\n\n"
    "Step 17D: Official data population pack completed.\n\n"
    "Step 17E: Source-assisted official FIFA data population completed.\n\n"
    "Step 17F: Official FIFA data population workflow completed.\n\n"
    "Step 17G: Official data import execution workflow completed.\n\n"
    "Step 17H: Official data apply blocker cleanup completed.\n\n"
    "Step 18: FIFA World Cup Awards Predictor completed."
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

st.subheader("Step 14: Full Tournament Single-Run Outputs")
step14_rows = [
    {
        "file": FULL_TOURNAMENT_SIMULATED_MATCHES_FILE,
        "path": str(PROCESSED_DATA_DIR / FULL_TOURNAMENT_SIMULATED_MATCHES_FILE),
        "present": (PROCESSED_DATA_DIR / FULL_TOURNAMENT_SIMULATED_MATCHES_FILE).is_file(),
    },
    {
        "file": FULL_TOURNAMENT_GROUP_TABLES_FILE,
        "path": str(PROCESSED_DATA_DIR / FULL_TOURNAMENT_GROUP_TABLES_FILE),
        "present": (PROCESSED_DATA_DIR / FULL_TOURNAMENT_GROUP_TABLES_FILE).is_file(),
    },
    {
        "file": FULL_TOURNAMENT_KNOCKOUT_MATCHES_FILE,
        "path": str(PROCESSED_DATA_DIR / FULL_TOURNAMENT_KNOCKOUT_MATCHES_FILE),
        "present": (PROCESSED_DATA_DIR / FULL_TOURNAMENT_KNOCKOUT_MATCHES_FILE).is_file(),
    },
    {
        "file": FULL_TOURNAMENT_STAGE_RESULTS_FILE,
        "path": str(PROCESSED_DATA_DIR / FULL_TOURNAMENT_STAGE_RESULTS_FILE),
        "present": (PROCESSED_DATA_DIR / FULL_TOURNAMENT_STAGE_RESULTS_FILE).is_file(),
    },
    {
        "file": FULL_TOURNAMENT_PATH_REPORT_FILE,
        "path": str(PROCESSED_DATA_DIR / FULL_TOURNAMENT_PATH_REPORT_FILE),
        "present": (PROCESSED_DATA_DIR / FULL_TOURNAMENT_PATH_REPORT_FILE).is_file(),
    },
    {
        "file": FULL_TOURNAMENT_RESULT_FILE,
        "path": str(PROCESSED_DATA_DIR / FULL_TOURNAMENT_RESULT_FILE),
        "present": (PROCESSED_DATA_DIR / FULL_TOURNAMENT_RESULT_FILE).is_file(),
    },
    {
        "file": FULL_TOURNAMENT_SUMMARY_FILE,
        "path": str(PROCESSED_DATA_DIR / FULL_TOURNAMENT_SUMMARY_FILE),
        "present": (PROCESSED_DATA_DIR / FULL_TOURNAMENT_SUMMARY_FILE).is_file(),
    },
    {
        "file": FULL_TOURNAMENT_VALIDATION_REPORT_FILE,
        "path": str(PROCESSED_DATA_DIR / FULL_TOURNAMENT_VALIDATION_REPORT_FILE),
        "present": (PROCESSED_DATA_DIR / FULL_TOURNAMENT_VALIDATION_REPORT_FILE).is_file(),
    },
]
st.dataframe(pd.DataFrame(step14_rows), use_container_width=True)
st.caption("Step 14 connects group + knockout stages into one complete sampled tournament path.")

st.subheader("Step 15: Monte Carlo Simulation Outputs")
step15_rows = [
    {
        "file": MONTE_CARLO_SIMULATION_RESULTS_FILE,
        "path": str(PROCESSED_DATA_DIR / MONTE_CARLO_SIMULATION_RESULTS_FILE),
        "present": (PROCESSED_DATA_DIR / MONTE_CARLO_SIMULATION_RESULTS_FILE).is_file(),
    },
    {
        "file": MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE,
        "path": str(PROCESSED_DATA_DIR / MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE),
        "present": (PROCESSED_DATA_DIR / MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE).is_file(),
    },
    {
        "file": MONTE_CARLO_CHAMPION_PROBABILITIES_FILE,
        "path": str(PROCESSED_DATA_DIR / MONTE_CARLO_CHAMPION_PROBABILITIES_FILE),
        "present": (PROCESSED_DATA_DIR / MONTE_CARLO_CHAMPION_PROBABILITIES_FILE).is_file(),
    },
    {
        "file": MONTE_CARLO_FINALISTS_FILE,
        "path": str(PROCESSED_DATA_DIR / MONTE_CARLO_FINALISTS_FILE),
        "present": (PROCESSED_DATA_DIR / MONTE_CARLO_FINALISTS_FILE).is_file(),
    },
    {
        "file": MONTE_CARLO_SEMIFINALISTS_FILE,
        "path": str(PROCESSED_DATA_DIR / MONTE_CARLO_SEMIFINALISTS_FILE),
        "present": (PROCESSED_DATA_DIR / MONTE_CARLO_SEMIFINALISTS_FILE).is_file(),
    },
    {
        "file": MONTE_CARLO_SUMMARY_FILE,
        "path": str(PROCESSED_DATA_DIR / MONTE_CARLO_SUMMARY_FILE),
        "present": (PROCESSED_DATA_DIR / MONTE_CARLO_SUMMARY_FILE).is_file(),
    },
    {
        "file": MONTE_CARLO_VALIDATION_REPORT_FILE,
        "path": str(PROCESSED_DATA_DIR / MONTE_CARLO_VALIDATION_REPORT_FILE),
        "present": (PROCESSED_DATA_DIR / MONTE_CARLO_VALIDATION_REPORT_FILE).is_file(),
    },
]
st.dataframe(pd.DataFrame(step15_rows), use_container_width=True)
st.caption("Step 15 runs repeated full tournament samples to estimate progression/champion probabilities.")

st.subheader("Step 16: Monte Carlo Dashboard and Report Outputs")
step16_rows = [
    {
        "file": MONTE_CARLO_REPORT_MD_FILE,
        "path": str(REPORTS_DIR / MONTE_CARLO_REPORT_MD_FILE),
        "present": (REPORTS_DIR / MONTE_CARLO_REPORT_MD_FILE).is_file(),
    },
    {
        "file": MONTE_CARLO_SUMMARY_CARDS_FILE,
        "path": str(REPORTS_DIR / MONTE_CARLO_SUMMARY_CARDS_FILE),
        "present": (REPORTS_DIR / MONTE_CARLO_SUMMARY_CARDS_FILE).is_file(),
    },
    {
        "file": MONTE_CARLO_DASHBOARD_EXPORT_FILE,
        "path": str(REPORTS_DIR / MONTE_CARLO_DASHBOARD_EXPORT_FILE),
        "present": (REPORTS_DIR / MONTE_CARLO_DASHBOARD_EXPORT_FILE).is_file(),
    },
    {
        "file": MONTE_CARLO_CHAMPION_CHART_FILE,
        "path": str(FIGURES_DIR / MONTE_CARLO_CHAMPION_CHART_FILE),
        "present": (FIGURES_DIR / MONTE_CARLO_CHAMPION_CHART_FILE).is_file(),
    },
    {
        "file": MONTE_CARLO_STAGE_HEATMAP_FILE,
        "path": str(FIGURES_DIR / MONTE_CARLO_STAGE_HEATMAP_FILE),
        "present": (FIGURES_DIR / MONTE_CARLO_STAGE_HEATMAP_FILE).is_file(),
    },
]
st.dataframe(pd.DataFrame(step16_rows), use_container_width=True)
st.caption("Step 16 adds report artifacts, summary cards, and visuals on top of Monte Carlo outputs.")

st.subheader("Step 17A: Official World Cup 2026 Data Lock Outputs")
step17a_rows = [
    {
        "file": OFFICIAL_TEAMS_FILE,
        "path": str(OFFICIAL_PROCESSED_DIR / OFFICIAL_TEAMS_FILE),
        "present": (OFFICIAL_PROCESSED_DIR / OFFICIAL_TEAMS_FILE).is_file(),
    },
    {
        "file": OFFICIAL_GROUPS_FILE,
        "path": str(OFFICIAL_PROCESSED_DIR / OFFICIAL_GROUPS_FILE),
        "present": (OFFICIAL_PROCESSED_DIR / OFFICIAL_GROUPS_FILE).is_file(),
    },
    {
        "file": OFFICIAL_FIXTURES_FILE,
        "path": str(OFFICIAL_PROCESSED_DIR / OFFICIAL_FIXTURES_FILE),
        "present": (OFFICIAL_PROCESSED_DIR / OFFICIAL_FIXTURES_FILE).is_file(),
    },
    {
        "file": OFFICIAL_VENUES_FILE,
        "path": str(OFFICIAL_PROCESSED_DIR / OFFICIAL_VENUES_FILE),
        "present": (OFFICIAL_PROCESSED_DIR / OFFICIAL_VENUES_FILE).is_file(),
    },
    {
        "file": OFFICIAL_MATCH_CALENDAR_FILE,
        "path": str(OFFICIAL_PROCESSED_DIR / OFFICIAL_MATCH_CALENDAR_FILE),
        "present": (OFFICIAL_PROCESSED_DIR / OFFICIAL_MATCH_CALENDAR_FILE).is_file(),
    },
    {
        "file": OFFICIAL_DATA_SUMMARY_FILE,
        "path": str(OFFICIAL_PROCESSED_DIR / OFFICIAL_DATA_SUMMARY_FILE),
        "present": (OFFICIAL_PROCESSED_DIR / OFFICIAL_DATA_SUMMARY_FILE).is_file(),
    },
    {
        "file": OFFICIAL_DATA_VALIDATION_REPORT_FILE,
        "path": str(OFFICIAL_PROCESSED_DIR / OFFICIAL_DATA_VALIDATION_REPORT_FILE),
        "present": (OFFICIAL_PROCESSED_DIR / OFFICIAL_DATA_VALIDATION_REPORT_FILE).is_file(),
    },
    {
        "file": OFFICIAL_SOURCE_MANIFEST_FILE,
        "path": str(OFFICIAL_PROCESSED_DIR / OFFICIAL_SOURCE_MANIFEST_FILE),
        "present": (OFFICIAL_PROCESSED_DIR / OFFICIAL_SOURCE_MANIFEST_FILE).is_file(),
    },
]
st.dataframe(pd.DataFrame(step17a_rows), use_container_width=True)
st.caption("Step 17A adds an official-data lock so future official-mode predictions and simulations can be constrained to World Cup 2026 data contracts.")

st.subheader("Step 17B: Official Squads and Player Priors Merge Outputs")

OFFICIAL_PLAYERS_FILE = getattr(C, "OFFICIAL_PLAYERS_FILE", "official_players.csv")
OFFICIAL_SQUADS_FILE = getattr(C, "OFFICIAL_SQUADS_FILE", "official_squads.csv")
OFFICIAL_TEAM_PLAYER_MAP_FILE = getattr(C, "OFFICIAL_TEAM_PLAYER_MAP_FILE", "official_team_player_map.csv")
OFFICIAL_SQUAD_SUMMARY_FILE = getattr(C, "OFFICIAL_SQUAD_SUMMARY_FILE", "official_squad_summary.json")
OFFICIAL_SQUAD_VALIDATION_REPORT_FILE = getattr(C, "OFFICIAL_SQUAD_VALIDATION_REPORT_FILE", "official_squad_validation_report.csv")
OFFICIAL_PLAYER_PRIOR_MERGE_REPORT_FILE = getattr(C, "OFFICIAL_PLAYER_PRIOR_MERGE_REPORT_FILE", "official_player_prior_merge_report.csv")
PLAYER_AWARD_PRIORS_FILE = getattr(C, "PLAYER_AWARD_PRIORS_FILE", "player_award_priors.csv")
OFFICIAL_AWARD_CANDIDATES_FILE = getattr(C, "OFFICIAL_AWARD_CANDIDATES_FILE", "official_award_candidates.csv")

step17b_rows = [
    {
        "file": OFFICIAL_PLAYERS_FILE,
        "path": str(OFFICIAL_PROCESSED_DIR / OFFICIAL_PLAYERS_FILE),
        "present": (OFFICIAL_PROCESSED_DIR / OFFICIAL_PLAYERS_FILE).is_file(),
    },
    {
        "file": OFFICIAL_SQUADS_FILE,
        "path": str(OFFICIAL_PROCESSED_DIR / OFFICIAL_SQUADS_FILE),
        "present": (OFFICIAL_PROCESSED_DIR / OFFICIAL_SQUADS_FILE).is_file(),
    },
    {
        "file": OFFICIAL_TEAM_PLAYER_MAP_FILE,
        "path": str(OFFICIAL_PROCESSED_DIR / OFFICIAL_TEAM_PLAYER_MAP_FILE),
        "present": (OFFICIAL_PROCESSED_DIR / OFFICIAL_TEAM_PLAYER_MAP_FILE).is_file(),
    },
    {
        "file": PLAYER_AWARD_PRIORS_FILE,
        "path": str(C.PROJECT_ROOT / C.PROCESSED_DATA_DIR / PLAYER_AWARD_PRIORS_FILE),
        "present": (C.PROJECT_ROOT / C.PROCESSED_DATA_DIR / PLAYER_AWARD_PRIORS_FILE).is_file(),
    },
    {
        "file": OFFICIAL_AWARD_CANDIDATES_FILE,
        "path": str(C.PROJECT_ROOT / C.PROCESSED_DATA_DIR / OFFICIAL_AWARD_CANDIDATES_FILE),
        "present": (C.PROJECT_ROOT / C.PROCESSED_DATA_DIR / OFFICIAL_AWARD_CANDIDATES_FILE).is_file(),
    },
    {
        "file": OFFICIAL_SQUAD_SUMMARY_FILE,
        "path": str(OFFICIAL_PROCESSED_DIR / OFFICIAL_SQUAD_SUMMARY_FILE),
        "present": (OFFICIAL_PROCESSED_DIR / OFFICIAL_SQUAD_SUMMARY_FILE).is_file(),
    },
    {
        "file": OFFICIAL_SQUAD_VALIDATION_REPORT_FILE,
        "path": str(OFFICIAL_PROCESSED_DIR / OFFICIAL_SQUAD_VALIDATION_REPORT_FILE),
        "present": (OFFICIAL_PROCESSED_DIR / OFFICIAL_SQUAD_VALIDATION_REPORT_FILE).is_file(),
    },
    {
        "file": OFFICIAL_PLAYER_PRIOR_MERGE_REPORT_FILE,
        "path": str(OFFICIAL_PROCESSED_DIR / OFFICIAL_PLAYER_PRIOR_MERGE_REPORT_FILE),
        "present": (OFFICIAL_PROCESSED_DIR / OFFICIAL_PLAYER_PRIOR_MERGE_REPORT_FILE).is_file(),
    },
]
st.dataframe(pd.DataFrame(step17b_rows), use_container_width=True)
st.caption("Step 17B adds official squads and editable player priors, merged into official_award_candidates.csv. Only official squad players can enter award predictions in official mode.")

st.subheader("Step 17D: Official Data Population Pack Outputs")

OFFICIAL_POPULATION_GUIDE_FILE = getattr(C, "OFFICIAL_POPULATION_GUIDE_FILE", "official_data_population_guide.md")
OFFICIAL_POPULATION_STATUS_FILE = getattr(C, "OFFICIAL_POPULATION_STATUS_FILE", "official_population_status.json")
OFFICIAL_POPULATION_MISSING_DATA_REPORT_FILE = getattr(C, "OFFICIAL_POPULATION_MISSING_DATA_REPORT_FILE", "official_population_missing_data_report.csv")
OFFICIAL_POPULATION_DIFF_REPORT_FILE = getattr(C, "OFFICIAL_POPULATION_DIFF_REPORT_FILE", "official_population_diff_report.csv")
OFFICIAL_MASTER_IMPORT_WORKBOOK_FILE = getattr(C, "OFFICIAL_MASTER_IMPORT_WORKBOOK_FILE", "official_worldcup_2026_master_import.xlsx")
OFFICIAL_MASTER_IMPORT_README_FILE = getattr(C, "OFFICIAL_MASTER_IMPORT_README_FILE", "official_worldcup_2026_master_import_README.md")
OFFICIAL_FINAL_MODE_FLAG_FILE = getattr(C, "OFFICIAL_FINAL_MODE_FLAG_FILE", "official_final_mode.json")
OFFICIAL_POPULATION_DIR = getattr(C, "OFFICIAL_POPULATION_DIR", "data/official/population")
OFFICIAL_POPULATION_REPORTS_DIR = getattr(C, "OFFICIAL_POPULATION_REPORTS_DIR", "data/official/population/reports")
OFFICIAL_POPULATION_WORKBOOK_DIR = getattr(C, "OFFICIAL_POPULATION_WORKBOOK_DIR", "data/official/population/workbooks")

POPULATION_ROOT = PROJECT_ROOT / str(OFFICIAL_POPULATION_DIR)
POPULATION_REPORTS = PROJECT_ROOT / str(OFFICIAL_POPULATION_REPORTS_DIR)
POPULATION_WORKBOOKS = PROJECT_ROOT / str(OFFICIAL_POPULATION_WORKBOOK_DIR)

step17d_rows = [
    {"file": OFFICIAL_POPULATION_GUIDE_FILE, "path": str(POPULATION_ROOT / OFFICIAL_POPULATION_GUIDE_FILE), "present": (POPULATION_ROOT / OFFICIAL_POPULATION_GUIDE_FILE).is_file()},
    {"file": OFFICIAL_POPULATION_STATUS_FILE, "path": str(POPULATION_ROOT / OFFICIAL_POPULATION_STATUS_FILE), "present": (POPULATION_ROOT / OFFICIAL_POPULATION_STATUS_FILE).is_file()},
    {"file": OFFICIAL_POPULATION_MISSING_DATA_REPORT_FILE, "path": str(POPULATION_REPORTS / OFFICIAL_POPULATION_MISSING_DATA_REPORT_FILE), "present": (POPULATION_REPORTS / OFFICIAL_POPULATION_MISSING_DATA_REPORT_FILE).is_file()},
    {"file": OFFICIAL_POPULATION_DIFF_REPORT_FILE, "path": str(POPULATION_REPORTS / OFFICIAL_POPULATION_DIFF_REPORT_FILE), "present": (POPULATION_REPORTS / OFFICIAL_POPULATION_DIFF_REPORT_FILE).is_file()},
    {"file": OFFICIAL_MASTER_IMPORT_WORKBOOK_FILE, "path": str(POPULATION_WORKBOOKS / OFFICIAL_MASTER_IMPORT_WORKBOOK_FILE), "present": (POPULATION_WORKBOOKS / OFFICIAL_MASTER_IMPORT_WORKBOOK_FILE).is_file()},
    {"file": OFFICIAL_MASTER_IMPORT_README_FILE, "path": str(POPULATION_WORKBOOKS / OFFICIAL_MASTER_IMPORT_README_FILE), "present": (POPULATION_WORKBOOKS / OFFICIAL_MASTER_IMPORT_README_FILE).is_file()},
    {"file": OFFICIAL_FINAL_MODE_FLAG_FILE, "path": str(OFFICIAL_PROCESSED_DIR / OFFICIAL_FINAL_MODE_FLAG_FILE), "present": (OFFICIAL_PROCESSED_DIR / OFFICIAL_FINAL_MODE_FLAG_FILE).is_file()},
]
st.dataframe(pd.DataFrame(step17d_rows), use_container_width=True)
st.caption("Step 17D adds manual population workflow: guides, templates, missing-data reports, import preview/diff, and safe official_final promotion.")

st.subheader("Step 17E: Source-Assisted Official FIFA Data Population Outputs")

OFFICIAL_SOURCE_DATA_DIR = getattr(C, "OFFICIAL_SOURCE_DATA_DIR", "data/official/source_data")
OFFICIAL_SOURCE_STAGING_DIR = getattr(C, "OFFICIAL_SOURCE_STAGING_DIR", "data/official/source_data/staging")
OFFICIAL_SOURCE_REPORTS_DIR = getattr(C, "OFFICIAL_SOURCE_REPORTS_DIR", "data/official/source_data/reports")
OFFICIAL_SOURCE_EXPORTS_DIR = getattr(C, "OFFICIAL_SOURCE_EXPORTS_DIR", "data/official/source_data/exports")
OFFICIAL_SOURCE_REGISTRY_FILE = getattr(C, "OFFICIAL_SOURCE_REGISTRY_FILE", "official_source_registry.json")
OFFICIAL_SOURCE_SNAPSHOT_MANIFEST_FILE = getattr(C, "OFFICIAL_SOURCE_SNAPSHOT_MANIFEST_FILE", "official_source_snapshot_manifest.json")
STAGED_OFFICIAL_TEAMS_FILE = getattr(C, "STAGED_OFFICIAL_TEAMS_FILE", "staged_official_teams.csv")
STAGED_OFFICIAL_FIXTURES_FILE = getattr(C, "STAGED_OFFICIAL_FIXTURES_FILE", "staged_official_fixtures.csv")
STAGED_OFFICIAL_VENUES_FILE = getattr(C, "STAGED_OFFICIAL_VENUES_FILE", "staged_official_venues.csv")
STAGED_OFFICIAL_PLAYERS_FILE = getattr(C, "STAGED_OFFICIAL_PLAYERS_FILE", "staged_official_players.csv")
OFFICIAL_SOURCE_PARSE_REPORT_FILE = getattr(C, "OFFICIAL_SOURCE_PARSE_REPORT_FILE", "official_source_parse_report.csv")
OFFICIAL_STAGING_VALIDATION_REPORT_FILE = getattr(C, "OFFICIAL_STAGING_VALIDATION_REPORT_FILE", "official_staging_validation_report.csv")
OFFICIAL_SOURCE_POPULATION_SUMMARY_FILE = getattr(C, "OFFICIAL_SOURCE_POPULATION_SUMMARY_FILE", "official_source_population_summary.json")
OFFICIAL_DOWNLOADABLE_IMPORT_PACK_FILE = getattr(C, "OFFICIAL_DOWNLOADABLE_IMPORT_PACK_FILE", "official_worldcup_2026_import_pack.zip")

SOURCE_ROOT = PROJECT_ROOT / str(OFFICIAL_SOURCE_DATA_DIR)
SOURCE_STAGING = PROJECT_ROOT / str(OFFICIAL_SOURCE_STAGING_DIR)
SOURCE_REPORTS = PROJECT_ROOT / str(OFFICIAL_SOURCE_REPORTS_DIR)
SOURCE_EXPORTS = PROJECT_ROOT / str(OFFICIAL_SOURCE_EXPORTS_DIR)

step17e_rows = [
    {"file": OFFICIAL_SOURCE_REGISTRY_FILE, "path": str(SOURCE_ROOT / OFFICIAL_SOURCE_REGISTRY_FILE), "present": (SOURCE_ROOT / OFFICIAL_SOURCE_REGISTRY_FILE).is_file()},
    {"file": OFFICIAL_SOURCE_SNAPSHOT_MANIFEST_FILE, "path": str(SOURCE_ROOT / OFFICIAL_SOURCE_SNAPSHOT_MANIFEST_FILE), "present": (SOURCE_ROOT / OFFICIAL_SOURCE_SNAPSHOT_MANIFEST_FILE).is_file()},
    {"file": STAGED_OFFICIAL_TEAMS_FILE, "path": str(SOURCE_STAGING / STAGED_OFFICIAL_TEAMS_FILE), "present": (SOURCE_STAGING / STAGED_OFFICIAL_TEAMS_FILE).is_file()},
    {"file": STAGED_OFFICIAL_FIXTURES_FILE, "path": str(SOURCE_STAGING / STAGED_OFFICIAL_FIXTURES_FILE), "present": (SOURCE_STAGING / STAGED_OFFICIAL_FIXTURES_FILE).is_file()},
    {"file": STAGED_OFFICIAL_VENUES_FILE, "path": str(SOURCE_STAGING / STAGED_OFFICIAL_VENUES_FILE), "present": (SOURCE_STAGING / STAGED_OFFICIAL_VENUES_FILE).is_file()},
    {"file": STAGED_OFFICIAL_PLAYERS_FILE, "path": str(SOURCE_STAGING / STAGED_OFFICIAL_PLAYERS_FILE), "present": (SOURCE_STAGING / STAGED_OFFICIAL_PLAYERS_FILE).is_file()},
    {"file": OFFICIAL_SOURCE_PARSE_REPORT_FILE, "path": str(SOURCE_REPORTS / OFFICIAL_SOURCE_PARSE_REPORT_FILE), "present": (SOURCE_REPORTS / OFFICIAL_SOURCE_PARSE_REPORT_FILE).is_file()},
    {"file": OFFICIAL_STAGING_VALIDATION_REPORT_FILE, "path": str(SOURCE_REPORTS / OFFICIAL_STAGING_VALIDATION_REPORT_FILE), "present": (SOURCE_REPORTS / OFFICIAL_STAGING_VALIDATION_REPORT_FILE).is_file()},
    {"file": OFFICIAL_SOURCE_POPULATION_SUMMARY_FILE, "path": str(SOURCE_REPORTS / OFFICIAL_SOURCE_POPULATION_SUMMARY_FILE), "present": (SOURCE_REPORTS / OFFICIAL_SOURCE_POPULATION_SUMMARY_FILE).is_file()},
    {"file": OFFICIAL_DOWNLOADABLE_IMPORT_PACK_FILE, "path": str(SOURCE_EXPORTS / OFFICIAL_DOWNLOADABLE_IMPORT_PACK_FILE), "present": (SOURCE_EXPORTS / OFFICIAL_DOWNLOADABLE_IMPORT_PACK_FILE).is_file()},
]
st.dataframe(pd.DataFrame(step17e_rows), use_container_width=True)
st.caption("Step 17E stages official FIFA source data for review; official_final stays blocked until readiness passes.")

st.subheader("Step 17F: Populate Official FIFA World Cup Data Outputs")

OFFICIAL_POPULATED_DATA_DIR = getattr(C, "OFFICIAL_POPULATED_DATA_DIR", "data/official/populated")
OFFICIAL_POPULATED_REPORTS_DIR = getattr(C, "OFFICIAL_POPULATED_REPORTS_DIR", "data/official/populated/reports")
OFFICIAL_POPULATED_EXPORTS_DIR = getattr(C, "OFFICIAL_POPULATED_EXPORTS_DIR", "data/official/populated/exports")
POPULATED_OFFICIAL_TEAMS_FILE = getattr(C, "POPULATED_OFFICIAL_TEAMS_FILE", "populated_official_teams.csv")
POPULATED_OFFICIAL_GROUPS_FILE = getattr(C, "POPULATED_OFFICIAL_GROUPS_FILE", "populated_official_groups.csv")
POPULATED_OFFICIAL_FIXTURES_FILE = getattr(C, "POPULATED_OFFICIAL_FIXTURES_FILE", "populated_official_fixtures.csv")
POPULATED_OFFICIAL_VENUES_FILE = getattr(C, "POPULATED_OFFICIAL_VENUES_FILE", "populated_official_venues.csv")
POPULATED_OFFICIAL_PLAYERS_FILE = getattr(C, "POPULATED_OFFICIAL_PLAYERS_FILE", "populated_official_players.csv")
POPULATED_PLAYER_AWARD_PRIORS_FILE = getattr(C, "POPULATED_PLAYER_AWARD_PRIORS_FILE", "populated_player_award_priors.csv")
OFFICIAL_POPULATION_COMPLETENESS_REPORT_FILE = getattr(
    C, "OFFICIAL_POPULATION_COMPLETENESS_REPORT_FILE", "official_population_completeness_report.csv"
)
OFFICIAL_POPULATION_FINAL_SUMMARY_FILE = getattr(
    C, "OFFICIAL_POPULATION_FINAL_SUMMARY_FILE", "official_population_final_summary.json"
)
OFFICIAL_READY_IMPORT_PACK_FILE = getattr(C, "OFFICIAL_READY_IMPORT_PACK_FILE", "official_ready_import_pack.zip")

POP_ROOT = PROJECT_ROOT / str(OFFICIAL_POPULATED_DATA_DIR)
POP_REPORTS = PROJECT_ROOT / str(OFFICIAL_POPULATED_REPORTS_DIR)
POP_EXPORTS = PROJECT_ROOT / str(OFFICIAL_POPULATED_EXPORTS_DIR)

step17f_rows = [
    {"file": POPULATED_OFFICIAL_TEAMS_FILE, "path": str(POP_ROOT / POPULATED_OFFICIAL_TEAMS_FILE), "present": (POP_ROOT / POPULATED_OFFICIAL_TEAMS_FILE).is_file()},
    {"file": POPULATED_OFFICIAL_GROUPS_FILE, "path": str(POP_ROOT / POPULATED_OFFICIAL_GROUPS_FILE), "present": (POP_ROOT / POPULATED_OFFICIAL_GROUPS_FILE).is_file()},
    {"file": POPULATED_OFFICIAL_FIXTURES_FILE, "path": str(POP_ROOT / POPULATED_OFFICIAL_FIXTURES_FILE), "present": (POP_ROOT / POPULATED_OFFICIAL_FIXTURES_FILE).is_file()},
    {"file": POPULATED_OFFICIAL_VENUES_FILE, "path": str(POP_ROOT / POPULATED_OFFICIAL_VENUES_FILE), "present": (POP_ROOT / POPULATED_OFFICIAL_VENUES_FILE).is_file()},
    {"file": POPULATED_OFFICIAL_PLAYERS_FILE, "path": str(POP_ROOT / POPULATED_OFFICIAL_PLAYERS_FILE), "present": (POP_ROOT / POPULATED_OFFICIAL_PLAYERS_FILE).is_file()},
    {"file": POPULATED_PLAYER_AWARD_PRIORS_FILE, "path": str(POP_ROOT / POPULATED_PLAYER_AWARD_PRIORS_FILE), "present": (POP_ROOT / POPULATED_PLAYER_AWARD_PRIORS_FILE).is_file()},
    {"file": OFFICIAL_POPULATION_COMPLETENESS_REPORT_FILE, "path": str(POP_REPORTS / OFFICIAL_POPULATION_COMPLETENESS_REPORT_FILE), "present": (POP_REPORTS / OFFICIAL_POPULATION_COMPLETENESS_REPORT_FILE).is_file()},
    {"file": OFFICIAL_POPULATION_FINAL_SUMMARY_FILE, "path": str(POP_REPORTS / OFFICIAL_POPULATION_FINAL_SUMMARY_FILE), "present": (POP_REPORTS / OFFICIAL_POPULATION_FINAL_SUMMARY_FILE).is_file()},
    {"file": OFFICIAL_READY_IMPORT_PACK_FILE, "path": str(POP_EXPORTS / OFFICIAL_READY_IMPORT_PACK_FILE), "present": (POP_EXPORTS / OFFICIAL_READY_IMPORT_PACK_FILE).is_file()},
]
st.dataframe(pd.DataFrame(step17f_rows), use_container_width=True)
st.caption("Step 17F builds populated import files from FIFA sources; apply only when completeness checks pass.")

st.subheader("Step 17G: Official Data Import Execution Outputs")

OFFICIAL_IMPORT_EXECUTION_SUMMARY_FILE = getattr(
    C, "OFFICIAL_IMPORT_EXECUTION_SUMMARY_FILE", "official_import_execution_summary.json"
)
OFFICIAL_FINAL_READINESS_REPORT_FILE = getattr(
    C, "OFFICIAL_FINAL_READINESS_REPORT_FILE", "official_final_readiness_report.json"
)
OFFICIAL_FINAL_READINESS_CHECKLIST_FILE = getattr(
    C, "OFFICIAL_FINAL_READINESS_CHECKLIST_FILE", "official_final_readiness_checklist.csv"
)

step17g_rows = [
    {
        "file": OFFICIAL_IMPORT_EXECUTION_SUMMARY_FILE,
        "path": str(POP_REPORTS / OFFICIAL_IMPORT_EXECUTION_SUMMARY_FILE),
        "present": (POP_REPORTS / OFFICIAL_IMPORT_EXECUTION_SUMMARY_FILE).is_file(),
    },
    {
        "file": OFFICIAL_POPULATION_COMPLETENESS_REPORT_FILE,
        "path": str(POP_REPORTS / OFFICIAL_POPULATION_COMPLETENESS_REPORT_FILE),
        "present": (POP_REPORTS / OFFICIAL_POPULATION_COMPLETENESS_REPORT_FILE).is_file(),
    },
    {
        "file": OFFICIAL_FINAL_READINESS_REPORT_FILE,
        "path": str(OFFICIAL_PROCESSED_DIR / OFFICIAL_FINAL_READINESS_REPORT_FILE),
        "present": (OFFICIAL_PROCESSED_DIR / OFFICIAL_FINAL_READINESS_REPORT_FILE).is_file(),
    },
    {
        "file": OFFICIAL_FINAL_READINESS_CHECKLIST_FILE,
        "path": str(OFFICIAL_PROCESSED_DIR / OFFICIAL_FINAL_READINESS_CHECKLIST_FILE),
        "present": (OFFICIAL_PROCESSED_DIR / OFFICIAL_FINAL_READINESS_CHECKLIST_FILE).is_file(),
    },
]
st.dataframe(pd.DataFrame(step17g_rows), use_container_width=True)
st.caption("Step 17G runs staging, preview, optional apply, and final readiness — without forcing official_final.")

st.subheader("Step 18: FIFA World Cup Awards Predictor Outputs")
step18_rows = [
    {
        "file": WORLD_CUP_AWARDS_PREDICTIONS_FILE,
        "path": str(PROCESSED_DATA_DIR / WORLD_CUP_AWARDS_PREDICTIONS_FILE),
        "present": (PROCESSED_DATA_DIR / WORLD_CUP_AWARDS_PREDICTIONS_FILE).is_file(),
    },
    {
        "file": GOLDEN_BALL_PREDICTIONS_FILE,
        "path": str(PROCESSED_DATA_DIR / GOLDEN_BALL_PREDICTIONS_FILE),
        "present": (PROCESSED_DATA_DIR / GOLDEN_BALL_PREDICTIONS_FILE).is_file(),
    },
    {
        "file": GOLDEN_BOOT_PREDICTIONS_FILE,
        "path": str(PROCESSED_DATA_DIR / GOLDEN_BOOT_PREDICTIONS_FILE),
        "present": (PROCESSED_DATA_DIR / GOLDEN_BOOT_PREDICTIONS_FILE).is_file(),
    },
    {
        "file": GOLDEN_GLOVE_PREDICTIONS_FILE,
        "path": str(PROCESSED_DATA_DIR / GOLDEN_GLOVE_PREDICTIONS_FILE),
        "present": (PROCESSED_DATA_DIR / GOLDEN_GLOVE_PREDICTIONS_FILE).is_file(),
    },
    {
        "file": YOUNG_PLAYER_PREDICTIONS_FILE,
        "path": str(PROCESSED_DATA_DIR / YOUNG_PLAYER_PREDICTIONS_FILE),
        "present": (PROCESSED_DATA_DIR / YOUNG_PLAYER_PREDICTIONS_FILE).is_file(),
    },
    {
        "file": FAIR_PLAY_PREDICTIONS_FILE,
        "path": str(PROCESSED_DATA_DIR / FAIR_PLAY_PREDICTIONS_FILE),
        "present": (PROCESSED_DATA_DIR / FAIR_PLAY_PREDICTIONS_FILE).is_file(),
    },
    {
        "file": MOST_ENTERTAINING_TEAM_PREDICTIONS_FILE,
        "path": str(PROCESSED_DATA_DIR / MOST_ENTERTAINING_TEAM_PREDICTIONS_FILE),
        "present": (PROCESSED_DATA_DIR / MOST_ENTERTAINING_TEAM_PREDICTIONS_FILE).is_file(),
    },
    {
        "file": TEAM_OF_THE_TOURNAMENT_FILE,
        "path": str(PROCESSED_DATA_DIR / TEAM_OF_THE_TOURNAMENT_FILE),
        "present": (PROCESSED_DATA_DIR / TEAM_OF_THE_TOURNAMENT_FILE).is_file(),
    },
    {
        "file": WORLD_CUP_AWARDS_SUMMARY_FILE,
        "path": str(PROCESSED_DATA_DIR / WORLD_CUP_AWARDS_SUMMARY_FILE),
        "present": (PROCESSED_DATA_DIR / WORLD_CUP_AWARDS_SUMMARY_FILE).is_file(),
    },
    {
        "file": WORLD_CUP_AWARDS_VALIDATION_REPORT_FILE,
        "path": str(PROCESSED_DATA_DIR / WORLD_CUP_AWARDS_VALIDATION_REPORT_FILE),
        "present": (PROCESSED_DATA_DIR / WORLD_CUP_AWARDS_VALIDATION_REPORT_FILE).is_file(),
    },
    {
        "file": WORLD_CUP_AWARDS_REPORT_FILE,
        "path": str(Path("reports") / WORLD_CUP_AWARDS_REPORT_FILE),
        "present": (Path("reports") / WORLD_CUP_AWARDS_REPORT_FILE).is_file(),
    },
]
st.dataframe(pd.DataFrame(step18_rows), use_container_width=True)
st.caption(
    "Step 18 requires official_final=true. Uses official_award_candidates.csv and Monte Carlo progression. "
    "Outputs are explainable analytics estimates, not official FIFA predictions."
)

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
    - **Official Data Health** — official-style data contracts, validation reports, and sample-vs-official mode visibility.
    - **World Cup Awards Predictor** — Golden Ball, Golden Boot, Golden Glove, and team awards using official squads (Step 18).
    - **Model Explanation** — feature importance, SHAP values, calibration.
    """
)

st.info("Use the sidebar to navigate between the placeholder module pages.")

st.caption(
    "Disclaimer: This is an educational sports-analytics project. "
    "It is not betting advice."
)
