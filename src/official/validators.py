"""Validators for the official World Cup 2026 data bundle."""

from __future__ import annotations

from typing import Any

import pandas as pd

import src.utils.constants as C
from src.official.official_data_contracts import check_required_columns, get_official_contract
from src.official.stage_normalization import is_group_stage_label
from src.utils.team_name_mapping import standardize_team_name

OFFICIAL_PLACEHOLDER_VALUES = {str(value).strip() for value in getattr(C, "OFFICIAL_PLACEHOLDER_VALUES", [])}
OFFICIAL_REQUIRED_TEAM_COUNT = int(getattr(C, "OFFICIAL_REQUIRED_TEAM_COUNT", 48))
OFFICIAL_REQUIRED_GROUP_COUNT = int(getattr(C, "OFFICIAL_REQUIRED_GROUP_COUNT", 12))
OFFICIAL_TEAMS_PER_GROUP = int(getattr(C, "OFFICIAL_TEAMS_PER_GROUP", 4))
OFFICIAL_TOTAL_MATCHES = int(getattr(C, "OFFICIAL_TOTAL_MATCHES", 104))
OFFICIAL_GROUP_STAGE_MATCHES = int(getattr(C, "OFFICIAL_GROUP_STAGE_MATCHES", 72))
WC2026_GROUPS = list(getattr(C, "WC2026_GROUPS", ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]))

OPTIONAL_PLACEHOLDER_FIELDS: dict[str, set[str]] = {
    "teams": {"team_code", "confederation"},
    "groups": {"team_code", "confederation"},
    "venues": {"timezone", "capacity", "latitude", "longitude", "venue_id"},
    "fixtures": {
        "timezone",
        "kickoff_utc",
        "team_a_code",
        "team_b_code",
        "team_a_group_slot",
        "team_b_group_slot",
        "group",
    },
    "players": {
        "first_names",
        "last_names",
        "club",
        "club_country",
        "date_of_birth",
        "age_at_tournament_start",
        "shirt_number",
        "height_cm",
    },
}


def create_validation_row(check: str, expected, actual, passed: bool, severity: str = "error") -> dict:
    """Create one validation row for an official-data report."""
    return {
        "check": check,
        "expected": expected,
        "actual": actual,
        "passed": bool(passed),
        "severity": severity,
    }



def _source_series(df: pd.DataFrame) -> pd.Series:
    if "source" not in df.columns:
        return pd.Series(["sample_to_be_verified"] * len(df), index=df.index)
    return df["source"].fillna("sample_to_be_verified").astype(str)



def validate_no_placeholder_values(df, columns: list[str], dataset_name: str) -> tuple[bool, pd.DataFrame]:
    """Flag placeholder values; optional metadata gaps are warnings, not errors."""
    rows: list[dict[str, Any]] = []
    source = _source_series(df)
    optional_cols = OPTIONAL_PLACEHOLDER_FIELDS.get(dataset_name, set())
    for column in columns:
        if column not in df.columns:
            continue
        values = df[column].fillna("").astype(str).str.strip()
        token_placeholders = values.isin(OFFICIAL_PLACEHOLDER_VALUES - {""}) | values.str.startswith("TBD", na=False)
        empty_values = values.eq("")
        is_placeholder = token_placeholders | (empty_values if column not in optional_cols else pd.Series(False, index=values.index))
        failed_count = int(is_placeholder.sum())
        optional_gaps = int((empty_values | token_placeholders).sum()) if column in optional_cols else 0
        if failed_count == 0 and optional_gaps == 0:
            rows.append(create_validation_row(f"{dataset_name}_{column}_no_placeholder", "0 placeholders", 0, True, "error"))
            continue
        if column in optional_cols:
            severity = "warning"
            failed_count = optional_gaps
        else:
            sample_like = source[is_placeholder].eq("sample_to_be_verified").all() if failed_count else True
            severity = "warning" if sample_like else "error"
        rows.append(
            create_validation_row(
                f"{dataset_name}_{column}_no_placeholder",
                "0 placeholders",
                failed_count,
                failed_count == 0,
                severity,
            )
        )
    report_df = pd.DataFrame(rows)
    no_errors = not ((report_df["severity"] == "error") & (~report_df["passed"])).any() if not report_df.empty else True
    return bool(no_errors), report_df



