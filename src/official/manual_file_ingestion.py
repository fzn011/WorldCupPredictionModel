"""Manual CSV/XLSX ingestion into Step 17E staging area."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C
from src.official.master_workbook import _sheet_columns

TARGET_TO_STAGED: dict[str, str] = {
    "teams": C.STAGED_OFFICIAL_TEAMS_FILE,
    "groups": C.STAGED_OFFICIAL_GROUPS_FILE,
    "fixtures": C.STAGED_OFFICIAL_FIXTURES_FILE,
    "venues": C.STAGED_OFFICIAL_VENUES_FILE,
    "players": C.STAGED_OFFICIAL_PLAYERS_FILE,
    "player_priors": C.STAGED_PLAYER_AWARD_PRIORS_FILE,
}

TARGET_TO_TEMPLATE_TYPE: dict[str, str] = {
    "teams": "teams",
    "groups": "groups",
    "fixtures": "fixtures",
    "venues": "venues",
    "players": "players",
    "player_priors": "player_priors",
}

_COLUMN_MAP: dict[str, list[str]] = {
    "teams": C.IMPORT_TEAMS_REQUIRED_COLUMNS,
    "groups": C.IMPORT_GROUPS_REQUIRED_COLUMNS,
    "fixtures": C.IMPORT_FIXTURES_REQUIRED_COLUMNS,
    "venues": C.IMPORT_VENUES_REQUIRED_COLUMNS,
    "players": C.IMPORT_PLAYERS_REQUIRED_COLUMNS,
    "player_priors": C.IMPORT_PLAYER_PRIORS_REQUIRED_COLUMNS,
}


def _validate_staging_columns(df: pd.DataFrame, template_type: str) -> tuple[bool, list[str]]:
    """Validate required columns only (partial row counts allowed in staging)."""
    required = _COLUMN_MAP.get(template_type)
    if required is None:
        return False, [f"Unknown template type: {template_type}"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        return False, [f"Missing required columns: {missing}"]
    return True, []


def _staging_dir() -> Path:
    p = C.PROJECT_ROOT / C.OFFICIAL_SOURCE_STAGING_DIR
    p.mkdir(parents=True, exist_ok=True)
    return p


def _read_table(file_path: Path) -> pd.DataFrame:
    suffix = file_path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(file_path)
    return pd.read_csv(file_path)


def ingest_manual_official_file(file_path: str, target_name: str) -> dict[str, Any]:
    """Ingest user CSV/XLSX into staging with contract validation."""
    path = Path(file_path)
    if target_name not in TARGET_TO_STAGED:
        return {
            "success": False,
            "errors": [f"Invalid target_name: {target_name}"],
            "staged_path": "",
        }

    if not path.is_file():
        return {"success": False, "errors": [f"File not found: {file_path}"], "staged_path": ""}

    try:
        df = _read_table(path)
    except Exception as exc:
        return {"success": False, "errors": [f"Failed to read file: {exc}"], "staged_path": ""}

    template_type = TARGET_TO_TEMPLATE_TYPE[target_name]
    is_valid, errors = _validate_staging_columns(df, template_type)

    if not is_valid:
        return {"success": False, "errors": errors, "staged_path": ""}

    staged_path = _staging_dir() / TARGET_TO_STAGED[target_name]
    df.to_csv(staged_path, index=False)
    return {
        "success": True,
        "errors": [],
        "target": target_name,
        "rows": len(df),
        "staged_path": str(staged_path),
        "source_file": str(path),
    }


def ingest_master_workbook(workbook_path: str) -> dict[str, Any]:
    """Read master workbook sheets into staged CSVs."""
    path = Path(workbook_path)
    if not path.is_file():
        return {"success": False, "errors": [f"Workbook not found: {workbook_path}"], "sheets": {}}

    sheet_map = {
        "Teams": "teams",
        "Groups": "groups",
        "Fixtures": "fixtures",
        "Venues": "venues",
        "Players": "players",
        "Player_Priors": "player_priors",
    }

    results: dict[str, Any] = {"success": True, "errors": [], "sheets": {}}
    try:
        xls = pd.ExcelFile(path)
    except Exception as exc:
        return {"success": False, "errors": [f"Failed to open workbook: {exc}"], "sheets": {}}

    for sheet_name, target in sheet_map.items():
        if sheet_name not in xls.sheet_names:
            continue
        df = pd.read_excel(xls, sheet_name=sheet_name)
        df = df.dropna(how="all")
        if df.empty:
            results["sheets"][sheet_name] = {"skipped": True, "reason": "empty sheet"}
            continue
        tmp = _staging_dir() / f"_wb_{target}.csv"
        df.to_csv(tmp, index=False)
        ingested = ingest_manual_official_file(str(tmp), target)
        tmp.unlink(missing_ok=True)
        results["sheets"][sheet_name] = ingested
        if not ingested.get("success"):
            results["success"] = False
            results["errors"].extend(ingested.get("errors", []))

    return results
