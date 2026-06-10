"""Population completeness scoring for Step 17F."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C

UNVERIFIED_SOURCES = {"sample_to_be_verified", "ai_prefilled_needs_verification"}


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


def _count_placeholders(df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    count = 0
    placeholders = (set(C.OFFICIAL_PLACEHOLDER_VALUES) | UNVERIFIED_SOURCES) - {""}
    for col in df.columns:
        if col in {"source", "notes", "verification_notes"}:
            continue
        series = df[col].fillna("").astype(str).str.strip()
        count += int(series.isin(placeholders).sum())
    if "source" in df.columns:
        count += int(df["source"].fillna("").astype(str).isin(UNVERIFIED_SOURCES).sum())
    return count


def _missing_required(df: pd.DataFrame, required: list[str]) -> int:
    if df.empty:
        return len(required)
    missing = 0
    for col in required:
        if col not in df.columns:
            missing += len(df) if len(df) else 1
            continue
        missing += int(df[col].fillna("").astype(str).str.strip().eq("").sum())
    return missing


def calculate_population_completeness() -> tuple[dict[str, Any], pd.DataFrame]:
    """Load populated files and compute completeness metrics."""
    teams = _read(C.POPULATED_OFFICIAL_TEAMS_FILE)
    groups = _read(C.POPULATED_OFFICIAL_GROUPS_FILE)
    fixtures = _read(C.POPULATED_OFFICIAL_FIXTURES_FILE)
    venues = _read(C.POPULATED_OFFICIAL_VENUES_FILE)
    players = _read(C.POPULATED_OFFICIAL_PLAYERS_FILE)

    group_stage = 0
    knockout = 0
    if not fixtures.empty and "stage" in fixtures.columns:
        stage_lower = fixtures["stage"].fillna("").astype(str).str.lower()
        group_stage = int(
            stage_lower.str.contains("group|first stage", na=False).sum()
        )
        knockout = int(
            stage_lower.str.contains(
                "knockout|round|quarter|semi|final|third|play-off", na=False
            ).sum()
        )

    teams_with_26 = 0
    if not players.empty and "team" in players.columns:
        per_team = players.groupby("team").size()
        teams_with_26 = int((per_team == C.OFFICIAL_REQUIRED_PLAYERS_PER_TEAM).sum())

    sample_count = 0
    for df in (teams, groups, fixtures, venues, players):
        if not df.empty and "source" in df.columns:
            sample_count += int(
                df["source"].fillna("").astype(str).str.lower().isin(
                    {s.lower() for s in UNVERIFIED_SOURCES}
                ).sum()
            )

    placeholder_issues = sum(_count_placeholders(df) for df in (teams, groups, fixtures, venues, players))
    missing_required = (
        _missing_required(teams, ["team", "team_code"])
        + _missing_required(fixtures, ["match_id", "team_a", "team_b", "date"])
        + _missing_required(players, ["player_name", "team", "date_of_birth"])
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
        "placeholder_issues_count": placeholder_issues,
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
            "notes": "72 group-stage matches",
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
            "category": "placeholder_issues",
            "target": 0,
            "actual": metrics.get("placeholder_issues_count", 0),
            "complete": metrics.get("placeholder_issues_count", 0) == 0,
            "blocking": metrics.get("placeholder_issues_count", 0) > 0,
            "notes": "No TBD/Unknown placeholders",
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
