"""Feature engineering for match-level prediction."""

from __future__ import annotations

import pandas as pd

from src.features.historical_features import build_historical_feature_dataset
from src.utils.constants import (
    BASIC_FEATURE_COLUMNS,
    FEATURE_QUALITY_REPORT_FILE,
    FRIENDLY_KEYWORDS,
    MAJOR_TOURNAMENT_KEYWORDS,
    RECENT_FORM_WINDOWS,
    RESULT_LABELS,
    WORLD_CUP_2026_HOSTS,
    WORLD_CUP_QUALIFIER_KEYWORDS,
    WORLD_CUP_TOURNAMENT_KEYWORDS,
    CONTINENTAL_TOURNAMENT_KEYWORDS,
)
from src.utils.team_name_mapping import standardize_team_name


def build_basic_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build a minimal set of placeholder match features.

    Adds:
        * ``goal_difference`` — team_a_score - team_b_score
        * ``total_goals``     — team_a_score + team_b_score
        * ``is_draw``         — 1 if scores are equal, else 0
    """
    if "team_a_score" not in df.columns or "team_b_score" not in df.columns:
        raise ValueError(
            "DataFrame must contain 'team_a_score' and 'team_b_score' columns."
        )

    out = df.copy()
    out["goal_difference"] = out["team_a_score"] - out["team_b_score"]
    out["total_goals"] = out["team_a_score"] + out["team_b_score"]
    out["is_draw"] = (out["team_a_score"] == out["team_b_score"]).astype(int)

    # TODO (later step): add FIFA ranking, Elo, and player-level features.
    return out


def _contains_keyword(text: str, keywords: list[str]) -> bool:
    if not text:
        return False
    return any(keyword.lower() in text.lower() for keyword in keywords)


def add_match_context_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add tournament-context flags to a match DataFrame."""
    out = df.copy()
    tournament = out["tournament"] if "tournament" in out.columns else pd.Series("")
    tournament = pd.Series(tournament, index=out.index).fillna("")

    neutral = out["neutral"] if "neutral" in out.columns else pd.Series(0, index=out.index)
    neutral = pd.Series(neutral, index=out.index)
    out["is_neutral"] = pd.to_numeric(neutral, errors="coerce").fillna(0).astype(int)
    out["is_world_cup"] = tournament.map(lambda value: int(_contains_keyword(str(value), WORLD_CUP_TOURNAMENT_KEYWORDS)))
    out["is_world_cup_qualifier"] = tournament.map(lambda value: int(_contains_keyword(str(value), WORLD_CUP_QUALIFIER_KEYWORDS)))
    out["is_friendly"] = tournament.map(lambda value: int(_contains_keyword(str(value), FRIENDLY_KEYWORDS)))
    out["is_continental_tournament"] = tournament.map(lambda value: int(_contains_keyword(str(value), CONTINENTAL_TOURNAMENT_KEYWORDS)))
    out["is_major_tournament"] = tournament.map(lambda value: int(_contains_keyword(str(value), MAJOR_TOURNAMENT_KEYWORDS)))

    # Conservative placeholder: keep this simple until we have explicit stage data.
    date = pd.to_datetime(out["date"], errors="coerce") if "date" in out.columns else pd.Series(pd.NaT, index=out.index)
    out["is_knockout_like_match"] = (
        (out["is_world_cup"] == 1)
        & date.notna()
        & (date.dt.year >= 1982)
        & (date.dt.month.isin([6, 7, 11, 12]))
    ).astype(int)
    return out


def add_host_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Flag whether team A or team B is one of the 2026 hosts."""
    out = df.copy()
    hosts = {standardize_team_name(team) for team in WORLD_CUP_2026_HOSTS}
    out["team_a_is_host_2026"] = out["team_a"].map(lambda value: int(standardize_team_name(value) in hosts))
    out["team_b_is_host_2026"] = out["team_b"].map(lambda value: int(standardize_team_name(value) in hosts))
    return out


def add_basic_target_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure the target columns are present for downstream modeling."""
    out = df.copy()
    if "result" not in out.columns and {"team_a_score", "team_b_score"}.issubset(out.columns):
        out["result"] = 1
        out.loc[out["team_a_score"] > out["team_b_score"], "result"] = 2
        out.loc[out["team_a_score"] < out["team_b_score"], "result"] = 0
    if "result_label" not in out.columns and "result" in out.columns:
        out["result_label"] = out["result"].map(RESULT_LABELS)
    return out


def _reorder_feature_columns(df: pd.DataFrame) -> pd.DataFrame:
    preferred = [col for col in BASIC_FEATURE_COLUMNS if col in df.columns]
    remaining = [col for col in df.columns if col not in preferred]
    return df[preferred + remaining]


