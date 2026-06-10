"""Tests for official World Cup data validators."""

from __future__ import annotations

import pandas as pd

from src.official.validators import (
    validate_fixture_team_consistency,
    validate_official_data_bundle,
    validate_official_fixtures,
    validate_official_groups,
    validate_official_teams,
    validate_official_venues,
)


def _valid_teams_df() -> pd.DataFrame:
    rows = []
    groups = [chr(ord("A") + i) for i in range(12)]
    for gi, group in enumerate(groups):
        for slot in range(1, 5):
            idx = gi * 4 + slot
            rows.append(
                {
                    "team_id": f"team-{idx:02d}",
                    "team": f"Team {idx:02d}",
                    "team_code": f"T{idx:02d}",
                    "confederation": "UEFA",
                    "group": group,
                    "group_slot": slot,
                    "is_host": 0,
                    "qualified": 1,
                    "source": "verified_official",
                    "last_verified_at": "2026-06-05",
                }
            )
    return pd.DataFrame(rows)


def _valid_groups_df(teams_df: pd.DataFrame) -> pd.DataFrame:
    return teams_df.rename(columns={"group_slot": "slot"})[["group", "slot", "team", "team_code", "confederation", "is_host", "source", "last_verified_at"]].copy()


def _valid_fixtures_df(teams_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    match_number = 1
    for group, group_df in teams_df.groupby("group"):
        teams = group_df.sort_values("group_slot").to_dict(orient="records")
        pairings = [(0, 1), (2, 3), (0, 2), (3, 1), (3, 0), (1, 2)]
        for day_idx, (a, b) in enumerate(pairings, start=1):
            team_a = teams[a]
            team_b = teams[b]
            rows.append(
                {
                    "match_id": f"M-{match_number:03d}",
                    "match_number": match_number,
                    "stage": "group_stage",
                    "group": group,
                    "date": "2026-06-15",
                    "kickoff_local": "19:00",
                    "kickoff_utc": "23:00Z",
                    "timezone": "UTC-04:00",
                    "venue": f"Venue {group}",
                    "stadium": f"Stadium {group}",
                    "city": f"City {group}",
                    "country": "United States",
                    "team_a": team_a["team"],
                    "team_b": team_b["team"],
                    "team_a_code": team_a["team_code"],
                    "team_b_code": team_b["team_code"],
                    "team_a_group_slot": team_a["group_slot"],
                    "team_b_group_slot": team_b["group_slot"],
                    "status": "scheduled",
                    "source": "verified_official",
                    "last_verified_at": "2026-06-05",
                }
            )
            match_number += 1
    return pd.DataFrame(rows)


def _valid_venues_df() -> pd.DataFrame:
    groups = [chr(ord("A") + i) for i in range(12)]
    return pd.DataFrame(
        {
            "venue_id": [f"venue-{g.lower()}" for g in groups],
            "stadium": [f"Stadium {g}" for g in groups],
            "venue": [f"Venue {g}" for g in groups],
            "city": [f"City {g}" for g in groups],
            "country": ["United States"] * 12,
            "timezone": ["UTC-04:00"] * 12,
            "capacity": [60000] * 12,
            "latitude": [40.0] * 12,
            "longitude": [-74.0] * 12,
            "source": ["verified_official"] * 12,
            "last_verified_at": ["2026-06-05"] * 12,
        }
    )


def _valid_calendar_df(fixtures_df: pd.DataFrame) -> pd.DataFrame:
    return fixtures_df[["match_id", "match_number", "stage", "group", "date", "kickoff_local", "kickoff_utc", "timezone", "venue", "city", "country", "team_a", "team_b", "status", "source", "last_verified_at"]].copy()


def test_validate_official_teams_passes_valid_synthetic_48_teams() -> None:
    valid, report = validate_official_teams(_valid_teams_df())
    assert valid is True
    assert not report.empty


def test_validate_official_teams_fails_duplicate_team() -> None:
    teams = _valid_teams_df()
    teams.loc[1, "team"] = teams.loc[0, "team"]
    valid, report = validate_official_teams(teams)
    assert valid is False
    assert (report["check"] == "teams_no_duplicate_team").any()


def test_validate_official_groups_fails_invalid_group_size() -> None:
    groups = _valid_groups_df(_valid_teams_df()).iloc[:-1].copy()
    valid, report = validate_official_groups(groups)
    assert valid is False
    assert (report["check"] == "groups_exactly_48_rows").any()


def test_validate_official_fixtures_flags_team_not_in_official_teams() -> None:
    teams = _valid_teams_df()
    fixtures = _valid_fixtures_df(teams)
    venues = _valid_venues_df()
    fixtures.loc[0, "team_a"] = "Not Official"
    valid, report = validate_official_fixtures(fixtures, teams_df=teams, venues_df=venues)
    assert valid is False
    assert (report["check"] == "fixtures_teams_in_official_list").any()


def test_validate_official_venues_flags_placeholder_venue() -> None:
    venues = _valid_venues_df()
    venues.loc[0, "venue"] = "Unknown"
    valid, report = validate_official_venues(venues)
    assert valid is False
    assert report["check"].str.contains("venues_venue_no_placeholder").any()


def test_validate_fixture_team_consistency_checks_group_stage_appearances() -> None:
    teams = _valid_teams_df()
    fixtures = _valid_fixtures_df(teams)
    valid, report = validate_fixture_team_consistency(fixtures, teams)
    assert valid is True
    assert (report["check"] == "group_stage_team_appearances_exactly_3").any()


def test_validate_official_data_bundle_combines_reports() -> None:
    teams = _valid_teams_df()
    groups = _valid_groups_df(teams)
    fixtures = _valid_fixtures_df(teams)
    venues = _valid_venues_df()
    calendar = _valid_calendar_df(fixtures)
    valid, report = validate_official_data_bundle(teams, groups, fixtures, venues, calendar)
    assert valid is True
    assert not report.empty
