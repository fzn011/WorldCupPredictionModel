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

# -----------------------------------------------------------------------------
# Step 14 full-tournament single-run constants
# -----------------------------------------------------------------------------

FULL_TOURNAMENT_SIMULATED_MATCHES_FILE: str = "full_tournament_simulated_matches.csv"
FULL_TOURNAMENT_GROUP_TABLES_FILE: str = "full_tournament_group_tables.csv"
FULL_TOURNAMENT_KNOCKOUT_MATCHES_FILE: str = "full_tournament_knockout_matches.csv"
FULL_TOURNAMENT_STAGE_RESULTS_FILE: str = "full_tournament_stage_results.csv"
FULL_TOURNAMENT_PATH_REPORT_FILE: str = "full_tournament_path_report.csv"
FULL_TOURNAMENT_RESULT_FILE: str = "single_world_cup_result.json"
FULL_TOURNAMENT_SUMMARY_FILE: str = "full_tournament_summary.json"
FULL_TOURNAMENT_VALIDATION_REPORT_FILE: str = "full_tournament_validation_report.csv"

FULL_TOURNAMENT_RUN_TYPE_SINGLE: str = "single_run"
FULL_TOURNAMENT_STAGE_GROUP: str = "group_stage"
FULL_TOURNAMENT_STAGE_KNOCKOUT: str = "knockout_stage"

# -----------------------------------------------------------------------------
# Step 15 Monte Carlo tournament simulation constants
# -----------------------------------------------------------------------------

MONTE_CARLO_SIMULATION_RESULTS_FILE: str = "monte_carlo_simulation_results.csv"
MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE: str = "monte_carlo_team_stage_probabilities.csv"
MONTE_CARLO_CHAMPION_PROBABILITIES_FILE: str = "monte_carlo_champion_probabilities.csv"
MONTE_CARLO_FINALISTS_FILE: str = "monte_carlo_finalists.csv"
MONTE_CARLO_SEMIFINALISTS_FILE: str = "monte_carlo_semifinalists.csv"
MONTE_CARLO_SUMMARY_FILE: str = "monte_carlo_summary.json"
MONTE_CARLO_VALIDATION_REPORT_FILE: str = "monte_carlo_validation_report.csv"

DEFAULT_MONTE_CARLO_SIMULATIONS: int = 100
DEFAULT_MONTE_CARLO_SEED: int = 42

MONTE_CARLO_STAGE_COLUMNS: list[str] = [
    "group_stage",
    "round_of_32",
    "round_of_16",
    "quarter_final",
    "semi_final",
    "final",
    "champion",
]

MONTE_CARLO_FINAL_POSITIONS: list[str] = [
    "champion",
    "runner_up",
    "third_place",
    "fourth_place",
]

# -----------------------------------------------------------------------------
# Step 16 Monte Carlo dashboard/report polish constants
# -----------------------------------------------------------------------------

MONTE_CARLO_REPORT_MD_FILE: str = "monte_carlo_report.md"
MONTE_CARLO_SUMMARY_CARDS_FILE: str = "monte_carlo_summary_cards.csv"
MONTE_CARLO_DASHBOARD_EXPORT_FILE: str = "monte_carlo_dashboard_export.csv"

MONTE_CARLO_CHAMPION_CHART_FILE: str = "monte_carlo_champion_probabilities.png"
MONTE_CARLO_STAGE_HEATMAP_FILE: str = "monte_carlo_stage_heatmap.png"

MONTE_CARLO_TOP_N_TEAMS: int = 20

STAGE_PROBABILITY_DISPLAY_COLUMNS: list[str] = [
    "team",
    "round_of_32_probability",
    "round_of_16_probability",
    "quarter_final_probability",
    "semi_final_probability",
    "final_probability",
    "champion_probability",
]

# -----------------------------------------------------------------------------
# Step 17/18 FIFA World Cup awards predictor constants
# -----------------------------------------------------------------------------

AWARDS_OUTPUT_DIR: str = "data/processed"
AWARDS_REPORT_DIR: str = "reports"

PLAYER_CANDIDATES_FILE: str = "player_candidates.csv"
SAMPLE_PLAYER_CANDIDATES_FILE: str = "sample_player_candidates.csv"
TEAM_AWARD_PROFILES_FILE: str = "team_award_profiles.csv"
SAMPLE_TEAM_AWARD_PROFILES_FILE: str = "sample_team_award_profiles.csv"

