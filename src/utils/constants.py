"""Project-wide constants.

Centralizing constants here keeps the rest of the codebase free of magic
strings and numbers.
"""

from __future__ import annotations

from pathlib import Path

PROJECT_NAME: str = "FIFA World Cup 2026 AI Predictor"

RANDOM_SEED: int = 42

# Match result encoding (from team_a's perspective).
RESULT_LABELS: dict[int, str] = {
    0: "team_a_loss",
    1: "draw",
    2: "team_a_win",
}

# Tournament stages used by the simulator.
TOURNAMENT_STAGES: list[str] = [
    "group_stage",
    "round_of_32",
    "round_of_16",
    "quarter_final",
    "semi_final",
    "third_place",
    "final",
]

# FIFA World Cup 2026 host nations.
WORLD_CUP_2026_HOSTS: list[str] = [
    "Canada",
    "Mexico",
    "United States",
]

# Minimum columns required to treat a DataFrame as match data (canonical form).
BASIC_REQUIRED_MATCH_COLUMNS: list[str] = [
    "date",
    "team_a",
    "team_b",
    "team_a_score",
    "team_b_score",
]

# -----------------------------------------------------------------------------
# Path constants
# -----------------------------------------------------------------------------

# Project root = .../world-cup-2026-ai-predictor
PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]

DATA_DIR: Path = PROJECT_ROOT / "data"

RAW_MATCHES_DIR: Path = DATA_DIR / "raw" / "matches"
RAW_RANKINGS_DIR: Path = DATA_DIR / "raw" / "rankings"
RAW_WORLD_CUP_2026_DIR: Path = DATA_DIR / "raw" / "world_cup_2026"

SAMPLE_DATA_DIR: Path = DATA_DIR / "sample"
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
EXTERNAL_DATA_DIR: Path = DATA_DIR / "external"

# -----------------------------------------------------------------------------
# Expected real-dataset file names (placed under data/raw/...)
# -----------------------------------------------------------------------------

HISTORICAL_RESULTS_FILE: str = "results.csv"
SHOOTOUTS_FILE: str = "shootouts.csv"
FIFA_RANKINGS_FILE: str = "fifa_rankings.csv"
ELO_RATINGS_FILE: str = "elo_ratings.csv"
WC2026_TEAMS_FILE: str = "world_cup_2026_teams.csv"
WC2026_GROUPS_FILE: str = "world_cup_2026_groups.csv"
WC2026_SCHEDULE_FILE: str = "world_cup_2026_schedule.csv"

# -----------------------------------------------------------------------------
# Required column lists per dataset
# -----------------------------------------------------------------------------

HISTORICAL_RESULTS_REQUIRED_COLUMNS: list[str] = [
    "date",
    "home_team",
    "away_team",
    "home_score",
    "away_score",
    "tournament",
    "city",
    "country",
    "neutral",
]

FIFA_RANKINGS_REQUIRED_COLUMNS: list[str] = [
    "rank",
    "team",
    "team_code",
    "points",
    "ranking_date",
]

ELO_RATINGS_REQUIRED_COLUMNS: list[str] = [
    "rank",
    "team",
    "elo",
    "rating_date",
]

WC2026_TEAMS_REQUIRED_COLUMNS: list[str] = [
    "team",
    "confederation",
    "is_host",
    "qualified",
    "qualification_method",
]

WC2026_GROUPS_REQUIRED_COLUMNS: list[str] = [
    "group",
    "team",
    "pot",
]

WC2026_SCHEDULE_REQUIRED_COLUMNS: list[str] = [
    "match_id",
    "stage",
    "group",
    "date",
    "venue",
    "city",
    "country",
    "team_a",
    "team_b",
]

# -----------------------------------------------------------------------------
# Step 3 processed-output file names
# -----------------------------------------------------------------------------

CANONICAL_MATCHES_FILE: str = "canonical_matches.csv"
CANONICAL_MATCHES_SAMPLE_FILE: str = "canonical_matches_sample.csv"
TEAM_REGISTRY_FILE: str = "team_registry.csv"
SHOOTOUT_OUTCOMES_FILE: str = "shootout_outcomes.csv"
DATA_QUALITY_REPORT_FILE: str = "data_quality_report.csv"
CLEANING_SUMMARY_FILE: str = "cleaning_summary.json"

