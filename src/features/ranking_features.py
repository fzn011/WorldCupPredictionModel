"""FIFA ranking + Elo feature engineering for Step 7."""

from __future__ import annotations

import numpy as np
import pandas as pd

import src.utils.constants as C
from src.utils.team_name_mapping import standardize_team_name

FIFA_RANKING_FEATURE_COLUMNS = getattr(C, "FIFA_RANKING_FEATURE_COLUMNS", [])
ELO_FEATURE_COLUMNS = getattr(C, "ELO_FEATURE_COLUMNS", [])
TEAM_STRENGTH_FEATURE_COLUMNS = getattr(C, "TEAM_STRENGTH_FEATURE_COLUMNS", [])


def _to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _min_max_normalize(series: pd.Series) -> pd.Series:
    values = _to_numeric(series)
    valid = values.dropna()
    if valid.empty:
        return pd.Series(np.zeros(len(values), dtype=float), index=values.index)
    min_v = float(valid.min())
    max_v = float(valid.max())
    if np.isclose(min_v, max_v):
        out = pd.Series(np.zeros(len(values), dtype=float), index=values.index)
        out.loc[valid.index] = 1.0
        return out
    return (values - min_v) / (max_v - min_v)


def clean_fifa_rankings(df: pd.DataFrame) -> pd.DataFrame:
    """Clean FIFA rankings and keep one latest row per team."""
    required = {"rank", "team", "points", "ranking_date"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"FIFA rankings missing required columns: {sorted(missing)}")

    out = df.copy()
    out["team"] = out["team"].map(standardize_team_name)
    out["rank"] = _to_numeric(out["rank"])
    out["points"] = _to_numeric(out["points"])
    out["ranking_date"] = pd.to_datetime(out["ranking_date"], errors="coerce")

    out = out.dropna(subset=["team", "rank", "points", "ranking_date"]).copy()
    out["rank"] = out["rank"].astype(int)
    out = out.sort_values(["team", "ranking_date", "rank"], ascending=[True, False, True])
    out = out.drop_duplicates(subset=["team"], keep="first")

    columns = ["team", "rank", "points", "ranking_date"]
    if "team_code" in out.columns:
        columns.append("team_code")

    out = out[columns].rename(
        columns={
            "rank": "fifa_rank",
            "points": "fifa_points",
            "ranking_date": "fifa_ranking_date",
        }
    )
    return out.reset_index(drop=True)