WORLD_CUP_AWARDS_PREDICTIONS_FILE: str = "world_cup_awards_predictions.csv"
GOLDEN_BALL_PREDICTIONS_FILE: str = "golden_ball_predictions.csv"
GOLDEN_BOOT_PREDICTIONS_FILE: str = "golden_boot_predictions.csv"
GOLDEN_GLOVE_PREDICTIONS_FILE: str = "golden_glove_predictions.csv"
YOUNG_PLAYER_PREDICTIONS_FILE: str = "young_player_predictions.csv"
FAIR_PLAY_PREDICTIONS_FILE: str = "fair_play_predictions.csv"
MOST_ENTERTAINING_TEAM_PREDICTIONS_FILE: str = "most_entertaining_team_predictions.csv"
TEAM_OF_THE_TOURNAMENT_FILE: str = "team_of_the_tournament.csv"
PLAYER_OF_THE_MATCH_PROXY_FILE: str = "player_of_the_match_proxy.csv"
GOAL_OF_THE_TOURNAMENT_PROXY_FILE: str = "goal_of_the_tournament_proxy.csv"

WORLD_CUP_AWARDS_SUMMARY_FILE: str = "world_cup_awards_summary.json"
WORLD_CUP_AWARDS_VALIDATION_REPORT_FILE: str = "world_cup_awards_validation_report.csv"
WORLD_CUP_AWARDS_REPORT_FILE: str = "world_cup_awards_report.md"

GOLDEN_BALL_CANDIDATES_FILE: str = "golden_ball_candidates.csv"
GOLDEN_BALL_SUMMARY_FILE: str = "golden_ball_summary.json"
GOLDEN_BALL_VALIDATION_REPORT_FILE: str = "golden_ball_validation_report.csv"
GOLDEN_BALL_REPORT_FILE: str = "golden_ball_report.md"

WORLD_CUP_AWARD_NAMES: list[str] = [
    "Golden Ball",
    "Silver Ball",
    "Bronze Ball",
    "Golden Boot",
    "Silver Boot",
    "Bronze Boot",
    "Golden Glove",
    "Young Player Award",
    "Fair Play Trophy",
    "Most Entertaining Team",
    "Predicted Team of the Tournament",
    "Player of the Match Proxy",
    "Goal of the Tournament Proxy",
]

PLAYER_POSITIONS: list[str] = [
    "forward",
    "midfielder",
    "defender",
    "goalkeeper",
]

POSITION_WEIGHTS: dict[str, dict[str, float]] = {
    "forward": {
        "goals": 5.0,
        "assists": 2.5,
        "chance_creation": 1.5,
        "defensive_actions": 0.2,
        "goalkeeper_actions": 0.0,
    },
    "midfielder": {
        "goals": 3.5,
        "assists": 3.0,
        "chance_creation": 2.5,
        "defensive_actions": 1.0,
        "goalkeeper_actions": 0.0,
    },
    "defender": {
        "goals": 2.5,
        "assists": 1.5,
        "chance_creation": 0.8,
        "defensive_actions": 2.5,
        "goalkeeper_actions": 0.0,
    },
    "goalkeeper": {
        "goals": 0.0,
        "assists": 0.0,
        "chance_creation": 0.0,
        "defensive_actions": 0.5,
        "goalkeeper_actions": 4.0,
    },
}

TEAM_PROGRESSION_WEIGHTS: dict[str, float] = {
    "round_of_32_probability": 0.5,
    "round_of_16_probability": 1.0,
    "quarter_final_probability": 1.5,
    "semi_final_probability": 2.5,
    "final_probability": 3.5,
    "champion_probability": 5.0,
}

AWARD_POSITION_GROUPS: dict[str, str] = {
    "GK": "goalkeeper",
    "DF": "defender",
    "MF": "midfielder",
    "FW": "forward",
}