# Full canonical match schema produced by the Step 3 cleaning pipeline.
CANONICAL_MATCH_COLUMNS: list[str] = [
    "match_id",
    "date",
    "year",
    "team_a",
    "team_b",
    "team_a_score",
    "team_b_score",
    "score_difference",
    "total_goals",
    "result",
    "result_label",
    "winner",
    "loser",
    "is_draw",
    "tournament",
    "city",
    "country",
    "neutral",
    "has_shootout",
    "shootout_winner",
    "shootout_loser",
    "progression_winner",
    "data_source",
]

# Columns for the cleaned shootout-outcomes table.
SHOOTOUT_OUTCOME_COLUMNS: list[str] = [
    "date",
    "team_a",
    "team_b",
    "shootout_winner",
    "shootout_loser",
]

# Columns for the team registry.
TEAM_REGISTRY_COLUMNS: list[str] = [
    "team_id",
    "team",
    "team_slug",
    "first_match_date",
    "last_match_date",
    "matches_played",
    "is_world_cup_2026_host",
]

# -----------------------------------------------------------------------------
# Step 4 feature-engineering constants
# -----------------------------------------------------------------------------

FEATURE_DATASET_FILE: str = "feature_dataset.csv"
FEATURE_DATASET_SAMPLE_FILE: str = "feature_dataset_sample.csv"
FEATURE_QUALITY_REPORT_FILE: str = "feature_quality_report.csv"
FEATURE_SUMMARY_FILE: str = "feature_summary.json"

RECENT_FORM_WINDOWS: list[int] = [5, 10]

WORLD_CUP_TOURNAMENT_KEYWORDS: list[str] = [
    "FIFA World Cup",
]

WORLD_CUP_QUALIFIER_KEYWORDS: list[str] = [
    "FIFA World Cup qualification",
    "World Cup qualification",
]

FRIENDLY_KEYWORDS: list[str] = [
    "Friendly",
]

CONTINENTAL_TOURNAMENT_KEYWORDS: list[str] = [
    "UEFA Euro",
    "Copa América",
    "Copa America",
    "African Cup of Nations",
    "AFC Asian Cup",
    "CONCACAF Gold Cup",
    "Oceania Nations Cup",
    "UEFA Nations League",
]

MAJOR_TOURNAMENT_KEYWORDS: list[str] = [
    "FIFA World Cup",
    "UEFA Euro",
    "Copa América",
    "Copa America",
    "African Cup of Nations",
    "AFC Asian Cup",
    "CONCACAF Gold Cup",
]

# Helpful for lightweight inspection and validation.
BASIC_FEATURE_COLUMNS: list[str] = [
    "match_id",
    "date",
    "year",
    "team_a",
    "team_b",
    "tournament",
    "city",
    "country",
    "neutral",
    "result",
    "result_label",
    "progression_winner",
]

# -----------------------------------------------------------------------------
# Step 5 baseline model constants
# -----------------------------------------------------------------------------

BASELINE_MODEL_DIR: str = "models/baseline"

DUMMY_MODEL_FILE: str = "dummy_classifier.joblib"
LOGISTIC_REGRESSION_MODEL_FILE: str = "logistic_regression.joblib"
RANDOM_FOREST_MODEL_FILE: str = "random_forest.joblib"
BEST_BASELINE_MODEL_FILE: str = "best_baseline_model.joblib"

FEATURE_COLUMNS_FILE: str = "feature_columns.json"
MODEL_METADATA_FILE: str = "model_metadata.json"

MODEL_METRICS_FILE: str = "model_metrics.csv"
CLASSIFICATION_REPORT_DUMMY_FILE: str = "classification_report_dummy.csv"
CLASSIFICATION_REPORT_LOGISTIC_FILE: str = (
    "classification_report_logistic_regression.csv"
)
CLASSIFICATION_REPORT_RF_FILE: str = "classification_report_random_forest.csv"

CONFUSION_MATRIX_DUMMY_FILE: str = "confusion_matrix_dummy.csv"
CONFUSION_MATRIX_LOGISTIC_FILE: str = "confusion_matrix_logistic_regression.csv"
CONFUSION_MATRIX_RF_FILE: str = "confusion_matrix_random_forest.csv"

FEATURE_IMPORTANCE_RF_FILE: str = "feature_importance_random_forest.csv"

TARGET_COLUMN: str = "result"
TARGET_LABEL_COLUMN: str = "result_label"
TARGET_CLASS_ORDER: list[int] = [0, 1, 2]

