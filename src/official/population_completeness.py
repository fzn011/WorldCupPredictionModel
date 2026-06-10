"""Population completeness scoring for Step 17F/17H."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C
from src.official.source_labels import is_sample_source_label
from src.official.stage_normalization import is_group_stage_label, is_knockout_stage_label

UNVERIFIED_SOURCES = {"sample_to_be_verified", "ai_prefilled_needs_verification"}

BLOCKING_PLACEHOLDER_COLUMNS: dict[str, list[str]] = {
    "teams": ["team", "group"],
    "groups": ["team", "group"],
    "fixtures": ["match_id", "stage", "date", "stadium", "city", "country", "kickoff_local"],
    "venues": ["stadium", "city", "country"],
    "players": ["player_name", "team", "position"],
}

OPTIONAL_WARNING_COLUMNS: dict[str, list[str]] = {
    "teams": ["team_code", "confederation", "is_host", "qualified"],
    "groups": ["team_code", "confederation"],
    "fixtures": ["kickoff_utc", "timezone", "team_a_code", "team_b_code", "venue"],
    "venues": ["capacity", "latitude", "longitude", "timezone", "venue_id"],
    "players": ["height", "club_country", "shirt_number", "date_of_birth", "verification_notes"],
}

PLACEHOLDER_TOKENS = (set(C.OFFICIAL_PLACEHOLDER_VALUES) | UNVERIFIED_SOURCES) - {""}


def _populated_dir() -> Path:
    return C.PROJECT_ROOT / C.OFFICIAL_POPULATED_DATA_DIR


def _reports_dir() -> Path:
    return C.PROJECT_ROOT / C.OFFICIAL_POPULATED_REPORTS_DIR


def _read(name: str) -> pd.DataFrame:
    path = _populated_dir() / name
    if path.is_file():
        try:
            return pd.read_csv(path)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


def _is_placeholder_value(value: str) -> bool:
    v = str(value).strip()
    return v in PLACEHOLDER_TOKENS or v.lower().startswith("tbd")


def _count_blocking_placeholders(df: pd.DataFrame, dataset_key: str) -> int:
    if df.empty:
        return 0
    cols = BLOCKING_PLACEHOLDER_COLUMNS.get(dataset_key, [])
    count = 0
    for col in cols:
        if col not in df.columns:
            count += len(df)
            continue
        series = df[col].fillna("").astype(str).str.strip()
        count += int(series.eq("").sum())
        count += int(series.map(_is_placeholder_value).sum())
    if dataset_key == "fixtures" and "stage" in df.columns:
        for idx, row in df.iterrows():
            stage = str(row.get("stage", ""))
            if is_group_stage_label(stage):
                for team_col in ("team_a", "team_b"):
                    if team_col not in df.columns:
                        count += 1
                        continue
                    val = str(row.get(team_col, "")).strip()
                    if not val or _is_placeholder_value(val):
                        count += 1
    if "source" in df.columns:
        count += int(df["source"].fillna("").astype(str).map(is_sample_source_label).sum())
    return count


def _count_optional_warnings(df: pd.DataFrame, dataset_key: str) -> int:
    if df.empty:
        return 0
    cols = OPTIONAL_WARNING_COLUMNS.get(dataset_key, [])
    count = 0
    for col in cols:
        if col not in df.columns:
            continue
        series = df[col].fillna("").astype(str).str.strip()
        count += int(series.eq("").sum())
        count += int(series.map(_is_placeholder_value).sum())
    return count


def _missing_blocking_required(df: pd.DataFrame, dataset_key: str) -> int:
    if df.empty:
        return len(BLOCKING_PLACEHOLDER_COLUMNS.get(dataset_key, []))
    missing = 0
    cols = BLOCKING_PLACEHOLDER_COLUMNS.get(dataset_key, [])
    for col in cols:
        if col not in df.columns:
            missing += len(df)
            continue
        missing += int(df[col].fillna("").astype(str).str.strip().eq("").sum())
    if dataset_key == "fixtures" and "stage" in df.columns:
        for _, row in df.iterrows():
            if is_group_stage_label(str(row.get("stage", ""))):
                for team_col in ("team_a", "team_b"):
                    if team_col not in df.columns or not str(row.get(team_col, "")).strip():
                        missing += 1
    return missing


def _fixture_stage_counts(fixtures: pd.DataFrame) -> tuple[int, int]:
    group_stage = 0
    knockout = 0
    if fixtures.empty or "stage" not in fixtures.columns:
        return group_stage, knockout
    original = (
        fixtures["original_stage"].fillna("").astype(str)
        if "original_stage" in fixtures.columns
        else pd.Series([""] * len(fixtures), index=fixtures.index)
    )
    for stage, orig in zip(fixtures["stage"].fillna("").astype(str), original, strict=False):
        if is_group_stage_label(stage) or is_group_stage_label(orig):
            group_stage += 1
        elif is_knockout_stage_label(stage) or is_knockout_stage_label(orig):
            knockout += 1
    return group_stage, knockout


def calculate_population_completeness() -> tuple[dict[str, Any], pd.DataFrame]:
    """Load populated files and compute completeness metrics."""
    teams = _read(C.POPULATED_OFFICIAL_TEAMS_FILE)
    groups = _read(C.POPULATED_OFFICIAL_GROUPS_FILE)
    fixtures = _read(C.POPULATED_OFFICIAL_FIXTURES_FILE)
    venues = _read(C.POPULATED_OFFICIAL_VENUES_FILE)
    players = _read(C.POPULATED_OFFICIAL_PLAYERS_FILE)

    group_stage, knockout = _fixture_stage_counts(fixtures)

    teams_with_26 = 0
    if not players.empty and "team" in players.columns:
        per_team = players.groupby("team").size()
        teams_with_26 = int((per_team == C.OFFICIAL_REQUIRED_PLAYERS_PER_TEAM).sum())

    sample_count = 0
    for df in (teams, groups, fixtures, venues, players):
        if not df.empty and "source" in df.columns:
            sample_count += int(df["source"].fillna("").astype(str).map(is_sample_source_label).sum())

    blocking_placeholders = (
        _count_blocking_placeholders(teams, "teams")
        + _count_blocking_placeholders(groups, "groups")
        + _count_blocking_placeholders(fixtures, "fixtures")
        + _count_blocking_placeholders(venues, "venues")
        + _count_blocking_placeholders(players, "players")
    )
    optional_warnings = (
        _count_optional_warnings(teams, "teams")
        + _count_optional_warnings(groups, "groups")
        + _count_optional_warnings(fixtures, "fixtures")
        + _count_optional_warnings(venues, "venues")
        + _count_optional_warnings(players, "players")
    )
    missing_required = (
        _missing_blocking_required(teams, "teams")
        + _missing_blocking_required(fixtures, "fixtures")
        + _missing_blocking_required(players, "players")
    )

    metrics: dict[str, Any] = {
        "teams_count": len(teams),
        "groups_count": groups["group"].nunique() if not groups.empty and "group" in groups.columns else 0,
        "group_rows_count": len(groups),
        "fixtures_count": len(fixtures),
        "group_stage_fixtures_count": group_stage,
        "knockout_fixtures_count": knockout,
        "venues_count": len(venues),
        "players_count": len(players),
        "teams_with_26_players": teams_with_26,
        "sample_to_be_verified_count": sample_count,
        "blocking_placeholder_count": blocking_placeholders,
        "optional_metadata_warning_count": optional_warnings,
        "placeholder_issues_count": blocking_placeholders,
        "missing_required_values_count": missing_required,
    }
    report_df = create_population_completeness_report(metrics)
    return metrics, report_df


def create_population_completeness_report(metrics: dict[str, Any]) -> pd.DataFrame:
    """Build category/target/actual/complete/blocking report rows."""
    targets = C.POPULATION_TARGET_COUNTS
    rows = [
        {
            "category": "teams",
            "target": targets["teams"],
            "actual": metrics.get("teams_count", 0),
            "complete": metrics.get("teams_count", 0) == targets["teams"],
            "blocking": metrics.get("teams_count", 0) != targets["teams"],
            "notes": "48 official teams required",
        },
        {
            "category": "groups",
            "target": targets["groups"],
            "actual": metrics.get("groups_count", 0),
            "complete": metrics.get("groups_count", 0) == targets["groups"],
            "blocking": metrics.get("groups_count", 0) != targets["groups"],
            "notes": "12 groups required",
        },
        {
            "category": "group_rows",
            "target": targets["group_rows"],
            "actual": metrics.get("group_rows_count", 0),
            "complete": metrics.get("group_rows_count", 0) == targets["group_rows"],
            "blocking": metrics.get("group_rows_count", 0) != targets["group_rows"],
            "notes": "4 teams per group",
        },
        {
            "category": "fixtures",
            "target": targets["fixtures"],
            "actual": metrics.get("fixtures_count", 0),
            "complete": metrics.get("fixtures_count", 0) == targets["fixtures"],
            "blocking": metrics.get("fixtures_count", 0) != targets["fixtures"],
            "notes": "104 official fixtures",
        },
        {
            "category": "group_stage_fixtures",
            "target": targets["group_stage_fixtures"],
            "actual": metrics.get("group_stage_fixtures_count", 0),
            "complete": metrics.get("group_stage_fixtures_count", 0) == targets["group_stage_fixtures"],
            "blocking": metrics.get("group_stage_fixtures_count", 0) != targets["group_stage_fixtures"],
            "notes": "72 group-stage matches (First Stage → group_stage)",
        },
        {
            "category": "knockout_fixtures",
            "target": targets["knockout_fixtures"],
            "actual": metrics.get("knockout_fixtures_count", 0),
            "complete": metrics.get("knockout_fixtures_count", 0) == targets["knockout_fixtures"],
            "blocking": metrics.get("knockout_fixtures_count", 0) != targets["knockout_fixtures"],
            "notes": "32 knockout/bracket matches",
        },
        {
            "category": "players",
            "target": targets["players"],
            "actual": metrics.get("players_count", 0),
            "complete": metrics.get("players_count", 0) == targets["players"],
            "blocking": metrics.get("players_count", 0) != targets["players"],
            "notes": "1,248 official players",
        },
        {
            "category": "teams_with_26_players",
            "target": targets["teams"],
            "actual": metrics.get("teams_with_26_players", 0),
            "complete": metrics.get("teams_with_26_players", 0) == targets["teams"],
            "blocking": metrics.get("teams_with_26_players", 0) != targets["teams"],
            "notes": "26 players per team",
        },
        {
            "category": "sample_to_be_verified",
            "target": 0,
            "actual": metrics.get("sample_to_be_verified_count", 0),
            "complete": metrics.get("sample_to_be_verified_count", 0) == 0,
            "blocking": metrics.get("sample_to_be_verified_count", 0) > 0,
            "notes": "No unverified source rows",
        },
        {
            "category": "blocking_placeholders",
            "target": 0,
            "actual": metrics.get("blocking_placeholder_count", 0),
            "complete": metrics.get("blocking_placeholder_count", 0) == 0,
            "blocking": metrics.get("blocking_placeholder_count", 0) > 0,
            "notes": "Required fields without TBD/empty/sample sources",
        },
        {
            "category": "optional_metadata_warnings",
            "target": 0,
            "actual": metrics.get("optional_metadata_warning_count", 0),
            "complete": True,
            "blocking": False,
            "notes": "Non-blocking gaps (capacity, lat/long, height, etc.)",
        },
        {
            "category": "missing_required_values",
            "target": 0,
            "actual": metrics.get("missing_required_values_count", 0),
            "complete": metrics.get("missing_required_values_count", 0) == 0,
            "blocking": metrics.get("missing_required_values_count", 0) > 0,
            "notes": "Required fields filled",
        },
    ]
    return pd.DataFrame(rows)


def save_population_completeness_report(
    report_df: pd.DataFrame,
    output_path: str | None = None,
) -> str:
    """Save completeness report CSV."""
    _reports_dir().mkdir(parents=True, exist_ok=True)
    path = Path(output_path) if output_path else _reports_dir() / C.OFFICIAL_POPULATION_COMPLETENESS_REPORT_FILE
    if not path.is_absolute():
        path = C.PROJECT_ROOT / path
    report_df.to_csv(path, index=False)
    return str(path)


def population_is_ready_for_apply(metrics: dict[str, Any]) -> bool:
    """True only when all blocking completeness metrics pass."""
    if not metrics:
        metrics, _ = calculate_population_completeness()
    report_df = create_population_completeness_report(metrics)
    blocking = report_df[report_df["blocking"] == True]  # noqa: E712
    return blocking.empty
