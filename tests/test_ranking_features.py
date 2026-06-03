"""Tests for Step 7 ranking feature engineering."""

from __future__ import annotations

import pandas as pd

from src.features.ranking_features import (
    add_ranking_features_to_matches,
    build_team_strength_snapshot,
    clean_elo_ratings,
    clean_fifa_rankings,
    create_ranking_merge_report,
)


def _fifa_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "rank": [1, 2, 6],
            "team": ["France", "Spain", "Brazil"],
            "team_code": ["FRA", "ESP", "BRA"],
            "points": [1877.32, 1876.40, 1761.60],
            "ranking_date": ["2026-04-01", "2026-04-01", "2026-04-01"],
        }
    )


def _elo_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "rank": [3, 1, 5],
            "team": ["France", "Spain", "Brazil"],
            "elo": [2081, 2165, 1984],
            "rating_date": ["2026-05-31", "2026-05-31", "2026-05-31"],
        }
    )


def test_clean_fifa_rankings_standardizes_columns() -> None:
    out = clean_fifa_rankings(_fifa_df())
    assert {"team", "fifa_rank", "fifa_points", "fifa_ranking_date"}.issubset(out.columns)
    assert len(out) == 3


def test_clean_elo_ratings_standardizes_columns() -> None:
    out = clean_elo_ratings(_elo_df())
    assert {"team", "elo_rank", "elo", "elo_rating_date"}.issubset(out.columns)
    assert len(out) == 3


def test_build_team_strength_snapshot_creates_strength_score() -> None:
    out = build_team_strength_snapshot(_fifa_df(), _elo_df())
    assert "team_strength_score" in out.columns
    assert out["team_strength_score"].between(0, 1).all()


def test_add_ranking_features_to_matches_adds_diff_columns() -> None:
    feature_df = pd.DataFrame(
        {
            "match_id": ["m1", "m2"],
            "date": pd.to_datetime(["2026-06-01", "2026-06-02"]),
            "team_a": ["France", "Brazil"],
            "team_b": ["Brazil", "Spain"],
            "result": [2, 0],
            "result_label": ["team_a_win", "team_a_loss"],
        }
    )
    strength_df = build_team_strength_snapshot(_fifa_df(), _elo_df())
    out = add_ranking_features_to_matches(feature_df, strength_df)

    assert "diff_fifa_rank" in out.columns
    assert "diff_elo" in out.columns
    assert "diff_strength_score" in out.columns


def test_create_ranking_merge_report_expected_metrics() -> None:
    feature_df = pd.DataFrame(
        {
            "team_a": ["France"],
            "team_b": ["Brazil"],
            "team_a_has_fifa_ranking": [1],
            "team_b_has_fifa_ranking": [1],
            "team_a_has_elo": [1],
            "team_b_has_elo": [1],
            "team_a_fifa_rank": [1],
            "team_b_fifa_rank": [6],
            "team_a_elo": [2081],
            "team_b_elo": [1984],
            "team_a_strength_score": [0.9],
            "team_b_strength_score": [0.7],
        }
    )
    report = create_ranking_merge_report(feature_df)
    assert {"metric", "value"}.issubset(report.columns)
    assert "total_rows" in set(report["metric"])
