"""Tests for official team name enrichment utilities."""

from __future__ import annotations

import pandas as pd

from src.official.team_name_enrichment import (
    enrich_official_teams_dataframe,
    format_official_teams_for_display,
    is_valid_team_name,
    repair_official_teams_artifact,
    teams_need_name_repair,
)


def test_is_valid_team_name_rejects_blank_and_nan_tokens() -> None:
    assert is_valid_team_name("France") is True
    assert is_valid_team_name(None) is False
    assert is_valid_team_name("nan") is False
    assert is_valid_team_name("TBD") is False


def test_enrich_official_teams_dataframe_fills_from_groups_by_row_index() -> None:
    teams_df = pd.DataFrame(
        {
            "team_id": ["team_001", "team_002"],
            "team": [None, None],
            "team_code": [None, None],
            "confederation": [None, None],
            "group": [None, None],
            "group_slot": [None, None],
            "is_host": [None, None],
            "qualified": [None, None],
            "source": [None, None],
            "last_verified_at": [None, None],
        }
    )
    groups_df = pd.DataFrame(
        {
            "group": ["A", "A"],
            "slot": [1, 2],
            "team": ["Czechia", "Mexico"],
            "team_code": ["CZE", "MEX"],
            "confederation": ["UEFA", "CONCACAF"],
            "is_host": [0, 0],
            "source": ["fifa_schedule_api", "fifa_schedule_api"],
            "last_verified_at": ["2026-01-01", "2026-01-01"],
        }
    )

    enriched = enrich_official_teams_dataframe(teams_df, groups_df=groups_df, populated_df=pd.DataFrame())

    assert teams_need_name_repair(teams_df) is True
    assert teams_need_name_repair(enriched) is False
    assert enriched.iloc[0]["team"] == "Czechia"
    assert enriched.iloc[1]["team"] == "Mexico"
    assert enriched.iloc[0]["team_code"] == "CZE"
    assert enriched.iloc[0]["group"] == "A"


def test_enrich_official_teams_dataframe_prefers_populated_group_slot_match() -> None:
    teams_df = pd.DataFrame(
        {
            "team_id": ["team_010"],
            "team": [""],
            "team_code": [""],
            "confederation": [""],
            "group": ["C"],
            "group_slot": [3],
            "is_host": [0],
            "qualified": [1],
            "source": [""],
            "last_verified_at": [""],
        }
    )
    groups_df = pd.DataFrame(
        {
            "group": ["C"],
            "slot": [3],
            "team": ["Brazil"],
            "team_code": ["BRA"],
            "confederation": ["CONMEBOL"],
            "is_host": [0],
            "source": ["groups"],
            "last_verified_at": [""],
        }
    )
    populated_df = pd.DataFrame(
        {
            "team": ["Brazil"],
            "team_code": ["BRA"],
            "confederation": ["CONMEBOL"],
            "group": ["C"],
            "group_slot": [3],
            "is_host": [0],
            "qualified": [1],
            "source": ["fifa_schedule_api"],
        }
    )

    enriched = enrich_official_teams_dataframe(teams_df, groups_df=groups_df, populated_df=populated_df)
    assert enriched.iloc[0]["team"] == "Brazil"
    assert enriched.iloc[0]["source"] == "fifa_schedule_api"


def test_format_official_teams_for_display_uses_friendly_headers() -> None:
    teams_df = pd.DataFrame(
        {
            "team_id": ["team_001"],
            "team": [""],
            "team_code": ["CZE"],
            "confederation": ["UEFA"],
            "group": ["A"],
            "group_slot": [1],
            "is_host": [0],
            "qualified": [1],
            "source": ["fifa_schedule_api"],
            "last_verified_at": ["2026-01-01"],
        }
    )
    groups_df = pd.DataFrame(
        {
            "group": ["A"],
            "slot": [1],
            "team": ["Czechia"],
            "team_code": ["CZE"],
            "confederation": ["UEFA"],
            "is_host": [0],
            "source": ["fifa_schedule_api"],
            "last_verified_at": ["2026-01-01"],
        }
    )

    display = format_official_teams_for_display(
        enrich_official_teams_dataframe(teams_df, groups_df=groups_df, populated_df=pd.DataFrame())
    )

    assert list(display.columns) == [
        "Team",
        "Code",
        "Group",
        "Slot",
        "Confederation",
        "Host nation",
        "Qualified",
        "Source",
        "Last updated",
    ]
    assert display.iloc[0]["Team"] == "Czechia"
    assert display.iloc[0]["Host nation"] == "No"


def test_repair_official_teams_artifact_persists_fixed_rows(tmp_path, monkeypatch) -> None:
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir(parents=True)
    teams_path = processed_dir / "official_teams.csv"
    groups_path = processed_dir / "official_groups.csv"

    pd.DataFrame(
        {
            "team_id": ["team_001"],
            "team": [None],
            "team_code": [None],
            "confederation": [None],
            "group": [None],
            "group_slot": [None],
            "is_host": [None],
            "qualified": [None],
            "source": [None],
            "last_verified_at": [None],
        }
    ).to_csv(teams_path, index=False)
    pd.DataFrame(
        {
            "group": ["A"],
            "slot": [1],
            "team": ["Czechia"],
            "team_code": ["CZE"],
            "confederation": ["UEFA"],
            "is_host": [0],
            "source": ["fifa_schedule_api"],
            "last_verified_at": ["2026-01-01"],
        }
    ).to_csv(groups_path, index=False)

    path_fn = lambda name: processed_dir / name
    monkeypatch.setattr("src.official.loaders.official_path", path_fn)
    monkeypatch.setattr("src.official.team_name_enrichment.official_path", path_fn)

    repaired, changed = repair_official_teams_artifact(persist=True)
    assert changed is True
    assert repaired.iloc[0]["team"] == "Czechia"

    saved = pd.read_csv(teams_path)
    assert saved.iloc[0]["team"] == "Czechia"