AWARD_POSITION_WEIGHTS: dict[str, dict[str, float]] = {
    "goalkeeper": {
        "golden_ball": 0.85,
        "golden_boot": 0.02,
        "golden_glove": 1.50,
        "defensive": 1.20,
        "creative": 0.10,
        "attacking": 0.02,
    },
    "defender": {
        "golden_ball": 0.95,
        "golden_boot": 0.15,
        "golden_glove": 0.00,
        "defensive": 1.35,
        "creative": 0.50,
        "attacking": 0.25,
    },
    "midfielder": {
        "golden_ball": 1.10,
        "golden_boot": 0.65,
        "golden_glove": 0.00,
        "defensive": 0.75,
        "creative": 1.35,
        "attacking": 0.80,
    },
    "forward": {
        "golden_ball": 1.15,
        "golden_boot": 1.40,
        "golden_glove": 0.00,
        "defensive": 0.20,
        "creative": 0.80,
        "attacking": 1.50,
    },
}

AWARD_TEAM_PROGRESSION_WEIGHTS: dict[str, float] = {
    "round_of_32_probability": 0.5,
    "round_of_16_probability": 1.0,
    "quarter_final_probability": 1.5,
    "semi_final_probability": 2.5,
    "final_probability": 3.5,
    "champion_probability": 5.0,
}

AWARDS_ANALYTICS_DISCLAIMER: str = (
    "These are explainable analytics estimates based on official squads, editable player priors, "
    "team profiles, and Monte Carlo team progression probabilities. They are not official FIFA predictions."
)

YOUNG_PLAYER_CUTOFF_DATE_2026: str = "2005-01-01"

# -----------------------------------------------------------------------------
# Step 19: Player prior enrichment + portfolio packaging
# -----------------------------------------------------------------------------

PLAYER_PRIOR_ENRICHMENT_REPORT_FILE: str = "player_prior_enrichment_report.csv"
PLAYER_PRIOR_QUALITY_REPORT_FILE: str = "player_prior_quality_report.csv"
ENRICHED_PLAYER_AWARD_PRIORS_FILE: str = "enriched_player_award_priors.csv"
ENRICHED_OFFICIAL_AWARD_CANDIDATES_FILE: str = "enriched_official_award_candidates.csv"

FINAL_PROJECT_SUMMARY_FILE: str = "final_project_summary.json"
FINAL_PROJECT_VALIDATION_REPORT_FILE: str = "final_project_validation_report.csv"

PORTFOLIO_DIR: str = "portfolio"
PORTFOLIO_ASSETS_DIR: str = "portfolio/assets"
PORTFOLIO_SCREENSHOTS_DIR: str = "portfolio/screenshots"
PORTFOLIO_DEMO_SCRIPT_FILE: str = "portfolio/demo_script.md"
PORTFOLIO_README_FILE: str = "portfolio/PORTFOLIO_README.md"
PROJECT_ARCHITECTURE_FILE: str = "portfolio/project_architecture.md"
PROJECT_LIMITATIONS_FILE: str = "portfolio/limitations.md"
DEPLOYMENT_GUIDE_FILE: str = "portfolio/deployment_guide.md"
REPRODUCIBILITY_CHECKLIST_FILE: str = "portfolio/reproducibility_checklist.md"

DEFAULT_PRIOR_BY_POSITION: dict[str, dict[str, float]] = {
    "goalkeeper": {
        "base_player_rating": 58,
        "expected_minutes_share": 0.35,
        "goals_prior": 0,
        "assists_prior": 0,
        "chance_creation_prior": 0,
        "defensive_actions_prior": 3,
        "goalkeeper_actions_prior": 5,
        "discipline_risk": 0.25,
        "star_role_score": 1.0,
        "flair_score": 0.2,
    },
    "defender": {
        "base_player_rating": 58,
        "expected_minutes_share": 0.40,
        "goals_prior": 0.3,
        "assists_prior": 0.3,
        "chance_creation_prior": 0.4,
        "defensive_actions_prior": 5,
        "goalkeeper_actions_prior": 0,
        "discipline_risk": 0.35,
        "star_role_score": 1.0,
        "flair_score": 0.3,
    },
    "midfielder": {
        "base_player_rating": 60,
        "expected_minutes_share": 0.45,
        "goals_prior": 0.8,
        "assists_prior": 1.0,
        "chance_creation_prior": 3,
        "defensive_actions_prior": 2,
        "goalkeeper_actions_prior": 0,
        "discipline_risk": 0.30,
        "star_role_score": 1.5,
        "flair_score": 0.8,
    },
    "forward": {
        "base_player_rating": 60,
        "expected_minutes_share": 0.45,
        "goals_prior": 1.5,
        "assists_prior": 0.7,
        "chance_creation_prior": 2,
        "defensive_actions_prior": 0.5,
        "goalkeeper_actions_prior": 0,
        "discipline_risk": 0.25,
        "star_role_score": 1.5,
        "flair_score": 1.0,
    },
}

