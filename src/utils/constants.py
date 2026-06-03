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
