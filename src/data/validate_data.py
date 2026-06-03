"""Match-data validation."""

from __future__ import annotations

import pandas as pd

from src.utils.constants import (
    BASIC_REQUIRED_MATCH_COLUMNS,
    CANONICAL_MATCH_COLUMNS,
    ELO_RATINGS_REQUIRED_COLUMNS,
    FIFA_RANKINGS_REQUIRED_COLUMNS,
    HISTORICAL_RESULTS_REQUIRED_COLUMNS,
    RESULT_LABELS,
    TEAM_REGISTRY_COLUMNS,
    WC2026_GROUPS_REQUIRED_COLUMNS,
    WC2026_SCHEDULE_REQUIRED_COLUMNS,
    WC2026_TEAMS_REQUIRED_COLUMNS,
)


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: list[str],
    dataset_name: str,
) -> bool:
    """Generic column-presence validator.

    Raises ``ValueError`` listing any missing columns; otherwise returns True.
    """
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(
            f"Dataset '{dataset_name}' is missing required columns: {missing}"
        )
    return True


def validate_match_data(df: pd.DataFrame) -> bool:
    """Validate a canonical match-results DataFrame (team_a / team_b form)."""
    return validate_required_columns(
        df, BASIC_REQUIRED_MATCH_COLUMNS, "canonical_matches"
    )


def _ensure_non_null_team_columns(
    df: pd.DataFrame, columns: list[str], dataset_name: str
) -> None:
    for col in columns:
        if col in df.columns and df[col].isna().all():
            raise ValueError(
                f"Dataset '{dataset_name}': column '{col}' is entirely null."
            )


def validate_historical_results(df: pd.DataFrame) -> bool:
    """Validate the raw historical-results dataset."""
    validate_required_columns(
        df, HISTORICAL_RESULTS_REQUIRED_COLUMNS, "historical_results"
    )
    for col in ("home_score", "away_score"):
        if pd.to_numeric(df[col], errors="coerce").isna().all():
            raise ValueError(
                f"historical_results: column '{col}' is not numeric."
            )
    if pd.to_datetime(df["date"], errors="coerce").isna().all():
        raise ValueError("historical_results: column 'date' is not parseable.")
    _ensure_non_null_team_columns(
        df, ["home_team", "away_team"], "historical_results"
    )
    return True


def validate_fifa_rankings(df: pd.DataFrame) -> bool:
    """Validate the FIFA-rankings dataset."""
    validate_required_columns(
        df, FIFA_RANKINGS_REQUIRED_COLUMNS, "fifa_rankings"
    )
    if pd.to_numeric(df["points"], errors="coerce").isna().all():
        raise ValueError("fifa_rankings: column 'points' is not numeric.")
    if pd.to_datetime(df["ranking_date"], errors="coerce").isna().all():
        raise ValueError("fifa_rankings: column 'ranking_date' is not parseable.")
    _ensure_non_null_team_columns(df, ["team"], "fifa_rankings")
    return True


def validate_elo_ratings(df: pd.DataFrame) -> bool:
    """Validate the Elo-ratings dataset."""
    validate_required_columns(df, ELO_RATINGS_REQUIRED_COLUMNS, "elo_ratings")
    if pd.to_numeric(df["elo"], errors="coerce").isna().all():
        raise ValueError("elo_ratings: column 'elo' is not numeric.")
    if pd.to_datetime(df["rating_date"], errors="coerce").isna().all():
        raise ValueError("elo_ratings: column 'rating_date' is not parseable.")
    _ensure_non_null_team_columns(df, ["team"], "elo_ratings")
    return True


def validate_wc2026_teams(df: pd.DataFrame) -> bool:
    """Validate the WC2026 teams dataset."""
    validate_required_columns(df, WC2026_TEAMS_REQUIRED_COLUMNS, "wc2026_teams")
    _ensure_non_null_team_columns(df, ["team"], "wc2026_teams")
    return True


def validate_wc2026_groups(df: pd.DataFrame) -> bool:
    """Validate the WC2026 groups dataset."""
    validate_required_columns(df, WC2026_GROUPS_REQUIRED_COLUMNS, "wc2026_groups")
    _ensure_non_null_team_columns(df, ["team"], "wc2026_groups")
    return True


def validate_wc2026_schedule(df: pd.DataFrame) -> bool:
    """Validate the WC2026 schedule dataset."""
    validate_required_columns(
        df, WC2026_SCHEDULE_REQUIRED_COLUMNS, "wc2026_schedule"
    )
    if pd.to_datetime(df["date"], errors="coerce").isna().all():
        raise ValueError("wc2026_schedule: column 'date' is not parseable.")
    _ensure_non_null_team_columns(df, ["team_a", "team_b"], "wc2026_schedule")
    return True


def validate_canonical_matches(df: pd.DataFrame) -> bool:
    """Validate the Step 3 canonical-matches dataset.

    Checks required columns, valid result labels, that team_a != team_b,
    and that the result encoding is within {0, 1, 2}.
    """
    validate_required_columns(
        df, CANONICAL_MATCH_COLUMNS, "canonical_matches"
    )
    if df.empty:
        return True

    invalid_results = set(df["result"].dropna().unique()) - {0, 1, 2}
    if invalid_results:
        raise ValueError(
            f"canonical_matches: invalid result codes {sorted(invalid_results)}."
        )

    valid_labels = set(RESULT_LABELS.values())
    invalid_labels = set(df["result_label"].dropna().unique()) - valid_labels
    if invalid_labels:
        raise ValueError(
            f"canonical_matches: invalid result labels {sorted(invalid_labels)}."
        )

    same_team = df[df["team_a"] == df["team_b"]]
    if not same_team.empty:
        raise ValueError(
            f"canonical_matches: {len(same_team)} rows where team_a == team_b."
        )
    return True


def validate_team_registry(df: pd.DataFrame) -> bool:
    """Validate the Step 3 team-registry dataset.

    Checks required columns, unique team names and slugs, and that every
    team has at least one recorded match.
    """
    validate_required_columns(df, TEAM_REGISTRY_COLUMNS, "team_registry")
    if df.empty:
        return True

    if df["team"].duplicated().any():
        raise ValueError("team_registry: duplicate team names found.")
    if df["team_slug"].duplicated().any():
        raise ValueError("team_registry: duplicate team slugs found.")
    if (pd.to_numeric(df["matches_played"], errors="coerce") < 1).any():
        raise ValueError("team_registry: some teams have matches_played < 1.")
    return True
