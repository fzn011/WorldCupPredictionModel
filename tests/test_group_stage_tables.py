"""Tests for Step 12 group table building/ranking/qualification."""

from __future__ import annotations

import pandas as pd

from src.simulation.group_stage import (
    build_group_tables,
    rank_group_tables,
    select_group_qualifiers,
    validate_group_stage_simulation,
)
from src.tournament.fixtures import generate_group_stage_fixtures
from src.tournament.groups import load_tournament_groups


def _sample_group_matches() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"match_id": "G-A-01", "group": "A", "team_a": "Mexico", "team_b": "South Africa", "team_a_score": 2, "team_b_score": 0},
            {"match_id": "G-A-02", "group": "A", "team_a": "South Korea", "team_b": "Czechia", "team_a_score": 1, "team_b_score": 1},
            {"match_id": "G-A-03", "group": "A", "team_a": "Mexico", "team_b": "South Korea", "team_a_score": 1, "team_b_score": 1},
            {"match_id": "G-A-04", "group": "A", "team_a": "Czechia", "team_b": "South Africa", "team_a_score": 0, "team_b_score": 1},
            {"match_id": "G-A-05", "group": "A", "team_a": "Czechia", "team_b": "Mexico", "team_a_score": 0, "team_b_score": 2},
            {"match_id": "G-A-06", "group": "A", "team_a": "South Africa", "team_b": "South Korea", "team_a_score": 0, "team_b_score": 2},
        ]
    )


def test_build_group_tables_computes_points_correctly() -> None:
    tables = build_group_tables(_sample_group_matches())
    mexico_points = int(tables.loc[tables["team"] == "Mexico", "points"].iloc[0])
    assert mexico_points == 7


def test_rank_group_tables_tiebreak_order() -> None:
    tables = build_group_tables(_sample_group_matches())
    ranked = rank_group_tables(tables)
    top_team = ranked.loc[(ranked["group"] == "A") & (ranked["group_rank"] == 1), "team"].iloc[0]
    assert top_team == "Mexico"


def test_select_group_qualifiers_returns_top_two_plus_best_thirds() -> None:
    groups_df = load_tournament_groups(path="data/sample/sample_tournament_groups.csv")
    fixtures_df = generate_group_stage_fixtures(groups_df)

    # Deterministic synthetic results: team_a wins each match 1-0
    simulated = fixtures_df[["match_id", "group", "team_a", "team_b"]].copy()
    simulated["team_a_score"] = 1
    simulated["team_b_score"] = 0

    tables = build_group_tables(simulated)
    ranked = rank_group_tables(tables)
    auto_df, third_df, qualifiers_df = select_group_qualifiers(ranked)

    assert len(auto_df) == 24
    assert len(third_df) == 8
    assert len(qualifiers_df) == 32


def test_validate_group_stage_simulation_passes_for_valid_generated_data() -> None:
    groups_df = load_tournament_groups(path="data/sample/sample_tournament_groups.csv")
    fixtures_df = generate_group_stage_fixtures(groups_df)

    simulated = fixtures_df[["match_id", "group", "team_a", "team_b"]].copy()
    simulated["team_a_score"] = 1
    simulated["team_b_score"] = 0

    tables = build_group_tables(simulated)
    ranked = rank_group_tables(tables)
    auto_df, third_df, qualifiers_df = select_group_qualifiers(ranked)

    valid, report = validate_group_stage_simulation(simulated, ranked, qualifiers_df)
    assert valid is True
    assert report["passed"].all()