def validate_official_teams(teams_df: pd.DataFrame) -> tuple[bool, pd.DataFrame]:
    """Validate official teams table against the official data contract."""
    rows: list[dict[str, Any]] = []
    required = get_official_contract("teams")
    ok, missing = check_required_columns(teams_df, required, "teams")
    rows.append(create_validation_row("teams_required_columns", required, missing if missing else "ok", ok))
    if not ok:
        report_df = pd.DataFrame(rows)
        return False, report_df

    teams = teams_df.copy()
    teams["team"] = teams["team"].map(standardize_team_name)
    rows.append(create_validation_row("teams_exactly_48", OFFICIAL_REQUIRED_TEAM_COUNT, int(len(teams)), len(teams) == OFFICIAL_REQUIRED_TEAM_COUNT))
    rows.append(create_validation_row("teams_no_duplicate_team", 0, int(teams["team"].duplicated().sum()), teams["team"].duplicated().sum() == 0))

    non_empty_codes = teams[teams["team_code"].fillna("").astype(str).str.strip().ne("")]["team_code"].astype(str)
    rows.append(create_validation_row("teams_no_duplicate_team_codes", 0, int(non_empty_codes.duplicated().sum()), non_empty_codes.duplicated().sum() == 0))

    groups = sorted(teams["group"].astype(str).str.upper().unique().tolist())
    rows.append(create_validation_row("teams_groups_are_A_to_L", sorted(WC2026_GROUPS), groups, groups == sorted(WC2026_GROUPS)))

    group_counts = teams.groupby("group")["team"].count().to_dict()
    group_counts_ok = len(group_counts) == OFFICIAL_REQUIRED_GROUP_COUNT and all(count == OFFICIAL_TEAMS_PER_GROUP for count in group_counts.values())
    rows.append(create_validation_row("teams_each_group_has_4", OFFICIAL_TEAMS_PER_GROUP, group_counts, group_counts_ok))

    slots = pd.to_numeric(teams["group_slot"], errors="coerce")
    slots_ok = teams.groupby("group")["group_slot"].apply(lambda s: sorted(pd.to_numeric(s, errors="coerce").dropna().astype(int).tolist()) == [1, 2, 3, 4]).all()
    rows.append(create_validation_row("teams_group_slots_1_to_4", "1-4 per group", slots.tolist()[:8], bool(slots_ok)))

    _, placeholder_df = validate_no_placeholder_values(teams, ["team", "team_code", "group"], "teams")
    rows.extend(placeholder_df.to_dict(orient="records"))

    report_df = pd.DataFrame(rows)
    valid = not (((report_df["severity"] == "error") & (~report_df["passed"])).any())
    return bool(valid), report_df



def validate_official_groups(groups_df: pd.DataFrame) -> tuple[bool, pd.DataFrame]:
    """Validate official groups table."""
    rows: list[dict[str, Any]] = []
    required = get_official_contract("groups")
    ok, missing = check_required_columns(groups_df, required, "groups")
    rows.append(create_validation_row("groups_required_columns", required, missing if missing else "ok", ok))
    if not ok:
        report_df = pd.DataFrame(rows)
        return False, report_df

    groups = groups_df.copy()
    groups["team"] = groups["team"].map(standardize_team_name)
    rows.append(create_validation_row("groups_exactly_48_rows", 48, int(len(groups)), len(groups) == 48))
    group_labels = sorted(groups["group"].astype(str).str.upper().unique().tolist())
    rows.append(create_validation_row("groups_count_12", sorted(WC2026_GROUPS), group_labels, group_labels == sorted(WC2026_GROUPS)))
    group_counts = groups.groupby("group")["team"].count().to_dict()
    rows.append(create_validation_row("groups_each_group_has_4", 4, group_counts, all(count == 4 for count in group_counts.values()) and len(group_counts) == 12))
    slot_ok = groups.groupby("group")["slot"].apply(lambda s: sorted(pd.to_numeric(s, errors="coerce").dropna().astype(int).tolist()) == [1, 2, 3, 4]).all()
    rows.append(create_validation_row("groups_slots_1_to_4", "1-4 per group", bool(slot_ok), bool(slot_ok)))
    rows.append(create_validation_row("groups_no_duplicate_teams", 0, int(groups["team"].duplicated().sum()), groups["team"].duplicated().sum() == 0))
    _, placeholder_df = validate_no_placeholder_values(groups, ["team"], "groups")
    rows.extend(placeholder_df.to_dict(orient="records"))

    report_df = pd.DataFrame(rows)
    valid = not (((report_df["severity"] == "error") & (~report_df["passed"])).any())
    return bool(valid), report_df



