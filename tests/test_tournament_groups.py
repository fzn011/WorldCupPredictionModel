"""Tests for Step 11 tournament groups utilities."""

from __future__ import annotations

import pandas as pd

from src.tournament.groups import (
    create_group_lookup,
    load_tournament_groups,
    validate_tournament_groups,
)


def test_load_tournament_groups_returns_dataframe() -> None:
    df = load_tournament_groups()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_validate_tournament_groups_passes_sample_data() -> None:
    df = load_tournament_groups(path="data/sample/sample_tournament_groups.csv")
    is_valid, report_df = validate_tournament_groups(df)
    assert is_valid is True
    assert report_df["passed"].all()


def test_validate_tournament_groups_duplicate_teams_fail() -> None:
    df = load_tournament_groups(path="data/sample/sample_tournament_groups.csv")
    df.loc[df.index[0], "team"] = df.loc[df.index[1], "team"]
    is_valid, report_df = validate_tournament_groups(df)
    assert is_valid is False
    assert bool(report_df.loc[report_df["check"] == "no_duplicate_team_names", "passed"].iloc[0]) is False


def test_validate_tournament_groups_invalid_group_size_fail() -> None:
    df = load_tournament_groups(path="data/sample/sample_tournament_groups.csv")
    df = df[~((df["group"] == "A") & (df["slot"] == 4))]
    is_valid, report_df = validate_tournament_groups(df)
    assert is_valid is False
    assert bool(report_df.loc[report_df["check"] == "group_size_exactly_4", "passed"].iloc[0]) is False


def test_create_group_lookup_returns_expected_nested_dict() -> None:
    df = load_tournament_groups(path="data/sample/sample_tournament_groups.csv")
    lookup = create_group_lookup(df)
    assert "A" in lookup
    assert set(lookup["A"].keys()) == {1, 2, 3, 4}
    assert isinstance(lookup["A"][1], str)