PLAYER_PRIOR_FLATNESS_WARNING_THRESHOLD: float = 0.80
PLAYER_PRIOR_MIN_NON_DEFAULT_SHARE: float = 0.20

PRIOR_NUMERIC_COLUMNS: list[str] = [
    "base_player_rating",
    "expected_minutes_share",
    "goals_prior",
    "assists_prior",
    "chance_creation_prior",
    "defensive_actions_prior",
    "goalkeeper_actions_prior",
    "discipline_risk",
    "star_role_score",
    "flair_score",
]

# -----------------------------------------------------------------------------
# Step 17A official World Cup 2026 data lock constants
# -----------------------------------------------------------------------------

OFFICIAL_DATA_DIR: str = "data/official"
OFFICIAL_RAW_DIR: str = "data/official/raw"
OFFICIAL_PROCESSED_DIR: str = "data/official/processed"
OFFICIAL_REPORTS_DIR: str = "data/official/reports"

OFFICIAL_TEAMS_FILE: str = "official_teams.csv"
OFFICIAL_GROUPS_FILE: str = "official_groups.csv"
OFFICIAL_FIXTURES_FILE: str = "official_fixtures.csv"
OFFICIAL_VENUES_FILE: str = "official_venues.csv"
OFFICIAL_MATCH_CALENDAR_FILE: str = "official_match_calendar.csv"
OFFICIAL_DATA_SUMMARY_FILE: str = "official_data_summary.json"
OFFICIAL_DATA_VALIDATION_REPORT_FILE: str = "official_data_validation_report.csv"
OFFICIAL_SOURCE_MANIFEST_FILE: str = "source_manifest.json"

DATA_MODE_SAMPLE: str = "sample"
DATA_MODE_OFFICIAL: str = "official"
DEFAULT_TOURNAMENT_DATA_MODE: str = "official"

OFFICIAL_PLACEHOLDER_VALUES: list[str] = [
    "",
    "Unknown",
    "Sample Venue",
    "Sample City",
    "Sample Country",
    "TBD",
    "To Be Determined",
    "sample_to_be_verified",
]

OFFICIAL_REQUIRED_TEAM_COUNT: int = 48
OFFICIAL_REQUIRED_GROUP_COUNT: int = 12
OFFICIAL_TEAMS_PER_GROUP: int = 4
OFFICIAL_TOTAL_MATCHES: int = 104
OFFICIAL_GROUP_STAGE_MATCHES: int = 72
OFFICIAL_KNOCKOUT_MATCHES: int = 32

OFFICIAL_TEAMS_REQUIRED_COLUMNS: list[str] = [
    "team_id",
    "team",
    "team_code",
    "confederation",
    "group",
    "group_slot",
    "is_host",
    "qualified",
    "source",
    "last_verified_at",
]

OFFICIAL_GROUPS_REQUIRED_COLUMNS: list[str] = [
    "group",
    "slot",
    "team",
    "team_code",
    "confederation",
    "is_host",
    "source",
    "last_verified_at",
]

OFFICIAL_FIXTURES_REQUIRED_COLUMNS: list[str] = [
    "match_id",
    "match_number",
    "stage",
    "group",
    "date",
    "kickoff_local",
    "kickoff_utc",
    "timezone",
    "venue",
    "stadium",
    "city",
    "country",
    "team_a",
    "team_b",
    "team_a_code",
    "team_b_code",
    "team_a_group_slot",
    "team_b_group_slot",
    "status",
    "source",
    "last_verified_at",
]

OFFICIAL_VENUES_REQUIRED_COLUMNS: list[str] = [
    "venue_id",
    "stadium",
    "venue",
    "city",
    "country",
    "timezone",
    "capacity",
    "latitude",
    "longitude",
    "source",
    "last_verified_at",
]

OFFICIAL_MATCH_CALENDAR_REQUIRED_COLUMNS: list[str] = [
    "match_id",
    "match_number",
    "stage",
    "group",
    "date",
    "kickoff_local",
    "kickoff_utc",
    "timezone",
    "venue",
    "city",
    "country",
    "team_a",
    "team_b",
    "status",
    "source",
    "last_verified_at",
]