def build_feature_dataset(
    canonical_df: pd.DataFrame,
    min_year: int | None = 1990,
) -> pd.DataFrame:
    """Build the Step 4 machine-learning feature dataset."""
    feature_df = build_historical_feature_dataset(
        canonical_df,
        windows=RECENT_FORM_WINDOWS,
        min_year=min_year,
    )
    if feature_df.empty:
        return feature_df

    feature_df = add_match_context_features(feature_df)
    feature_df = add_host_flags(feature_df)
    feature_df = add_basic_target_columns(feature_df)
    return _reorder_feature_columns(feature_df)


def create_feature_quality_report(feature_df: pd.DataFrame) -> pd.DataFrame:
    """Create a compact quality report for the engineered feature dataset."""
    if feature_df is None:
        feature_df = pd.DataFrame()

    team_count = 0
    if not feature_df.empty and {"team_a", "team_b"}.issubset(feature_df.columns):
        team_count = len(pd.unique(feature_df[["team_a", "team_b"]].values.ravel("K")))

    def _count(flag_column: str) -> int:
        if flag_column in feature_df.columns:
            return int(pd.to_numeric(feature_df[flag_column], errors="coerce").fillna(0).sum())
        return 0

    def _missing_history_count(column_name: str) -> int:
        if column_name not in feature_df.columns:
            return 0
        return int((pd.to_numeric(feature_df[column_name], errors="coerce").fillna(0) == 0).sum())

    def _object_column_count() -> int:
        count = 0
        for column in feature_df.columns:
            dtype_str = str(feature_df[column].dtype)
            if dtype_str == "object" or dtype_str.startswith("string"):
                count += 1
        return count

    rows = [
        ("feature_rows", len(feature_df)),
        ("feature_columns", len(feature_df.columns)),
        ("date_min", str(pd.to_datetime(feature_df["date"], errors="coerce").min()) if "date" in feature_df.columns and not feature_df.empty else ""),
        ("date_max", str(pd.to_datetime(feature_df["date"], errors="coerce").max()) if "date" in feature_df.columns and not feature_df.empty else ""),
        ("unique_teams", team_count),
        ("target_team_a_win_count", int((feature_df["result"] == 2).sum()) if "result" in feature_df.columns else 0),
        ("target_draw_count", int((feature_df["result"] == 1).sum()) if "result" in feature_df.columns else 0),
        ("target_team_a_loss_count", int((feature_df["result"] == 0).sum()) if "result" in feature_df.columns else 0),
        ("missing_values_total", int(feature_df.isna().sum().sum())),
        ("numeric_feature_count", int(feature_df.select_dtypes(include="number").shape[1])),
        ("object_column_count", _object_column_count()),
        ("matches_with_no_prior_team_a_history", _missing_history_count("team_a_matches_played_before")),
        ("matches_with_no_prior_team_b_history", _missing_history_count("team_b_matches_played_before")),
        ("world_cup_matches", _count("is_world_cup")),
        ("friendly_matches", _count("is_friendly")),
        ("major_tournament_matches", _count("is_major_tournament")),
    ]
    return pd.DataFrame(rows, columns=["metric", "value"])


def create_feature_summary(feature_df: pd.DataFrame) -> dict:
    """Return a JSON-serialisable summary for the feature dataset."""
    if feature_df is None:
        feature_df = pd.DataFrame()

    date_series = pd.to_datetime(feature_df["date"], errors="coerce") if "date" in feature_df.columns else pd.Series(dtype="datetime64[ns]")
    target_distribution = {}
    if "result_label" in feature_df.columns:
        target_distribution = feature_df["result_label"].value_counts(dropna=False).to_dict()

    summary = {
        "status": "ok" if not feature_df.empty else "empty",
        "rows": int(len(feature_df)),
        "columns": int(len(feature_df.columns)),
        "date_min": str(date_series.min()) if not date_series.empty else None,
        "date_max": str(date_series.max()) if not date_series.empty else None,
        "unique_teams": int(len(pd.unique(feature_df[["team_a", "team_b"]].values.ravel("K")))) if not feature_df.empty and {"team_a", "team_b"}.issubset(feature_df.columns) else 0,
        "numeric_feature_count": int(feature_df.select_dtypes(include="number").shape[1]),
        "target_distribution": target_distribution,
        "missing_values_total": int(feature_df.isna().sum().sum()),
        "notes": [
            "Historical features are leakage-safe: only matches before each game date are used.",
            "Recent form windows currently use 5 and 10 matches.",
            f"Quality report schema: {FEATURE_QUALITY_REPORT_FILE}",
        ],
    }
    return summary
