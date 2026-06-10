"""Preparation orchestrator for Step 17A official World Cup 2026 data lock."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.official.loaders import (
    load_official_fixtures,
    load_official_groups,
    load_official_match_calendar,
    load_official_teams,
    load_official_venues,
    load_source_manifest,
    official_path,
)
from src.official.validators import validate_official_data_bundle
from src.utils.team_name_mapping import slugify_team_name, standardize_team_name
import src.utils.constants as C

PROJECT_ROOT = getattr(C, "PROJECT_ROOT", Path(__file__).resolve().parents[2])
OFFICIAL_DATA_DIR = PROJECT_ROOT / str(getattr(C, "OFFICIAL_DATA_DIR", "data/official"))
OFFICIAL_RAW_DIR = PROJECT_ROOT / str(getattr(C, "OFFICIAL_RAW_DIR", "data/official/raw"))
OFFICIAL_PROCESSED_DIR = PROJECT_ROOT / str(getattr(C, "OFFICIAL_PROCESSED_DIR", "data/official/processed"))
OFFICIAL_REPORTS_DIR = PROJECT_ROOT / str(getattr(C, "OFFICIAL_REPORTS_DIR", "data/official/reports"))
PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", PROJECT_ROOT / "data" / "processed")
SAMPLE_DATA_DIR = getattr(C, "SAMPLE_DATA_DIR", PROJECT_ROOT / "data" / "sample")

TOURNAMENT_GROUPS_FILE = getattr(C, "TOURNAMENT_GROUPS_FILE", "tournament_groups.csv")
TOURNAMENT_FIXTURES_FILE = getattr(C, "TOURNAMENT_FIXTURES_FILE", "tournament_fixtures.csv")
OFFICIAL_TEAMS_FILE = getattr(C, "OFFICIAL_TEAMS_FILE", "official_teams.csv")
OFFICIAL_GROUPS_FILE = getattr(C, "OFFICIAL_GROUPS_FILE", "official_groups.csv")
OFFICIAL_FIXTURES_FILE = getattr(C, "OFFICIAL_FIXTURES_FILE", "official_fixtures.csv")
OFFICIAL_VENUES_FILE = getattr(C, "OFFICIAL_VENUES_FILE", "official_venues.csv")
OFFICIAL_MATCH_CALENDAR_FILE = getattr(C, "OFFICIAL_MATCH_CALENDAR_FILE", "official_match_calendar.csv")
OFFICIAL_DATA_SUMMARY_FILE = getattr(C, "OFFICIAL_DATA_SUMMARY_FILE", "official_data_summary.json")
OFFICIAL_DATA_VALIDATION_REPORT_FILE = getattr(C, "OFFICIAL_DATA_VALIDATION_REPORT_FILE", "official_data_validation_report.csv")
OFFICIAL_SOURCE_MANIFEST_FILE = getattr(C, "OFFICIAL_SOURCE_MANIFEST_FILE", "source_manifest.json")
DATA_MODE_OFFICIAL = getattr(C, "DATA_MODE_OFFICIAL", "official")
DATA_MODE_SAMPLE = getattr(C, "DATA_MODE_SAMPLE", "sample")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()



def _ensure_directories() -> None:
    for path in [OFFICIAL_DATA_DIR, OFFICIAL_RAW_DIR, OFFICIAL_PROCESSED_DIR, OFFICIAL_REPORTS_DIR]:
        path.mkdir(parents=True, exist_ok=True)



def _load_group_seed() -> pd.DataFrame:
    processed_path = PROCESSED_DATA_DIR / TOURNAMENT_GROUPS_FILE
    sample_path = SAMPLE_DATA_DIR / "sample_tournament_groups.csv"
    path = processed_path if processed_path.is_file() else sample_path
    if not path.is_file():
        raise FileNotFoundError(f"Tournament groups source file not found: {path}")
    df = pd.read_csv(path)
    df["team"] = df["team"].map(standardize_team_name)
    return df



def _load_fixture_seed() -> pd.DataFrame:
    processed_path = PROCESSED_DATA_DIR / TOURNAMENT_FIXTURES_FILE
    sample_path = SAMPLE_DATA_DIR / "sample_tournament_schedule.csv"
    path = processed_path if processed_path.is_file() else sample_path
    if not path.is_file():
        raise FileNotFoundError(f"Tournament fixtures source file not found: {path}")
    df = pd.read_csv(path)
    for column in ["team_a", "team_b"]:
        if column in df.columns:
            df[column] = df[column].map(standardize_team_name)
    return df



def _generate_team_code(team: str, used: set[str]) -> str:
    tokens = [token for token in slugify_team_name(team).upper().split("-") if token]
    if len(tokens) >= 3:
        base = "".join(token[0] for token in tokens[:3])
    elif len(tokens) == 2:
        second = tokens[1][1] if len(tokens[1]) > 1 else tokens[1][0]
        base = f"{tokens[0][0]}{tokens[1][0]}{second}"
    else:
        merged = "".join(tokens) if tokens else "TEAM"
        base = (merged + "XXX")[:3]
    code = base[:3]
    counter = 1
    while code in used:
        suffix = str(counter)
        code = f"{base[:max(0, 3 - len(suffix))]}{suffix}"[:3]
        counter += 1
    used.add(code)
    return code



def _create_official_groups_template(groups_seed: pd.DataFrame) -> pd.DataFrame:
    used_codes: set[str] = set()
    rows: list[dict[str, Any]] = []
    for _, row in groups_seed.iterrows():
        team = standardize_team_name(row.get("team", ""))
        rows.append(
            {
                "group": str(row.get("group", "")).strip().upper(),
                "slot": int(pd.to_numeric(row.get("slot"), errors="coerce")),
                "team": team,
                "team_code": _generate_team_code(team, used_codes),
                "confederation": row.get("confederation", ""),
                "is_host": int(pd.to_numeric(row.get("is_host", 0), errors="coerce") or 0),
                "source": "sample_to_be_verified",
                "last_verified_at": "MANUALLY_UPDATE_DATE",
            }
        )
    return pd.DataFrame(rows)



def _create_official_teams_template(groups_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, row in groups_df.iterrows():
        team = standardize_team_name(row["team"])
        rows.append(
            {
                "team_id": slugify_team_name(team),
                "team": team,
                "team_code": row["team_code"],
                "confederation": row.get("confederation", ""),
                "group": row["group"],
                "group_slot": row["slot"],
                "is_host": int(pd.to_numeric(row.get("is_host", 0), errors="coerce") or 0),
                "qualified": 1,
                "source": "sample_to_be_verified",
                "last_verified_at": "MANUALLY_UPDATE_DATE",
            }
        )
    return pd.DataFrame(rows)



def _create_official_fixtures_template(fixtures_seed: pd.DataFrame, teams_df: pd.DataFrame) -> pd.DataFrame:
    team_code_map = dict(zip(teams_df["team"], teams_df["team_code"]))
    group_slot_map = dict(zip(teams_df["team"], teams_df["group_slot"]))
    rows: list[dict[str, Any]] = []
    for idx, row in fixtures_seed.reset_index(drop=True).iterrows():
        team_a = standardize_team_name(row.get("team_a", ""))
        team_b = standardize_team_name(row.get("team_b", ""))
        venue = str(row.get("venue", "TBD")).strip()
        city = str(row.get("city", "TBD")).strip()
        country = str(row.get("country", "TBD")).strip()
        stage = str(row.get("stage", "")).strip()
        rows.append(
            {
                "match_id": row.get("match_id", f"M-{idx + 1:03d}"),
                "match_number": idx + 1,
                "stage": stage,
                "group": row.get("group", ""),
                "date": row.get("date", ""),
                "kickoff_local": "TBD",
                "kickoff_utc": "TBD",
                "timezone": "TBD",
                "venue": venue,
                "stadium": venue,
                "city": city,
                "country": country,
                "team_a": team_a,
                "team_b": team_b,
                "team_a_code": team_code_map.get(team_a, ""),
                "team_b_code": team_code_map.get(team_b, ""),
                "team_a_group_slot": group_slot_map.get(team_a, row.get("team_a_slot", "")),
                "team_b_group_slot": group_slot_map.get(team_b, row.get("team_b_slot", "")),
                "status": "scheduled",
                "source": "sample_to_be_verified",
                "last_verified_at": "MANUALLY_UPDATE_DATE",
            }
        )
    return pd.DataFrame(rows)



def _create_official_venues_template(fixtures_df: pd.DataFrame) -> pd.DataFrame:
    if fixtures_df.empty:
        return pd.DataFrame(columns=["venue_id", "stadium", "venue", "city", "country", "timezone", "capacity", "latitude", "longitude", "source", "last_verified_at"])
    venue_df = fixtures_df[["venue", "stadium", "city", "country", "timezone", "source", "last_verified_at"]].drop_duplicates().copy()
    venue_df.insert(0, "venue_id", venue_df["venue"].astype(str).map(slugify_team_name))
    venue_df["capacity"] = pd.NA
    venue_df["latitude"] = pd.NA
    venue_df["longitude"] = pd.NA
    return venue_df[["venue_id", "stadium", "venue", "city", "country", "timezone", "capacity", "latitude", "longitude", "source", "last_verified_at"]]



def _create_match_calendar(fixtures_df: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "match_id",
        "match_number",
        "stage",
        "group",
        "date",
        "kickoff_local",
        "kickoff_utc",
        "timezone",
        "venue",
        "city",
        "country",
        "team_a",
        "team_b",
        "status",
        "source",
        "last_verified_at",
    ]
    calendar_df = fixtures_df[columns].copy() if not fixtures_df.empty else pd.DataFrame(columns=columns)
    return calendar_df



def _save_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)



def _ensure_manifest(data_mode: str) -> None:
    manifest_path = official_path(OFFICIAL_SOURCE_MANIFEST_FILE)
    if manifest_path.is_file():
        payload = load_source_manifest()
    else:
        payload = {
            "official_mode": data_mode == DATA_MODE_OFFICIAL,
            "teams_source": "FIFA World Cup 2026 Teams page",
            "fixtures_source": "FIFA World Cup 2026 Match Schedule page",
            "venues_source": "FIFA World Cup 2026 Match Schedule/Stadiums page",
            "groups_source": "FIFA World Cup 2026 Groups/Schedule data",
            "squads_source": "To be added in Step 17B from FIFA Squad Lists PDF",
            "last_verified_at": "MANUALLY_UPDATE_DATE",
            "notes": [
                "Official data should be refreshed if FIFA updates teams, fixtures, venues, kickoff times, or squads.",
                "This manifest records source intent; users should verify final data against FIFA before final use.",
            ],
        }
    payload["official_mode"] = data_mode == DATA_MODE_OFFICIAL
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)



def prepare_step17a_official_worldcup_data(data_mode: str = DATA_MODE_OFFICIAL, strict_full_schedule: bool = False) -> dict[str, Any]:
    """Prepare official-style World Cup 2026 data bundle and validate it honestly."""
    _ensure_directories()
    _ensure_manifest(data_mode=data_mode)

    groups_path = official_path(OFFICIAL_GROUPS_FILE)
    teams_path = official_path(OFFICIAL_TEAMS_FILE)
    fixtures_path = official_path(OFFICIAL_FIXTURES_FILE)
    venues_path = official_path(OFFICIAL_VENUES_FILE)
    calendar_path = official_path(OFFICIAL_MATCH_CALENDAR_FILE)

    if not groups_path.is_file():
        groups_seed = _load_group_seed()
        official_groups_df = _create_official_groups_template(groups_seed)
        _save_csv(official_groups_df, groups_path)
    official_groups_df = load_official_groups()

    if not teams_path.is_file():
        official_teams_df = _create_official_teams_template(official_groups_df)
        _save_csv(official_teams_df, teams_path)
    official_teams_df = load_official_teams()

    if not fixtures_path.is_file():
        fixtures_seed = _load_fixture_seed()
        official_fixtures_df = _create_official_fixtures_template(fixtures_seed, official_teams_df)
        _save_csv(official_fixtures_df, fixtures_path)
    official_fixtures_df = load_official_fixtures()

    if not venues_path.is_file():
        official_venues_df = _create_official_venues_template(official_fixtures_df)
        _save_csv(official_venues_df, venues_path)
    official_venues_df = load_official_venues()

    official_calendar_df = _create_match_calendar(official_fixtures_df)
    _save_csv(official_calendar_df, calendar_path)
    official_calendar_df = load_official_match_calendar()

    validation_passed, validation_report_df = validate_official_data_bundle(
        official_teams_df,
        official_groups_df,
        official_fixtures_df,
        official_venues_df,
        official_calendar_df,
        strict_full_schedule=strict_full_schedule,
    )

    failed_df = validation_report_df[validation_report_df["passed"] == False].copy() if not validation_report_df.empty else pd.DataFrame()
    errors_count = int((failed_df["severity"] == "error").sum()) if not failed_df.empty else 0
    warnings_count = int((failed_df["severity"] == "warning").sum()) if not failed_df.empty else 0
    sample_to_be_verified_present = False
    for df in [official_teams_df, official_groups_df, official_fixtures_df, official_venues_df]:
        if not df.empty and "source" in df.columns and df["source"].astype(str).eq("sample_to_be_verified").any():
            sample_to_be_verified_present = True
            break

    if errors_count > 0:
        status = "error"
    elif sample_to_be_verified_present or warnings_count > 0:
        status = "needs_verification"
    else:
        status = "ok"

    group_stage_matches = int((official_fixtures_df["stage"].astype(str) == "group_stage").sum()) if not official_fixtures_df.empty else 0
    knockout_matches = int(len(official_fixtures_df) - group_stage_matches) if not official_fixtures_df.empty else 0
    notes = []
    if sample_to_be_verified_present:
        notes.append("Official-style template data still contains sample_to_be_verified rows and must be manually checked against FIFA.")
    if warnings_count > 0:
        notes.append("Validation warnings remain; inspect the validation report before treating data as fully verified.")
    if not notes:
        notes.append("Official data bundle validated with no warnings.")

    summary = {
        "status": status,
        "data_mode": data_mode,
        "strict_full_schedule": bool(strict_full_schedule),
        "teams_count": int(len(official_teams_df)),
        "groups_count": int(official_groups_df["group"].nunique()) if not official_groups_df.empty else 0,
        "fixtures_count": int(len(official_fixtures_df)),
        "venues_count": int(len(official_venues_df)),
        "group_stage_matches": group_stage_matches,
        "knockout_matches": knockout_matches,
        "validation_passed": bool(validation_passed),
        "errors_count": errors_count,
        "warnings_count": warnings_count,
        "last_verified_at": _now_iso(),
        "notes": notes,
    }

    summary_path = official_path(OFFICIAL_DATA_SUMMARY_FILE)
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    validation_report_path = official_path(OFFICIAL_DATA_VALIDATION_REPORT_FILE)
    _save_csv(validation_report_df, validation_report_path)

    return {
        "status": status,
        "validation_passed": bool(validation_passed),
        "teams_count": int(len(official_teams_df)),
        "groups_count": int(official_groups_df["group"].nunique()) if not official_groups_df.empty else 0,
        "fixtures_count": int(len(official_fixtures_df)),
        "venues_count": int(len(official_venues_df)),
        "errors_count": errors_count,
        "warnings_count": warnings_count,
        "official_teams_path": str(teams_path),
        "official_groups_path": str(groups_path),
        "official_fixtures_path": str(fixtures_path),
        "official_venues_path": str(venues_path),
        "official_summary_path": str(summary_path),
        "validation_report_path": str(validation_report_path),
    }
