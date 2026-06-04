"""Tests for Step 11 knockout placeholder structure."""

from __future__ import annotations

from src.tournament.knockout import create_knockout_placeholders


def test_create_knockout_placeholders_round_counts() -> None:
    df = create_knockout_placeholders()
    counts = df.groupby("round")["match_id"].count().to_dict()
    assert counts.get("round_of_32") == 16
    assert counts.get("round_of_16") == 8
    assert counts.get("quarter_final") == 4
    assert counts.get("semi_final") == 2
    assert counts.get("third_place") == 1
    assert counts.get("final") == 1


def test_final_row_exists() -> None:
    df = create_knockout_placeholders()
    assert (df["match_id"] == "F-01").any()


def test_total_knockout_placeholder_matches_equals_32() -> None:
    df = create_knockout_placeholders()
    assert len(df) == 32