def validate_official_venues(venues_df: pd.DataFrame) -> tuple[bool, pd.DataFrame]:
    """Validate official venues table."""
    rows: list[dict[str, Any]] = []
    required = get_official_contract("venues")
    ok, missing = check_required_columns(venues_df, required, "venues")
    rows.append(create_validation_row("venues_required_columns", required, missing if missing else "ok", ok))
    if not ok:
        report_df = pd.DataFrame(rows)
        return False, report_df

    duplicate_rows = int(venues_df.duplicated(subset=["venue", "stadium"]).sum())
    rows.append(create_validation_row("venues_no_duplicate_venue_stadium", 0, duplicate_rows, duplicate_rows == 0))

    _, placeholder_df = validate_no_placeholder_values(venues_df, ["venue", "stadium", "city", "country", "timezone"], "venues")
    rows.extend(placeholder_df.to_dict(orient="records"))

    capacity_numeric = pd.to_numeric(venues_df["capacity"], errors="coerce")
    capacity_ok = venues_df["capacity"].isna().all() or capacity_numeric.dropna().notna().all()
    rows.append(create_validation_row("venues_capacity_numeric_if_present", "numeric or blank", bool(capacity_ok), bool(capacity_ok), "warning" if not capacity_ok else "error"))

    lat_numeric = pd.to_numeric(venues_df["latitude"], errors="coerce")
    lon_numeric = pd.to_numeric(venues_df["longitude"], errors="coerce")
    geo_ok = (venues_df["latitude"].isna() | lat_numeric.notna()).all() and (venues_df["longitude"].isna() | lon_numeric.notna()).all()
    rows.append(create_validation_row("venues_lat_lon_numeric_if_present", "numeric or blank", bool(geo_ok), bool(geo_ok), "warning" if not geo_ok else "error"))

    report_df = pd.DataFrame(rows)
    valid = not (((report_df["severity"] == "error") & (~report_df["passed"])).any())
    return bool(valid), report_df



def validate_fixture_team_consistency(fixtures_df, teams_df) -> tuple[bool, pd.DataFrame]:
    """Validate fixture teams against official team list and group-stage appearance counts."""
    rows: list[dict[str, Any]] = []
    official_teams = set(teams_df["team"].map(standardize_team_name).tolist()) if teams_df is not None and not teams_df.empty else set()
    fixture_teams = set()
    for column in ["team_a", "team_b"]:
        if column in fixtures_df.columns:
            fixture_teams |= {standardize_team_name(value) for value in fixtures_df[column].fillna("").astype(str).tolist() if str(value).strip() and str(value).strip() != "TBD"}
    unknown = sorted(team for team in fixture_teams if team not in official_teams)
    rows.append(create_validation_row("fixture_teams_exist_in_official_teams", "all fixture teams in official teams", unknown if unknown else "ok", len(unknown) == 0))

    group_stage = fixtures_df[fixtures_df["stage"].fillna("").astype(str).map(is_group_stage_label)].copy() if "stage" in fixtures_df.columns else pd.DataFrame()
    if len(group_stage) == OFFICIAL_GROUP_STAGE_MATCHES:
        team_games = pd.concat([
            group_stage[["team_a"]].rename(columns={"team_a": "team"}),
            group_stage[["team_b"]].rename(columns={"team_b": "team"}),
        ], ignore_index=True)
        team_games["team"] = team_games["team"].map(standardize_team_name)
        counts = team_games.groupby("team").size().to_dict()
        bad_counts = {team: count for team, count in counts.items() if count != 3}
        rows.append(create_validation_row("group_stage_team_appearances_exactly_3", "3 if group stage complete", bad_counts if bad_counts else "ok", len(bad_counts) == 0))
    else:
        rows.append(create_validation_row("group_stage_team_appearances_exactly_3", "3 if group stage complete", f"group_stage_rows={len(group_stage)}", False, "warning"))

    report_df = pd.DataFrame(rows)
    valid = not (((report_df["severity"] == "error") & (~report_df["passed"])).any())
    return bool(valid), report_df