# -----------------------------------------------------------------------------
# Step 17B official World Cup 2026 squads and player priors
# -----------------------------------------------------------------------------

OFFICIAL_PLAYERS_FILE: str = "official_players.csv"
OFFICIAL_SQUADS_FILE: str = "official_squads.csv"
OFFICIAL_TEAM_PLAYER_MAP_FILE: str = "official_team_player_map.csv"
OFFICIAL_SQUAD_SUMMARY_FILE: str = "official_squad_summary.json"
OFFICIAL_SQUAD_VALIDATION_REPORT_FILE: str = "official_squad_validation_report.csv"
OFFICIAL_PLAYER_PRIOR_MERGE_REPORT_FILE: str = "official_player_prior_merge_report.csv"

PLAYER_AWARD_PRIORS_FILE: str = "player_award_priors.csv"
OFFICIAL_AWARD_CANDIDATES_FILE: str = "official_award_candidates.csv"
SAMPLE_PLAYER_AWARD_PRIORS_FILE: str = "sample_player_award_priors.csv"

OFFICIAL_REQUIRED_PLAYERS_PER_TEAM: int = 26
OFFICIAL_REQUIRED_TOTAL_PLAYERS: int = 1248

OFFICIAL_POSITION_CODES: list[str] = ["GK", "DF", "MF", "FW"]

OFFICIAL_POSITION_MAP: dict[str, str] = {
    "GK": "goalkeeper",
    "DF": "defender",
    "MF": "midfielder",
    "FW": "forward",
}

PLAYER_PRIOR_REQUIRED_COLUMNS: list[str] = [
    "player",
    "team",
    "base_player_rating",
    "expected_minutes_share",
    "goals_prior",
    "assists_prior",
    "chance_creation_prior",
    "defensive_actions_prior",
    "goalkeeper_actions_prior",
    "discipline_risk",
    "star_role_score",
    "flair_score",
    "notes",
]

OFFICIAL_PLAYERS_REQUIRED_COLUMNS: list[str] = [
    "player_id",
    "team",
    "team_code",
    "shirt_number",
    "position_code",
    "position",
    "player_name",
    "first_names",
    "last_names",
    "name_on_shirt",
    "date_of_birth",
    "age_at_tournament_start",
    "club",
    "club_country",
    "height_cm",
    "source",
    "last_verified_at",
]

OFFICIAL_AWARD_CANDIDATES_REQUIRED_COLUMNS: list[str] = [
    "player_id",
    "team",
    "team_code",
    "shirt_number",
    "position_code",
    "position",
    "player_name",
    "date_of_birth",
    "age_at_tournament_start",
    "club",
    "height_cm",
    "base_player_rating",
    "expected_minutes_share",
    "goals_prior",
    "assists_prior",
    "chance_creation_prior",
    "defensive_actions_prior",
    "goalkeeper_actions_prior",
    "discipline_risk",
    "star_role_score",
    "flair_score",
    "has_player_prior",
    "prior_source",
    "source",
    "last_verified_at",
]

# -----------------------------------------------------------------------------
# Step 17C official data completion + manual FIFA verification constants
# -----------------------------------------------------------------------------

# Final readiness status levels
OFFICIAL_READINESS_BLOCKED: str = "blocked"
OFFICIAL_READINESS_WARNING: str = "warning"
OFFICIAL_READINESS_READY: str = "ready"

# Import template file names
OFFICIAL_IMPORT_TEAMS_TEMPLATE_FILE: str = "import_teams_template.csv"
OFFICIAL_IMPORT_GROUPS_TEMPLATE_FILE: str = "import_groups_template.csv"
OFFICIAL_IMPORT_FIXTURES_TEMPLATE_FILE: str = "import_fixtures_template.csv"
OFFICIAL_IMPORT_VENUES_TEMPLATE_FILE: str = "import_venues_template.csv"
OFFICIAL_IMPORT_PLAYERS_TEMPLATE_FILE: str = "import_players_template.csv"
OFFICIAL_IMPORT_SQUADS_TEMPLATE_FILE: str = "import_squads_template.csv"

# Import results report
OFFICIAL_IMPORT_RESULTS_FILE: str = "official_import_results.json"

