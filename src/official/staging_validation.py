"""Validate staged official data before applying imports (Step 17E)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C
from src.official.import_templates import validate_import_file
from src.official.squad_validators import validate_official_players
from src.official.validators import (
    validate_official_fixtures,
    validate_official_groups,
    validate_official_teams,
    validate_official_venues,
)

STAGED_FILES: dict[str, str] = {
    "teams": C.STAGED_OFFICIAL_TEAMS_FILE,
    "groups": C.STAGED_OFFICIAL_GROUPS_FILE,
    "fixtures": C.STAGED_OFFICIAL_FIXTURES_FILE,
    "venues": C.STAGED_OFFICIAL_VENUES_FILE,
    "players": C.STAGED_OFFICIAL_PLAYERS_FILE,
    "player_priors": C.STAGED_PLAYER_AWARD_PRIORS_FILE,
}


def _staging_dir() -> Path:
    return C.PROJECT_ROOT / C.OFFICIAL_SOURCE_STAGING_DIR


def load_staged_data() -> dict[str, pd.DataFrame]:
    """Load any staged CSVs that exist."""
    data: dict[str, pd.DataFrame] = {}
    for key, filename in STAGED_FILES.items():
        path = _staging_dir() / filename
        if path.is_file():
            try:
                data[key] = pd.read_csv(path)
            except Exception:
                data[key] = pd.DataFrame()
    return data


def validate_staged_teams(teams_df: pd.DataFrame) -> tuple[bool, pd.DataFrame]:
    """Validate staged teams against import + official rules."""
    reports = []
    if teams_df.empty:
        reports.append({"check": "teams_present", "passed": False, "message": "No staged teams"})
        return False, pd.DataFrame(reports)

    tmp = _staging_dir() / "_validate_staged_teams.csv"
    teams_df.to_csv(tmp, index=False)
    ok_import, errs = validate_import_file(tmp, "teams")
    tmp.unlink(missing_ok=True)
    if not ok_import:
        for e in errs:
            reports.append({"check": "import_contract", "passed": False, "message": e})
        return False, pd.DataFrame(reports)

    official_df = teams_df.copy()
    if "team_id" not in official_df.columns:
        official_df["team_id"] = [f"team_{i+1:03d}" for i in range(len(official_df))]
    if "last_verified_at" not in official_df.columns:
        official_df["last_verified_at"] = ""
    passed, val_report = validate_official_teams(official_df)
    return passed, val_report


def validate_staged_fixtures(
    fixtures_df: pd.DataFrame,
    teams_df: pd.DataFrame | None = None,
    venues_df: pd.DataFrame | None = None,
) -> tuple[bool, pd.DataFrame]:
    """Validate staged fixtures."""
    if fixtures_df.empty:
        return False, pd.DataFrame([{"check": "fixtures_present", "passed": False}])

    tmp = _staging_dir() / "_validate_staged_fixtures.csv"
    fixtures_df.to_csv(tmp, index=False)
    ok_import, errs = validate_import_file(tmp, "fixtures")
    tmp.unlink(missing_ok=True)
    if not ok_import:
        return False, pd.DataFrame([{"check": "import_contract", "passed": False, "message": e} for e in errs])

    off_df = fixtures_df.copy()
    for col in C.OFFICIAL_FIXTURES_REQUIRED_COLUMNS:
        if col not in off_df.columns:
            off_df[col] = ""
    return validate_official_fixtures(off_df, teams_df=teams_df, venues_df=venues_df)


def validate_staged_players(
    players_df: pd.DataFrame,
    teams_df: pd.DataFrame | None = None,
    strict_squad_size: bool = False,
) -> tuple[bool, pd.DataFrame]:
    """Validate staged players."""
    if players_df.empty:
        return False, pd.DataFrame(
            [{"check": "players_present", "passed": False, "message": "No staged players (manual import may be required)"}]
        )

    tmp = _staging_dir() / "_validate_staged_players.csv"
    players_df.to_csv(tmp, index=False)
    ok_import, errs = validate_import_file(tmp, "players")
    tmp.unlink(missing_ok=True)
    if not ok_import:
        return False, pd.DataFrame([{"check": "import_contract", "passed": False, "message": e} for e in errs])

    off_df = players_df.copy()
    for col in C.OFFICIAL_PLAYERS_REQUIRED_COLUMNS:
        if col not in off_df.columns:
            off_df[col] = ""
    return validate_official_players(off_df, strict_squad_size=strict_squad_size)


def validate_all_staged_data(strict_final: bool = False) -> tuple[bool, pd.DataFrame]:
    """Run combined staged validation; returns (all_passed, report_df)."""
    staged = load_staged_data()
    teams_df = staged.get("teams", pd.DataFrame())
    groups_df = staged.get("groups", pd.DataFrame())
    fixtures_df = staged.get("fixtures", pd.DataFrame())
    venues_df = staged.get("venues", pd.DataFrame())
    players_df = staged.get("players", pd.DataFrame())

    report_parts: list[pd.DataFrame] = []
    overall = True

    if not teams_df.empty:
        ok, rep = validate_staged_teams(teams_df)
        rep["dataset"] = "teams"
        report_parts.append(rep)
        overall = overall and ok
    if not groups_df.empty:
        off_groups = groups_df.copy()
        if "slot" not in off_groups.columns and "group_slot" in off_groups.columns:
            off_groups["slot"] = off_groups["group_slot"]
        for col in C.OFFICIAL_GROUPS_REQUIRED_COLUMNS:
            if col not in off_groups.columns:
                off_groups[col] = ""
        ok, rep = validate_official_groups(off_groups)
        rep["dataset"] = "groups"
        report_parts.append(rep)
        overall = overall and ok
    if not venues_df.empty:
        off_ven = venues_df.copy()
        for col in C.OFFICIAL_VENUES_REQUIRED_COLUMNS:
            if col not in off_ven.columns:
                off_ven[col] = ""
        ok, rep = validate_official_venues(off_ven)
        rep["dataset"] = "venues"
        report_parts.append(rep)
        overall = overall and ok
    if not fixtures_df.empty:
        ok, rep = validate_staged_fixtures(fixtures_df, teams_df=teams_df, venues_df=venues_df)
        rep["dataset"] = "fixtures"
        report_parts.append(rep)
        overall = overall and ok
    if not players_df.empty:
        ok, rep = validate_staged_players(players_df, teams_df=teams_df, strict_squad_size=strict_final)
        rep["dataset"] = "players"
        report_parts.append(rep)
        overall = overall and ok

    if not report_parts:
        empty = pd.DataFrame(
            [{"dataset": "none", "check": "staged_data", "passed": False, "message": "No staged files found"}]
        )
        return False, empty

    report = pd.concat(report_parts, ignore_index=True)
    if strict_final:
        overall = overall and bool(report.get("passed", pd.Series(dtype=bool)).all())
    return overall, report


def save_staging_validation_report(report_df: pd.DataFrame, output_path: str | None = None) -> str:
    """Write staging validation report CSV."""
    path = Path(output_path) if output_path else C.PROJECT_ROOT / C.OFFICIAL_SOURCE_REPORTS_DIR / C.OFFICIAL_STAGING_VALIDATION_REPORT_FILE
    if not path.is_absolute():
        path = C.PROJECT_ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    report_df.to_csv(path, index=False)
    return str(path)
