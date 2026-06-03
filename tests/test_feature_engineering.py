"""Tests for the placeholder feature-engineering pipeline."""

from __future__ import annotations

from src.data.load_data import load_sample_matches
from src.data.clean_data import clean_match_results, create_match_result_column
from src.features.build_features import build_basic_features


def test_basic_feature_pipeline() -> None:
    df = load_sample_matches()
    df = clean_match_results(df)
    df = create_match_result_column(df)
    df = build_basic_features(df)

    for col in ("goal_difference", "total_goals", "is_draw", "result"):
        assert col in df.columns, f"missing column: {col}"

    assert len(df) > 0