DEFAULT_TEST_START_DATE: str = "2022-01-01"

LEAKAGE_COLUMNS: list[str] = [
    "team_a_score",
    "team_b_score",
    "score_difference",
    "total_goals",
    "winner",
    "loser",
    "is_draw",
    "has_shootout",
    "shootout_winner",
    "shootout_loser",
    "progression_winner",
    "result",
    "result_label",
]

NON_FEATURE_COLUMNS: list[str] = [
    "match_id",
    "date",
    "year",
    "team_a",
    "team_b",
    "tournament",
    "city",
    "country",
    "data_source",
]

# -----------------------------------------------------------------------------
# Step 6 improved model constants
# -----------------------------------------------------------------------------

IMPROVED_MODEL_DIR: str = "models/improved"

XGBOOST_MODEL_FILE: str = "xgboost_model.joblib"
LIGHTGBM_MODEL_FILE: str = "lightgbm_model.joblib"
HIST_GRADIENT_BOOSTING_MODEL_FILE: str = "hist_gradient_boosting_model.joblib"

CALIBRATED_RANDOM_FOREST_FILE: str = "calibrated_random_forest.joblib"
CALIBRATED_XGBOOST_FILE: str = "calibrated_xgboost.joblib"
CALIBRATED_LIGHTGBM_FILE: str = "calibrated_lightgbm.joblib"
CALIBRATED_HIST_GB_FILE: str = "calibrated_hist_gradient_boosting.joblib"

BEST_IMPROVED_MODEL_FILE: str = "best_improved_model.joblib"
IMPROVED_FEATURE_COLUMNS_FILE: str = "improved_feature_columns.json"
IMPROVED_MODEL_METADATA_FILE: str = "improved_model_metadata.json"

IMPROVED_MODEL_METRICS_FILE: str = "improved_model_metrics.csv"
BASELINE_VS_IMPROVED_METRICS_FILE: str = "baseline_vs_improved_metrics.csv"
TEMPORAL_BACKTEST_RESULTS_FILE: str = "temporal_backtest_results.csv"
CALIBRATION_REPORT_FILE: str = "calibration_report.csv"
PROBABILITY_QUALITY_REPORT_FILE: str = "probability_quality_report.csv"
IMPROVED_FEATURE_IMPORTANCE_FILE: str = "improved_feature_importance.csv"
MODEL_COMPARISON_SUMMARY_FILE: str = "model_comparison_summary.json"

BACKTEST_WINDOWS: list[dict[str, str]] = [
    {"name": "test_2018_onward", "test_start_date": "2018-01-01"},
    {"name": "test_2020_onward", "test_start_date": "2020-01-01"},
    {"name": "test_2022_onward", "test_start_date": "2022-01-01"},
    {"name": "test_2024_onward", "test_start_date": "2024-01-01"},
]

CALIBRATION_METHODS: list[str] = ["sigmoid"]
DEFAULT_CALIBRATION_METHOD: str = "sigmoid"

# -----------------------------------------------------------------------------
# Step 7 ranking + Elo integration constants
# -----------------------------------------------------------------------------

RANKING_FEATURE_DATASET_FILE: str = "ranking_feature_dataset.csv"
RANKING_FEATURE_DATASET_SAMPLE_FILE: str = "ranking_feature_dataset_sample.csv"
RANKING_MERGE_REPORT_FILE: str = "ranking_merge_report.csv"
RANKING_FEATURE_SUMMARY_FILE: str = "ranking_feature_summary.json"
TEAM_STRENGTH_SNAPSHOT_FILE: str = "team_strength_snapshot.csv"

RANKING_ENHANCED_MODEL_DIR: str = "models/ranking_enhanced"

RANKING_ENHANCED_MODEL_FILE: str = "ranking_enhanced_model.joblib"
BEST_RANKING_ENHANCED_MODEL_FILE: str = "best_ranking_enhanced_model.joblib"
RANKING_FEATURE_COLUMNS_FILE: str = "ranking_feature_columns.json"
RANKING_MODEL_METADATA_FILE: str = "ranking_model_metadata.json"

RANKING_ENHANCED_MODEL_METRICS_FILE: str = "ranking_enhanced_model_metrics.csv"
RANKING_VS_PREVIOUS_METRICS_FILE: str = "ranking_vs_previous_metrics.csv"
RANKING_FEATURE_IMPORTANCE_FILE: str = "ranking_feature_importance.csv"
RANKING_MODEL_SUMMARY_FILE: str = "ranking_model_summary.json"