def validate_group_team_consistency(groups_df, teams_df) -> tuple[bool, pd.DataFrame]:
    """Validate official groups and teams files against each other."""
    rows: list[dict[str, Any]] = []
    if groups_df is not None and not groups_df.empty:
        groups_df = groups_df.copy()
        groups_df["team"] = groups_df["team"].fillna("").astype(str).map(standardize_team_name)
    if teams_df is not None and not teams_df.empty:
        teams_df = teams_df.copy()
        teams_df["team"] = teams_df["team"].fillna("").astype(str).map(standardize_team_name)

    group_teams = set(groups_df["team"].tolist()) if groups_df is not None and not groups_df.empty else set()
    team_teams = set(teams_df["team"].tolist()) if teams_df is not None and not teams_df.empty else set()
    rows.append(create_validation_row("groups_and_teams_same_team_set", sorted(team_teams), sorted(group_teams), group_teams == team_teams))

    merged = groups_df.merge(teams_df[["team", "group", "group_slot"]], on="team", how="left", suffixes=("_groups", "_teams"))
    consistent = (
        (merged["group_groups"].astype(str) == merged["group_teams"].astype(str)).all()
        and (pd.to_numeric(merged["slot"], errors="coerce") == pd.to_numeric(merged["group_slot"], errors="coerce")).all()
    )
    rows.append(create_validation_row("groups_team_slot_consistency", "group and slot align", bool(consistent), bool(consistent)))
    report_df = pd.DataFrame(rows)
    valid = not (((report_df["severity"] == "error") & (~report_df["passed"])).any())
    return bool(valid), report_df



