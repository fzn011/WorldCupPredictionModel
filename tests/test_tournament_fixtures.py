"""Tests for Step 11 tournament fixtures utilities."""

from __future__ import annotations

import pandas as pd

from src.tournament.fixtures import (
    generate_group_stage_fixtures,
    validate_group_stage_fixtures,
)
from src.tournament.groups import load_tournament_groups


def test_generate_group_stage_fixtures_creates_72_rows() -> None:
    groups_df = load_tournament_groups(path="data/sample/sample_tournament_groups.csv")
    fixtures_df = generate_group_stage_fixtures(groups_df)
    assert len(fixtures_df) == 72


def test_generate_group_stage_fixtures_has_6_matches_per_group() -> None:
    groups_df = load_tournament_groups(path="data/sample/sample_tournament_groups.csv")
    fixtures_df = generate_group_stage_fixtures(groups_df)
    counts = fixtures_df.groupby("group")["match_id"].count()
    assert (counts == 6).all()


def test_each_team_plays_3_matches() -> None:
    groups_df = load_tournament_groups(path="data/sample/sample_tournament_groups.csv")
    fixtures_df = generate_group_stage_fixtures(groups_df)
    teams_df = pd.concat(
        [
            fixtures_df[["group", "team_a"]].rename(columns={"team_a": "team"}),
            fixtures_df[["group", "team_b"]].rename(columns={"team_b": "team"}),
        ],
        ignore_index=True,
    )
    counts = teams_df.groupby(["group", "team"]).size()
    assert (counts == 3).all()


def test_validate_group_stage_fixtures_passes_generated_fixtures() -> None:
    groups_df = load_tournament_groups(path="data/sample/sample_tournament_groups.csv")
    fixtures_df = generate_group_stage_fixtures(groups_df)
    is_valid, report_df = validate_group_stage_fixtures(fixtures_df, groups_df)
    assert is_valid is True
    assert report_df["passed"].all()


def test_no_team_plays_itself() -> None:
    groups_df = load_tournament_groups(path="data/sample/sample_tournament_groups.csv")
    fixtures_df = generate_group_stage_fixtures(groups_df)
    assert (fixtures_df["team_a"] != fixtures_df["team_b"]).all()