FIFA_RANKING_FEATURE_COLUMNS: list[str] = [
    "team_a_fifa_rank",
    "team_b_fifa_rank",
    "diff_fifa_rank",
    "team_a_fifa_points",
    "team_b_fifa_points",
    "diff_fifa_points",
    "team_a_has_fifa_ranking",
    "team_b_has_fifa_ranking",
]

ELO_FEATURE_COLUMNS: list[str] = [
    "team_a_elo_rank",
    "team_b_elo_rank",
    "diff_elo_rank",
    "team_a_elo",
    "team_b_elo",
    "diff_elo",
    "team_a_has_elo",
    "team_b_has_elo",
]

TEAM_STRENGTH_FEATURE_COLUMNS: list[str] = [
    "team_a_strength_score",
    "team_b_strength_score",
    "diff_strength_score",
]

RANKING_SNAPSHOT_MODE: str = "snapshot"
RANKING_HISTORICAL_MODE: str = "historical"

# -----------------------------------------------------------------------------
# Step 8 future match feature generation + prediction constants
# -----------------------------------------------------------------------------

FUTURE_PREDICTION_REPORT_FILE: str = "future_prediction_report.csv"
FUTURE_PREDICTION_LOG_FILE: str = "future_prediction_log.csv"

DEFAULT_FUTURE_MATCH_DATE: str = "2026-06-11"
DEFAULT_FUTURE_TOURNAMENT: str = "FIFA World Cup"
DEFAULT_FUTURE_CITY: str = "Unknown"
DEFAULT_FUTURE_COUNTRY: str = "Unknown"
DEFAULT_FUTURE_NEUTRAL: int = 1

MODEL_PREFERENCE_ORDER: list[str] = [
    "ranking_enhanced",
    "improved",
    "baseline",
]

# -----------------------------------------------------------------------------
# Step 9/10 prediction-reporting + explainability constants
# -----------------------------------------------------------------------------

PREDICTION_HISTORY_FILE: str = "prediction_history.csv"
LATEST_PREDICTION_REPORT_FILE: str = "latest_prediction_report.csv"
PREDICTION_EXPLANATION_COLUMNS: list[str] = [
    "team_a",
    "team_b",
    "match_date",
    "model_type",
    "predicted_label",
    "confidence_label",
    "top_supporting_factors",
    "top_opposing_factors",
]

HIGH_CONFIDENCE_THRESHOLD: float = 0.60
MEDIUM_CONFIDENCE_THRESHOLD: float = 0.45

EXPLANATION_REPORT_FILE: str = "prediction_explanation_report.csv"
EXPLANATION_HISTORY_FILE: str = "prediction_explanation_history.csv"
GLOBAL_EXPLANATION_REPORT_FILE: str = "global_model_explanation.csv"

TOP_EXPLANATION_FEATURES: int = 10

EXPLANATION_METHOD_SHAP: str = "shap"
EXPLANATION_METHOD_PERMUTATION: str = "permutation"
EXPLANATION_METHOD_FEATURE_IMPORTANCE: str = "feature_importance"
EXPLANATION_METHOD_FALLBACK: str = "fallback"

READABLE_FEATURE_NAMES: dict[str, str] = {
    "team_a_last_5_win_rate": "Team A recent win rate",
    "team_b_last_5_win_rate": "Team B recent win rate",
    "diff_last_5_win_rate": "Recent win-rate advantage",
    "team_a_goals_scored_avg_before": "Team A historical goals scored average",
    "team_b_goals_scored_avg_before": "Team B historical goals scored average",
    "diff_goal_diff_avg_before": "Historical goal-difference advantage",
    "team_a_fifa_rank": "Team A FIFA rank",
    "team_b_fifa_rank": "Team B FIFA rank",
    "diff_fifa_rank": "FIFA ranking advantage",
    "team_a_elo": "Team A Elo rating",
    "team_b_elo": "Team B Elo rating",
    "diff_elo": "Elo rating advantage",
    "diff_strength_score": "Overall team-strength advantage",
}

# -----------------------------------------------------------------------------
# Step 11 tournament fixture/group setup constants
# -----------------------------------------------------------------------------

WC2026_GROUPS: list[str] = [
    "A", "B", "C", "D", "E", "F",
    "G", "H", "I", "J", "K", "L",
]