# Final readiness report
OFFICIAL_FINAL_READINESS_REPORT_FILE: str = "official_final_readiness_report.json"
OFFICIAL_FINAL_READINESS_CHECKLIST_FILE: str = "official_final_readiness_checklist.csv"

# Columns required for manual import files
IMPORT_TEAMS_REQUIRED_COLUMNS: list[str] = [
    "team",
    "team_code",
    "confederation",
    "group",
    "group_slot",
    "is_host",
    "qualified",
    "source",
]

IMPORT_GROUPS_REQUIRED_COLUMNS: list[str] = [
    "group",
    "slot",
    "team",
    "team_code",
    "confederation",
    "is_host",
    "source",
]

IMPORT_FIXTURES_REQUIRED_COLUMNS: list[str] = [
    "match_id",
    "match_number",
    "stage",
    "group",
    "date",
    "kickoff_local",
    "kickoff_utc",
    "timezone",
    "venue",
    "stadium",
    "city",
    "country",
    "team_a",
    "team_b",
    "team_a_code",
    "team_b_code",
    "team_a_group_slot",
    "team_b_group_slot",
    "status",
    "source",
]

IMPORT_VENUES_REQUIRED_COLUMNS: list[str] = [
    "venue_id",
    "stadium",
    "venue",
    "city",
    "country",
    "timezone",
    "capacity",
    "latitude",
    "longitude",
    "source",
]

IMPORT_PLAYERS_REQUIRED_COLUMNS: list[str] = [
    "player_id",
    "team",
    "team_code",
    "shirt_number",
    "position_code",
    "position",
    "player_name",
    "first_names",
    "last_names",
    "name_on_shirt",
    "date_of_birth",
    "age_at_tournament_start",
    "club",
    "club_country",
    "height_cm",
    "source",
]

IMPORT_SQUADS_REQUIRED_COLUMNS: list[str] = [
    "team",
    "team_code",
    "player_count",
    "goalkeepers",
    "defenders",
    "midfielders",
    "forwards",
    "avg_age",
    "avg_height_cm",
    "source",
]

# Final readiness checklist items
FINAL_READINESS_CHECKLIST: list[dict[str, str]] = [
    {"id": "teams_complete", "name": "All 48 teams verified", "category": "teams"},
    {"id": "teams_no_placeholders", "name": "No placeholder values in teams", "category": "teams"},
    {"id": "groups_complete", "name": "All 12 groups with 4 teams each", "category": "groups"},
    {"id": "groups_no_placeholders", "name": "No placeholder values in groups", "category": "groups"},
    {"id": "venues_complete", "name": "All venues verified", "category": "venues"},
    {"id": "venues_no_placeholders", "name": "No placeholder values in venues", "category": "venues"},
    {"id": "fixtures_complete", "name": "All 104 fixtures scheduled", "category": "fixtures"},
    {"id": "fixtures_no_placeholders", "name": "No placeholder values in fixtures", "category": "fixtures"},
    {"id": "squads_complete", "name": "All 48 teams with 26 players", "category": "squads"},
    {"id": "players_complete", "name": "All 1248 players registered", "category": "squads"},
    {"id": "players_no_placeholders", "name": "No placeholder values in players", "category": "squads"},
    {"id": "award_candidates_ready", "name": "Award candidates generated", "category": "awards"},
    {"id": "player_priors_merged", "name": "Player priors merged", "category": "awards"},
    {"id": "no_sample_rows", "name": "No sample_to_be_verified rows", "category": "data_quality"},
    {"id": "data_consistency", "name": "Cross-dataset consistency verified", "category": "data_quality"},
]

# Blocking conditions for official_final mode
OFFICIAL_FINAL_BLOCKERS: list[str] = [
    "incomplete_teams",
    "incomplete_groups",
    "incomplete_venues",
    "incomplete_fixtures",
    "incomplete_squads",
    "incomplete_players",
    "placeholder_values_detected",
    "sample_rows_detected",
    "data_inconsistency",
    "validation_failed",
]

# -----------------------------------------------------------------------------
# Step 17D official data population pack constants
# -----------------------------------------------------------------------------

OFFICIAL_POPULATION_DIR: str = "data/official/population"
OFFICIAL_POPULATION_REPORTS_DIR: str = "data/official/population/reports"
OFFICIAL_POPULATION_WORKBOOK_DIR: str = "data/official/population/workbooks"
OFFICIAL_IMPORT_TEMPLATES_DIR: str = "data/official/import_templates"

