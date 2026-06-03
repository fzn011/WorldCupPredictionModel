"""Registry of all data sources used by the project.

Each entry in :data:`DATA_SOURCES` describes:

* ``expected_path`` — where the real (user-supplied) CSV should live.
* ``sample_path``   — the small fallback CSV bundled with the repo.
* ``required_columns`` — minimum columns the loader expects.

This registry is the single source of truth used by
``src.data.load_data.load_dataset_with_fallback`` and by the
``scripts/check_datasets.py`` availability report.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.utils.constants import (
    ELO_RATINGS_FILE,
    ELO_RATINGS_REQUIRED_COLUMNS,
    FIFA_RANKINGS_FILE,
    FIFA_RANKINGS_REQUIRED_COLUMNS,
    HISTORICAL_RESULTS_FILE,
    HISTORICAL_RESULTS_REQUIRED_COLUMNS,
    RAW_MATCHES_DIR,
    RAW_RANKINGS_DIR,
    RAW_WORLD_CUP_2026_DIR,
    SAMPLE_DATA_DIR,
    WC2026_GROUPS_FILE,
    WC2026_GROUPS_REQUIRED_COLUMNS,
    WC2026_SCHEDULE_FILE,
    WC2026_SCHEDULE_REQUIRED_COLUMNS,
    WC2026_TEAMS_FILE,
    WC2026_TEAMS_REQUIRED_COLUMNS,
)


@dataclass(frozen=True)
class DataSourceConfig:
    """Description of a single dataset used by the project."""

    name: str
    expected_path: Path
    sample_path: Path
    required_columns: list[str]
    description: str


DATA_SOURCES: dict[str, DataSourceConfig] = {
    "historical_results": DataSourceConfig(
        name="Historical results",
        expected_path=RAW_MATCHES_DIR / HISTORICAL_RESULTS_FILE,
        sample_path=SAMPLE_DATA_DIR / "sample_results.csv",
        required_columns=HISTORICAL_RESULTS_REQUIRED_COLUMNS,
        description=(
            "Historical international football match results. Recommended "
            "source: Kaggle 'International football results from 1872 to 2026'."
        ),
    ),
    "fifa_rankings": DataSourceConfig(
        name="FIFA rankings",
        expected_path=RAW_RANKINGS_DIR / FIFA_RANKINGS_FILE,
        sample_path=SAMPLE_DATA_DIR / "sample_fifa_rankings.csv",
        required_columns=FIFA_RANKINGS_REQUIRED_COLUMNS,
        description="Official FIFA men's world ranking snapshot.",
    ),
    "elo_ratings": DataSourceConfig(
        name="Elo ratings",
        expected_path=RAW_RANKINGS_DIR / ELO_RATINGS_FILE,
        sample_path=SAMPLE_DATA_DIR / "sample_elo_ratings.csv",
        required_columns=ELO_RATINGS_REQUIRED_COLUMNS,
        description="World Football Elo ratings snapshot.",
    ),
    "wc2026_teams": DataSourceConfig(
        name="WC2026 teams",
        expected_path=RAW_WORLD_CUP_2026_DIR / WC2026_TEAMS_FILE,
        sample_path=SAMPLE_DATA_DIR / "sample_world_cup_2026_teams.csv",
        required_columns=WC2026_TEAMS_REQUIRED_COLUMNS,
        description="Qualified teams for the FIFA World Cup 2026.",
    ),
    "wc2026_groups": DataSourceConfig(
        name="WC2026 groups",
        expected_path=RAW_WORLD_CUP_2026_DIR / WC2026_GROUPS_FILE,
        sample_path=SAMPLE_DATA_DIR / "sample_world_cup_2026_groups.csv",
        required_columns=WC2026_GROUPS_REQUIRED_COLUMNS,
        description="Group-stage draw (12 groups of 4).",
    ),
    "wc2026_schedule": DataSourceConfig(
        name="WC2026 schedule",
        expected_path=RAW_WORLD_CUP_2026_DIR / WC2026_SCHEDULE_FILE,
        sample_path=SAMPLE_DATA_DIR / "sample_world_cup_2026_schedule.csv",
        required_columns=WC2026_SCHEDULE_REQUIRED_COLUMNS,
        description="Full match schedule for the FIFA World Cup 2026.",
    ),
}