WC2026_TEAMS_PER_GROUP: int = 4
WC2026_GROUP_MATCHES_PER_GROUP: int = 6
WC2026_TOTAL_GROUP_MATCHES: int = 72
WC2026_TOTAL_TEAMS: int = 48
WC2026_QUALIFIED_FROM_GROUP_TOP_N: int = 2
WC2026_BEST_THIRD_PLACED_QUALIFIERS: int = 8

TOURNAMENT_GROUPS_FILE: str = "tournament_groups.csv"
TOURNAMENT_FIXTURES_FILE: str = "tournament_fixtures.csv"
TOURNAMENT_STRUCTURE_FILE: str = "tournament_structure.json"
TOURNAMENT_VALIDATION_REPORT_FILE: str = "tournament_validation_report.csv"
KNOCKOUT_PLACEHOLDER_FILE: str = "knockout_placeholders.csv"

TOURNAMENT_STAGE_GROUP: str = "group_stage"
TOURNAMENT_STAGE_ROUND_OF_32: str = "round_of_32"
TOURNAMENT_STAGE_ROUND_OF_16: str = "round_of_16"
TOURNAMENT_STAGE_QUARTER_FINAL: str = "quarter_final"
TOURNAMENT_STAGE_SEMI_FINAL: str = "semi_final"
TOURNAMENT_STAGE_THIRD_PLACE: str = "third_place"
TOURNAMENT_STAGE_FINAL: str = "final"

# -----------------------------------------------------------------------------
# Step 12 group-stage simulation constants
# -----------------------------------------------------------------------------

GROUP_STAGE_SIMULATED_MATCHES_FILE: str = "group_stage_simulated_matches.csv"
GROUP_STAGE_TABLES_FILE: str = "group_stage_tables.csv"
GROUP_STAGE_RANKINGS_FILE: str = "group_stage_rankings.csv"
BEST_THIRD_PLACED_TEAMS_FILE: str = "best_third_placed_teams.csv"
ROUND_OF_32_QUALIFIERS_FILE: str = "round_of_32_qualifiers.csv"
GROUP_STAGE_SIMULATION_SUMMARY_FILE: str = "group_stage_simulation_summary.json"
GROUP_STAGE_SIMULATION_VALIDATION_REPORT_FILE: str = "group_stage_simulation_validation_report.csv"

SCORELINE_TEMPLATES: dict[str, list[tuple[int, int]]] = {
    "team_a_win": [(1, 0), (2, 0), (2, 1), (3, 1), (3, 2)],
    "draw": [(0, 0), (1, 1), (2, 2)],
    "team_a_loss": [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)],
}

GROUP_TABLE_COLUMNS: list[str] = [
    "group",
    "team",
    "played",
    "wins",
    "draws",
    "losses",
    "goals_for",
    "goals_against",
    "goal_difference",
    "points",
    "group_rank",
]

# -----------------------------------------------------------------------------
# Step 13 knockout simulation constants
# -----------------------------------------------------------------------------

KNOCKOUT_BRACKET_FILLED_FILE: str = "knockout_bracket_filled.csv"
KNOCKOUT_SIMULATED_MATCHES_FILE: str = "knockout_simulated_matches.csv"
SINGLE_TOURNAMENT_RESULT_FILE: str = "single_tournament_result.json"
KNOCKOUT_SIMULATION_SUMMARY_FILE: str = "knockout_simulation_summary.json"
KNOCKOUT_SIMULATION_VALIDATION_REPORT_FILE: str = "knockout_simulation_validation_report.csv"

KNOCKOUT_ROUNDS: list[str] = [
    "round_of_32",
    "round_of_16",
    "quarter_final",
    "semi_final",
    "third_place",
    "final",
]

KNOCKOUT_ROUND_MATCH_COUNTS: dict[str, int] = {
    "round_of_32": 16,
    "round_of_16": 8,
    "quarter_final": 4,
    "semi_final": 2,
    "third_place": 1,
    "final": 1,
}

KNOCKOUT_SCORELINE_TEMPLATES: dict[str, list[tuple[int, int]]] = {
    "team_a_win_regular": [(1, 0), (2, 0), (2, 1), (3, 1), (3, 2)],
    "team_b_win_regular": [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)],
    "team_a_win_extra": [(1, 1), (2, 2), (0, 0)],
    "team_b_win_extra": [(1, 1), (2, 2), (0, 0)],
}