OFFICIAL_POPULATION_GUIDE_FILE: str = "official_data_population_guide.md"
OFFICIAL_POPULATION_STATUS_FILE: str = "official_population_status.json"
OFFICIAL_POPULATION_MISSING_DATA_REPORT_FILE: str = "official_population_missing_data_report.csv"
OFFICIAL_POPULATION_DIFF_REPORT_FILE: str = "official_population_diff_report.csv"
OFFICIAL_POPULATION_IMPORT_AUDIT_FILE: str = "official_population_import_audit.csv"
OFFICIAL_POPULATION_PROMOTION_REPORT_FILE: str = "official_population_promotion_report.csv"

OFFICIAL_MASTER_IMPORT_WORKBOOK_FILE: str = "official_worldcup_2026_master_import.xlsx"
OFFICIAL_MASTER_IMPORT_README_FILE: str = "official_worldcup_2026_master_import_README.md"

OFFICIAL_FINAL_MODE_FLAG_FILE: str = "official_final_mode.json"

OFFICIAL_POPULATION_TEMPLATE_FILES: dict[str, str] = {
    "teams": "official_teams_import_template.csv",
    "groups": "official_groups_import_template.csv",
    "fixtures": "official_fixtures_import_template.csv",
    "venues": "official_venues_import_template.csv",
    "players": "official_players_import_template.csv",
    "player_priors": "player_award_priors_import_template.csv",
}

OFFICIAL_POPULATION_REQUIRED_STEPS: list[str] = [
    "fill_teams",
    "fill_groups",
    "fill_fixtures",
    "fill_venues",
    "fill_players",
    "fill_player_priors",
    "apply_imports",
    "run_squad_merge",
    "run_final_readiness",
    "promote_to_official_final",
]

OFFICIAL_POPULATION_ALLOWED_STATUSES: list[str] = [
    "not_started",
    "in_progress",
    "needs_review",
    "ready_for_import",
    "imported",
    "final_ready",
    "blocked",
]

OFFICIAL_VERIFICATION_FIELDS: list[str] = [
    "source",
    "last_verified_at",
    "verified_by",
    "verification_notes",
]

IMPORT_PLAYER_PRIORS_REQUIRED_COLUMNS: list[str] = [
    "player",
    "team",
    "base_player_rating",
    "expected_minutes_share",
    "goals_prior",
    "assists_prior",
    "chance_creation_prior",
    "defensive_actions_prior",
    "goalkeeper_actions_prior",
    "discipline_risk",
    "star_role_score",
    "flair_score",
    "notes",
    "source",
]

# -----------------------------------------------------------------------------
# Step 17E source-assisted official FIFA data population constants
# -----------------------------------------------------------------------------

OFFICIAL_SOURCE_DATA_DIR: str = "data/official/source_data"
OFFICIAL_SOURCE_RAW_DIR: str = "data/official/source_data/raw"
OFFICIAL_SOURCE_STAGING_DIR: str = "data/official/source_data/staging"
OFFICIAL_SOURCE_REPORTS_DIR: str = "data/official/source_data/reports"
OFFICIAL_SOURCE_EXPORTS_DIR: str = "data/official/source_data/exports"

OFFICIAL_SOURCE_REGISTRY_FILE: str = "official_source_registry.json"
OFFICIAL_SOURCE_SNAPSHOT_MANIFEST_FILE: str = "official_source_snapshot_manifest.json"

STAGED_OFFICIAL_TEAMS_FILE: str = "staged_official_teams.csv"
STAGED_OFFICIAL_GROUPS_FILE: str = "staged_official_groups.csv"
STAGED_OFFICIAL_FIXTURES_FILE: str = "staged_official_fixtures.csv"
STAGED_OFFICIAL_VENUES_FILE: str = "staged_official_venues.csv"
STAGED_OFFICIAL_PLAYERS_FILE: str = "staged_official_players.csv"
STAGED_PLAYER_AWARD_PRIORS_FILE: str = "staged_player_award_priors.csv"