def validate_official_fixtures(fixtures_df: pd.DataFrame, teams_df: pd.DataFrame | None = None, venues_df: pd.DataFrame | None = None, official_strict_full_schedule: bool = False) -> tuple[bool, pd.DataFrame]:
    """Validate official fixtures table and fixture-to-team/venue consistency."""
    rows: list[dict[str, Any]] = []
    required = get_official_contract("fixtures")
    ok, missing = check_required_columns(fixtures_df, required, "fixtures")
    rows.append(create_validation_row("fixtures_required_columns", required, missing if missing else "ok", ok))
    if not ok:
        report_df = pd.DataFrame(rows)
        return False, report_df

    total_rows = int(len(fixtures_df))
    if total_rows == OFFICIAL_TOTAL_MATCHES:
        rows.append(create_validation_row("fixtures_total_rows", OFFICIAL_TOTAL_MATCHES, total_rows, True))
    else:
        severity = "error" if official_strict_full_schedule else "warning"
        expected = f"{OFFICIAL_TOTAL_MATCHES} total matches (or partial group-stage template if pending verification)"
        rows.append(create_validation_row("fixtures_total_rows", expected, total_rows, False, severity))

    if "stage" in fixtures_df.columns:
        from src.official.stage_normalization import is_group_stage_label

        group_stage_rows = int(fixtures_df["stage"].fillna("").astype(str).map(is_group_stage_label).sum())
    else:
        group_stage_rows = 0
    if group_stage_rows == OFFICIAL_GROUP_STAGE_MATCHES:
        rows.append(create_validation_row("fixtures_group_stage_rows", OFFICIAL_GROUP_STAGE_MATCHES, group_stage_rows, True))
    else:
        rows.append(create_validation_row("fixtures_group_stage_rows", OFFICIAL_GROUP_STAGE_MATCHES, group_stage_rows, False, "warning"))

    unknown_teams = []
    if teams_df is not None and not teams_df.empty:
        official_teams = set(teams_df["team"].map(standardize_team_name).tolist())
        for column in ["team_a", "team_b"]:
            values = fixtures_df[column].fillna("").astype(str).tolist() if column in fixtures_df.columns else []
            for value in values:
                cleaned = standardize_team_name(value)
                if cleaned and cleaned not in {"TBD", "To Be Determined"} and cleaned not in official_teams:
                    unknown_teams.append(cleaned)
    rows.append(create_validation_row("fixtures_teams_in_official_list", "all non-TBD teams official", sorted(set(unknown_teams)) if unknown_teams else "ok", len(unknown_teams) == 0))

    no_self = bool((fixtures_df["team_a"].astype(str) != fixtures_df["team_b"].astype(str)).all())
    rows.append(create_validation_row("fixtures_no_team_plays_itself", True, no_self, no_self))
    rows.append(create_validation_row("fixtures_match_id_unique", int(len(fixtures_df)), int(fixtures_df["match_id"].nunique()), fixtures_df["match_id"].nunique() == len(fixtures_df)))
    rows.append(create_validation_row("fixtures_match_number_unique", int(len(fixtures_df)), int(fixtures_df["match_number"].nunique()), fixtures_df["match_number"].nunique() == len(fixtures_df)))

    dates = pd.to_datetime(fixtures_df["date"], errors="coerce")
    date_ok = dates.between(pd.Timestamp("2026-06-11"), pd.Timestamp("2026-07-19"), inclusive="both").all()
    rows.append(create_validation_row("fixtures_dates_in_world_cup_window", "2026-06-11 to 2026-07-19", f"min={dates.min()}, max={dates.max()}", bool(date_ok)))

    _, placeholder_df = validate_no_placeholder_values(fixtures_df, ["venue", "city", "country", "timezone"], "fixtures")
    rows.extend(placeholder_df.to_dict(orient="records"))

    if venues_df is not None and not venues_df.empty:
        official_venues = set(venues_df["venue"].fillna("").astype(str).tolist())
        unknown_venues = sorted(set(value for value in fixtures_df["venue"].fillna("").astype(str).tolist() if value and value not in official_venues))
        severity = "warning" if all(str(src) == "sample_to_be_verified" for src in _source_series(fixtures_df)) else "error"
        rows.append(create_validation_row("fixtures_venues_exist_in_official_venues", "all fixture venues in official venues", unknown_venues if unknown_venues else "ok", len(unknown_venues) == 0, severity if unknown_venues else "error"))

    report_df = pd.DataFrame(rows)
    valid = not (((report_df["severity"] == "error") & (~report_df["passed"])).any())
    return bool(valid), report_df



def validate_official_data_bundle(teams_df, groups_df, fixtures_df, venues_df, calendar_df, strict_full_schedule: bool = False) -> tuple[bool, pd.DataFrame]:
    """Run all official-data validations and combine into one report."""
    reports: list[pd.DataFrame] = []
    for validator, args in [
        (validate_official_teams, (teams_df,)),
        (validate_official_groups, (groups_df,)),
        (validate_official_venues, (venues_df,)),
        (validate_official_fixtures, (fixtures_df, teams_df, venues_df, strict_full_schedule)),
        (validate_group_team_consistency, (groups_df, teams_df)),
        (validate_fixture_team_consistency, (fixtures_df, teams_df)),
    ]:
        _, report = validator(*args)
        reports.append(report)

    required = get_official_contract("match_calendar")
    ok, missing = check_required_columns(calendar_df, required, "match_calendar")
    reports.append(pd.DataFrame([create_validation_row("match_calendar_required_columns", required, missing if missing else "ok", ok)]))

    combined = pd.concat(reports, ignore_index=True) if reports else pd.DataFrame(columns=["check", "expected", "actual", "passed", "severity"])
    bundle_valid = not (((combined["severity"] == "error") & (~combined["passed"])).any()) if not combined.empty else True
    return bool(bundle_valid), combined