def clean_elo_ratings(df: pd.DataFrame) -> pd.DataFrame:
    """Clean Elo ratings and keep one latest row per team."""
    required = {"rank", "team", "elo", "rating_date"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Elo ratings missing required columns: {sorted(missing)}")

    out = df.copy()
    out["team"] = out["team"].map(standardize_team_name)
    out["rank"] = _to_numeric(out["rank"])
    out["elo"] = _to_numeric(out["elo"])
    out["rating_date"] = pd.to_datetime(out["rating_date"], errors="coerce")

    out = out.dropna(subset=["team", "rank", "elo", "rating_date"]).copy()
    out["rank"] = out["rank"].astype(int)
    out = out.sort_values(["team", "rating_date", "rank"], ascending=[True, False, True])
    out = out.drop_duplicates(subset=["team"], keep="first")

    out = out[["team", "rank", "elo", "rating_date"]].rename(
        columns={
            "rank": "elo_rank",
            "rating_date": "elo_rating_date",
        }
    )
    return out.reset_index(drop=True)


def build_team_strength_snapshot(
    fifa_df: pd.DataFrame,
    elo_df: pd.DataFrame,
) -> pd.DataFrame:
    """Build a team-level strength snapshot from FIFA points and Elo."""
    fifa_clean = clean_fifa_rankings(fifa_df)
    elo_clean = clean_elo_ratings(elo_df)

    merged = fifa_clean.merge(elo_clean, on="team", how="outer")
    merged["has_fifa_ranking"] = merged["fifa_rank"].notna().astype(int)
    merged["has_elo"] = merged["elo"].notna().astype(int)

    merged["fifa_points_norm"] = _min_max_normalize(merged.get("fifa_points", pd.Series(dtype=float)))
    merged["elo_norm"] = _min_max_normalize(merged.get("elo", pd.Series(dtype=float)))

    strength_values = []
    for _, row in merged.iterrows():
        values = []
        if pd.notna(row.get("fifa_points_norm")) and int(row.get("has_fifa_ranking", 0)) == 1:
            values.append(float(row["fifa_points_norm"]))
        if pd.notna(row.get("elo_norm")) and int(row.get("has_elo", 0)) == 1:
            values.append(float(row["elo_norm"]))
        strength_values.append(float(np.mean(values)) if values else 0.0)

    merged["team_strength_score"] = strength_values

    ordered_cols = [
        "team",
        "fifa_rank",
        "fifa_points",
        "fifa_ranking_date",
        "elo_rank",
        "elo",
        "elo_rating_date",
        "has_fifa_ranking",
        "has_elo",
        "fifa_points_norm",
        "elo_norm",
        "team_strength_score",
    ]
    for col in ordered_cols:
        if col not in merged.columns:
            merged[col] = np.nan
    return merged[ordered_cols].reset_index(drop=True)


def add_ranking_features_to_matches(
    feature_df: pd.DataFrame,
    team_strength_df: pd.DataFrame,
) -> pd.DataFrame:
    """Join team strength snapshot to team_a/team_b and derive diff features."""
    out = feature_df.copy()

    left_cols = {
        "team": "team_a",
        "fifa_rank": "team_a_fifa_rank",
        "fifa_points": "team_a_fifa_points",
        "has_fifa_ranking": "team_a_has_fifa_ranking",
        "elo_rank": "team_a_elo_rank",
        "elo": "team_a_elo",
        "has_elo": "team_a_has_elo",
        "team_strength_score": "team_a_strength_score",
    }
    right_cols = {
        "team": "team_b",
        "fifa_rank": "team_b_fifa_rank",
        "fifa_points": "team_b_fifa_points",
        "has_fifa_ranking": "team_b_has_fifa_ranking",
        "elo_rank": "team_b_elo_rank",
        "elo": "team_b_elo",
        "has_elo": "team_b_has_elo",
        "team_strength_score": "team_b_strength_score",
    }

    team_strength_left = team_strength_df[list(left_cols.keys())].rename(columns=left_cols)
    team_strength_right = team_strength_df[list(right_cols.keys())].rename(columns=right_cols)

    out = out.merge(team_strength_left, on="team_a", how="left")
    out = out.merge(team_strength_right, on="team_b", how="left")

    out["team_a_has_fifa_ranking"] = out["team_a_has_fifa_ranking"].fillna(0).astype(int)
    out["team_b_has_fifa_ranking"] = out["team_b_has_fifa_ranking"].fillna(0).astype(int)
    out["team_a_has_elo"] = out["team_a_has_elo"].fillna(0).astype(int)
    out["team_b_has_elo"] = out["team_b_has_elo"].fillna(0).astype(int)

    out["diff_fifa_rank"] = _to_numeric(out["team_b_fifa_rank"]) - _to_numeric(out["team_a_fifa_rank"])
    out["diff_fifa_points"] = _to_numeric(out["team_a_fifa_points"]) - _to_numeric(out["team_b_fifa_points"])
    out["diff_elo_rank"] = _to_numeric(out["team_b_elo_rank"]) - _to_numeric(out["team_a_elo_rank"])
    out["diff_elo"] = _to_numeric(out["team_a_elo"]) - _to_numeric(out["team_b_elo"])
    out["diff_strength_score"] = _to_numeric(out["team_a_strength_score"]) - _to_numeric(out["team_b_strength_score"])

    return out


def create_ranking_merge_report(ranking_feature_df: pd.DataFrame) -> pd.DataFrame:
    """Create report describing ranking/elo coverage after merge."""
    if ranking_feature_df.empty:
        rows = [("total_rows", 0)]
        return pd.DataFrame(rows, columns=["metric", "value"])

    unique_teams = set(pd.unique(ranking_feature_df[["team_a", "team_b"]].values.ravel("K")))

    rows = [
        ("total_rows", int(len(ranking_feature_df))),
        ("teams_in_matches", int(len(unique_teams))),
        ("teams_with_fifa_ranking", int((ranking_feature_df["team_a_has_fifa_ranking"] == 1).sum() + (ranking_feature_df["team_b_has_fifa_ranking"] == 1).sum())),
        ("teams_missing_fifa_ranking", int((ranking_feature_df["team_a_has_fifa_ranking"] == 0).sum() + (ranking_feature_df["team_b_has_fifa_ranking"] == 0).sum())),
        ("teams_with_elo", int((ranking_feature_df["team_a_has_elo"] == 1).sum() + (ranking_feature_df["team_b_has_elo"] == 1).sum())),
        ("teams_missing_elo", int((ranking_feature_df["team_a_has_elo"] == 0).sum() + (ranking_feature_df["team_b_has_elo"] == 0).sum())),
        ("rows_with_both_fifa_rankings", int(((ranking_feature_df["team_a_has_fifa_ranking"] == 1) & (ranking_feature_df["team_b_has_fifa_ranking"] == 1)).sum())),
        ("rows_with_both_elo_ratings", int(((ranking_feature_df["team_a_has_elo"] == 1) & (ranking_feature_df["team_b_has_elo"] == 1)).sum())),
        ("rows_with_both_strength_scores", int((ranking_feature_df["team_a_strength_score"].notna() & ranking_feature_df["team_b_strength_score"].notna()).sum())),
        ("missing_team_a_fifa_rank", int(ranking_feature_df["team_a_fifa_rank"].isna().sum())),
        ("missing_team_b_fifa_rank", int(ranking_feature_df["team_b_fifa_rank"].isna().sum())),
        ("missing_team_a_elo", int(ranking_feature_df["team_a_elo"].isna().sum())),
        ("missing_team_b_elo", int(ranking_feature_df["team_b_elo"].isna().sum())),
    ]
    return pd.DataFrame(rows, columns=["metric", "value"])


def create_ranking_feature_summary(
    ranking_feature_df: pd.DataFrame,
    mode: str = "snapshot",
) -> dict:
    """Return JSON-serializable summary for Step 7 ranking features."""
    date_series = pd.to_datetime(ranking_feature_df.get("date", pd.Series(dtype=object)), errors="coerce")
    ranking_feature_columns_added = [
        col
        for col in (FIFA_RANKING_FEATURE_COLUMNS + ELO_FEATURE_COLUMNS + TEAM_STRENGTH_FEATURE_COLUMNS)
        if col in ranking_feature_df.columns
    ]

    summary = {
        "status": "ok" if not ranking_feature_df.empty else "empty",
        "mode": mode,
        "rows": int(len(ranking_feature_df)),
        "columns": int(len(ranking_feature_df.columns)),
        "date_min": str(date_series.min()) if not date_series.empty else None,
        "date_max": str(date_series.max()) if not date_series.empty else None,
        "unique_teams": int(len(pd.unique(ranking_feature_df[["team_a", "team_b"]].values.ravel("K"))))
        if not ranking_feature_df.empty and {"team_a", "team_b"}.issubset(ranking_feature_df.columns)
        else 0,
        "ranking_feature_columns_added": ranking_feature_columns_added,
        "missing_fifa_rows": int(
            ((ranking_feature_df.get("team_a_has_fifa_ranking", 0) == 0) | (ranking_feature_df.get("team_b_has_fifa_ranking", 0) == 0)).sum()
        )
        if not ranking_feature_df.empty
        else 0,
        "missing_elo_rows": int(
            ((ranking_feature_df.get("team_a_has_elo", 0) == 0) | (ranking_feature_df.get("team_b_has_elo", 0) == 0)).sum()
        )
        if not ranking_feature_df.empty
        else 0,
        "notes": [
            "Snapshot ranking mode uses the latest available ranking table for all rows. This is useful for future prediction preparation but should be replaced with historical ranking joins for strict historical backtesting.",
        ],
    }
    return summary