OFFICIAL_SOURCE_COVERAGE_REPORT_FILE: str = "official_source_coverage_report.csv"
OFFICIAL_SOURCE_PARSE_REPORT_FILE: str = "official_source_parse_report.csv"
OFFICIAL_STAGING_VALIDATION_REPORT_FILE: str = "official_staging_validation_report.csv"
OFFICIAL_SOURCE_POPULATION_SUMMARY_FILE: str = "official_source_population_summary.json"
OFFICIAL_DOWNLOADABLE_IMPORT_PACK_FILE: str = "official_worldcup_2026_import_pack.zip"

OFFICIAL_FIFA_SOURCE_URLS: dict[str, str] = {
    "teams": "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/teams",
    "schedule": (
        "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/"
        "articles/match-schedule-fixtures-results-teams-stadiums"
    ),
    "scores_fixtures": (
        "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/scores-fixtures"
    ),
    "squad_announcements": (
        "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/"
        "articles/all-world-cup-squad-announcements"
    ),
}

OFFICIAL_SOURCE_ALLOWED_DOMAINS: list[str] = [
    "fifa.com",
    "fdp.fifa.org",
]

OFFICIAL_STAGING_STATUS_VALUES: list[str] = [
    "not_started",
    "source_downloaded",
    "parsed",
    "partial",
    "needs_manual_review",
    "ready_for_import",
    "failed",
]

OFFICIAL_SOURCE_APPLY_ORDER: list[str] = [
    "teams",
    "groups",
    "venues",
    "fixtures",
    "players",
    "player_priors",
]

# -----------------------------------------------------------------------------
# Step 17F populate official FIFA World Cup data constants
# -----------------------------------------------------------------------------

OFFICIAL_POPULATED_DATA_DIR: str = "data/official/populated"
OFFICIAL_POPULATED_REPORTS_DIR: str = "data/official/populated/reports"
OFFICIAL_POPULATED_EXPORTS_DIR: str = "data/official/populated/exports"

POPULATED_OFFICIAL_TEAMS_FILE: str = "populated_official_teams.csv"
POPULATED_OFFICIAL_GROUPS_FILE: str = "populated_official_groups.csv"
POPULATED_OFFICIAL_FIXTURES_FILE: str = "populated_official_fixtures.csv"
POPULATED_OFFICIAL_VENUES_FILE: str = "populated_official_venues.csv"
POPULATED_OFFICIAL_PLAYERS_FILE: str = "populated_official_players.csv"
POPULATED_PLAYER_AWARD_PRIORS_FILE: str = "populated_player_award_priors.csv"

OFFICIAL_POPULATION_SOURCE_AUDIT_FILE: str = "official_population_source_audit.csv"
OFFICIAL_POPULATION_COMPLETENESS_REPORT_FILE: str = "official_population_completeness_report.csv"
OFFICIAL_POPULATION_APPLY_REPORT_FILE: str = "official_population_apply_report.csv"
OFFICIAL_POPULATION_FINAL_SUMMARY_FILE: str = "official_population_final_summary.json"
OFFICIAL_APPLY_BLOCKER_CLEANUP_REPORT_FILE: str = "official_apply_blocker_cleanup_report.csv"

OFFICIAL_READY_IMPORT_PACK_FILE: str = "official_ready_import_pack.zip"

OFFICIAL_SOURCE_PRIORITY: list[str] = [
    "fifa_teams_page",
    "fifa_schedule_page",
    "fifa_scores_fixtures_page",
    "fifa_squad_announcements_page",
    "fifa_squad_confirmation_page",
    "fifa_downloadable_schedule",
]

POPULATION_TARGET_COUNTS: dict[str, int] = {
    "teams": 48,
    "groups": 12,
    "group_rows": 48,
    "fixtures": 104,
    "group_stage_fixtures": 72,
    "knockout_fixtures": 32,
    "players": 1248,
    "players_per_team": 26,
}

FIFA_TEAM_NAME_ALIASES: dict[str, str] = {
    "Korea Republic": "South Korea",
    "USA": "United States",
    "USMNT": "United States",
    "Türkiye": "Turkey",
    "Turkiye": "Turkey",
    "Curaçao": "Curaçao",
    "Curacao": "Curaçao",
}

# -----------------------------------------------------------------------------
# Step 17G official data import execution constants
# -----------------------------------------------------------------------------

OFFICIAL_IMPORT_EXECUTION_SUMMARY_FILE: str = "official_import_execution_summary.json"
