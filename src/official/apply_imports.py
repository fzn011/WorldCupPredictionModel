"""Apply manual import files to update official World Cup 2026 data.

This module provides functions to apply verified import files and update
the official data files, triggering re-validation and readiness checks.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C
from src.official.import_templates import validate_import_file
from src.official.prepare_official_data import prepare_step17a_official_worldcup_data
from src.official.prepare_squads import prepare_step17b_official_squads_and_priors
from src.utils.team_name_mapping import standardize_team_name


def _backup_file(file_path: Path, backup_dir: Path) -> Path:
    """Create a backup of a file before overwriting."""
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
    backup_path = backup_dir / backup_name
    if file_path.exists():
        shutil.copy2(file_path, backup_path)
    return backup_path


def _add_metadata_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add source and last_verified_at columns if missing."""
    if "source" not in df.columns:
        df["source"] = "manual_import"
    if "last_verified_at" not in df.columns:
        df["last_verified_at"] = datetime.now(timezone.utc).isoformat()
    return df


def apply_teams_import(
    import_file: Path | str,
    output_dir: Path | str | None = None,
    create_backup: bool = True,
) -> dict[str, Any]:
    """Apply a teams import file.

    Args:
        import_file: Path to the import CSV file.
        output_dir: Output directory. Defaults to OFFICIAL_PROCESSED_DIR.
        create_backup: Whether to create a backup of the existing file.

    Returns:
        Dictionary with import results.
    """
    if isinstance(import_file, str):
        import_file = Path(import_file)
    if output_dir is None:
        output_dir = C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    result = {"type": "teams", "success": False, "errors": [], "warnings": []}

    # Validate import file
    is_valid, errors = validate_import_file(import_file, "teams")
    if not is_valid:
        result["errors"] = errors
        return result

    # Read import data
    try:
        import_df = pd.read_csv(import_file)
    except Exception as e:
        result["errors"] = [f"Failed to read import file: {e}"]
        return result

    # Map import columns to official format
    target_columns = C.OFFICIAL_TEAMS_REQUIRED_COLUMNS.copy()
    teams_df = pd.DataFrame()

    # Map columns (some may have same names)
    column_mapping = {
        "team": "team",
        "team_code": "team_code",
        "confederation": "confederation",
        "group": "group",
        "group_slot": "group_slot",
        "is_host": "is_host",
        "qualified": "qualified",
        "source": "source",
    }

    for target_col, source_col in column_mapping.items():
        if source_col in import_df.columns:
            teams_df[target_col] = import_df[source_col]
        elif target_col in import_df.columns:
            teams_df[target_col] = import_df[target_col]
        else:
            teams_df[target_col] = ""

    # Add team_id if missing
    if "team_id" not in teams_df.columns:
        teams_df["team_id"] = [f"team_{i+1:03d}" for i in range(len(teams_df))]

    # Add metadata columns
    teams_df = _add_metadata_columns(teams_df)

    # Ensure only target columns
    teams_df = teams_df[target_columns]

    # Backup existing file
    target_file = output_dir / C.OFFICIAL_TEAMS_FILE
    if create_backup and target_file.exists():
        backup_dir = output_dir / "backups"
        _backup_file(target_file, backup_dir)

    # Save
    teams_df.to_csv(target_file, index=False)
    result["success"] = True
    result["rows_imported"] = len(teams_df)

    return result


def apply_groups_import(
    import_file: Path | str,
    output_dir: Path | str | None = None,
    create_backup: bool = True,
) -> dict[str, Any]:
    """Apply a groups import file.

    Args:
        import_file: Path to the import CSV file.
        output_dir: Output directory. Defaults to OFFICIAL_PROCESSED_DIR.
        create_backup: Whether to create a backup of the existing file.

    Returns:
        Dictionary with import results.
    """
    if isinstance(import_file, str):
        import_file = Path(import_file)
    if output_dir is None:
        output_dir = C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    result = {"type": "groups", "success": False, "errors": [], "warnings": []}

    # Validate import file
    is_valid, errors = validate_import_file(import_file, "groups")
    if not is_valid:
        result["errors"] = errors
        return result

    # Read import data
    try:
        import_df = pd.read_csv(import_file)
    except Exception as e:
        result["errors"] = [f"Failed to read import file: {e}"]
        return result

    # Map import columns to official format
    target_columns = C.OFFICIAL_GROUPS_REQUIRED_COLUMNS.copy()
    groups_df = pd.DataFrame()

    column_mapping = {
        "group": "group",
        "slot": "slot",
        "team": "team",
        "team_code": "team_code",
        "confederation": "confederation",
        "is_host": "is_host",
        "source": "source",
    }

    for target_col, source_col in column_mapping.items():
        if source_col in import_df.columns:
            groups_df[target_col] = import_df[source_col]
        elif target_col in import_df.columns:
            groups_df[target_col] = import_df[target_col]
        else:
            groups_df[target_col] = ""

    # Add metadata columns
    groups_df = _add_metadata_columns(groups_df)

    # Ensure only target columns
    groups_df = groups_df[target_columns]

    # Backup existing file
    target_file = output_dir / C.OFFICIAL_GROUPS_FILE
    if create_backup and target_file.exists():
        backup_dir = output_dir / "backups"
        _backup_file(target_file, backup_dir)

    # Save
    groups_df.to_csv(target_file, index=False)
    result["success"] = True
    result["rows_imported"] = len(groups_df)

    return result


def apply_fixtures_import(
    import_file: Path | str,
    output_dir: Path | str | None = None,
    create_backup: bool = True,
) -> dict[str, Any]:
    """Apply a fixtures import file.

    Args:
        import_file: Path to the import CSV file.
        output_dir: Output directory. Defaults to OFFICIAL_PROCESSED_DIR.
        create_backup: Whether to create a backup of the existing file.

    Returns:
        Dictionary with import results.
    """
    if isinstance(import_file, str):
        import_file = Path(import_file)
    if output_dir is None:
        output_dir = C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    result = {"type": "fixtures", "success": False, "errors": [], "warnings": []}

    # Validate import file
    is_valid, errors = validate_import_file(import_file, "fixtures")
    if not is_valid:
        result["errors"] = errors
        return result

    # Read import data
    try:
        import_df = pd.read_csv(import_file)
    except Exception as e:
        result["errors"] = [f"Failed to read import file: {e}"]
        return result

    # Map import columns to official format
    target_columns = C.OFFICIAL_FIXTURES_REQUIRED_COLUMNS.copy()
    fixtures_df = pd.DataFrame()

    column_mapping = {
        "match_id": "match_id",
        "match_number": "match_number",
        "stage": "stage",
        "group": "group",
        "date": "date",
        "kickoff_local": "kickoff_local",
        "kickoff_utc": "kickoff_utc",
        "timezone": "timezone",
        "venue": "venue",
        "stadium": "stadium",
        "city": "city",
        "country": "country",
        "team_a": "team_a",
        "team_b": "team_b",
        "team_a_code": "team_a_code",
        "team_b_code": "team_b_code",
        "team_a_group_slot": "team_a_group_slot",
        "team_b_group_slot": "team_b_group_slot",
        "status": "status",
        "source": "source",
    }

    for target_col, source_col in column_mapping.items():
        if source_col in import_df.columns:
            fixtures_df[target_col] = import_df[source_col]
        elif target_col in import_df.columns:
            fixtures_df[target_col] = import_df[target_col]
        else:
            fixtures_df[target_col] = ""

    # Add metadata columns
    fixtures_df = _add_metadata_columns(fixtures_df)

    # Ensure only target columns (some may be missing, fill with empty)
    for col in target_columns:
        if col not in fixtures_df.columns:
            fixtures_df[col] = ""
    fixtures_df = fixtures_df[target_columns]

    # Backup existing file
    target_file = output_dir / C.OFFICIAL_FIXTURES_FILE
    if create_backup and target_file.exists():
        backup_dir = output_dir / "backups"
        _backup_file(target_file, backup_dir)

    # Save
    fixtures_df.to_csv(target_file, index=False)
    result["success"] = True
    result["rows_imported"] = len(fixtures_df)

    return result


def apply_venues_import(
    import_file: Path | str,
    output_dir: Path | str | None = None,
    create_backup: bool = True,
) -> dict[str, Any]:
    """Apply a venues import file.

    Args:
        import_file: Path to the import CSV file.
        output_dir: Output directory. Defaults to OFFICIAL_PROCESSED_DIR.
        create_backup: Whether to create a backup of the existing file.

    Returns:
        Dictionary with import results.
    """
    if isinstance(import_file, str):
        import_file = Path(import_file)
    if output_dir is None:
        output_dir = C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    result = {"type": "venues", "success": False, "errors": [], "warnings": []}

    # Validate import file
    is_valid, errors = validate_import_file(import_file, "venues")
    if not is_valid:
        result["errors"] = errors
        return result

    # Read import data
    try:
        import_df = pd.read_csv(import_file)
    except Exception as e:
        result["errors"] = [f"Failed to read import file: {e}"]
        return result

    # Map import columns to official format
    target_columns = C.OFFICIAL_VENUES_REQUIRED_COLUMNS.copy()
    venues_df = pd.DataFrame()

    column_mapping = {
        "venue_id": "venue_id",
        "stadium": "stadium",
        "venue": "venue",
        "city": "city",
        "country": "country",
        "timezone": "timezone",
        "capacity": "capacity",
        "latitude": "latitude",
        "longitude": "longitude",
        "source": "source",
    }

    for target_col, source_col in column_mapping.items():
        if source_col in import_df.columns:
            venues_df[target_col] = import_df[source_col]
        elif target_col in import_df.columns:
            venues_df[target_col] = import_df[target_col]
        else:
            venues_df[target_col] = ""

    # Add metadata columns
    venues_df = _add_metadata_columns(venues_df)

    # Ensure only target columns
    venues_df = venues_df[target_columns]

    # Backup existing file
    target_file = output_dir / C.OFFICIAL_VENUES_FILE
    if create_backup and target_file.exists():
        backup_dir = output_dir / "backups"
        _backup_file(target_file, backup_dir)

    # Save
    venues_df.to_csv(target_file, index=False)
    result["success"] = True
    result["rows_imported"] = len(venues_df)

    return result


def apply_players_import(
    import_file: Path | str,
    output_dir: Path | str | None = None,
    create_backup: bool = True,
) -> dict[str, Any]:
    """Apply a players import file.

    Args:
        import_file: Path to the import CSV file.
        output_dir: Output directory. Defaults to OFFICIAL_PROCESSED_DIR.
        create_backup: Whether to create a backup of the existing file.

    Returns:
        Dictionary with import results.
    """
    if isinstance(import_file, str):
        import_file = Path(import_file)
    if output_dir is None:
        output_dir = C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    result = {"type": "players", "success": False, "errors": [], "warnings": []}

    # Validate import file
    is_valid, errors = validate_import_file(import_file, "players")
    if not is_valid:
        result["errors"] = errors
        return result

    # Read import data
    try:
        import_df = pd.read_csv(import_file)
    except Exception as e:
        result["errors"] = [f"Failed to read import file: {e}"]
        return result

    # Map import columns to official format
    target_columns = C.OFFICIAL_PLAYERS_REQUIRED_COLUMNS.copy()
    players_df = pd.DataFrame()

    column_mapping = {
        "player_id": "player_id",
        "team": "team",
        "team_code": "team_code",
        "shirt_number": "shirt_number",
        "position_code": "position_code",
        "position": "position",
        "player_name": "player_name",
        "first_names": "first_names",
        "last_names": "last_names",
        "name_on_shirt": "name_on_shirt",
        "date_of_birth": "date_of_birth",
        "age_at_tournament_start": "age_at_tournament_start",
        "club": "club",
        "club_country": "club_country",
        "height_cm": "height_cm",
        "source": "source",
    }

    for target_col, source_col in column_mapping.items():
        if source_col in import_df.columns:
            players_df[target_col] = import_df[source_col]
        elif target_col in import_df.columns:
            players_df[target_col] = import_df[target_col]
        else:
            players_df[target_col] = ""

    # Add metadata columns
    players_df = _add_metadata_columns(players_df)

    # Ensure only target columns
    players_df = players_df[target_columns]

    # Backup existing file
    target_file = output_dir / C.OFFICIAL_PLAYERS_FILE
    if create_backup and target_file.exists():
        backup_dir = output_dir / "backups"
        _backup_file(target_file, backup_dir)

    # Save
    players_df.to_csv(target_file, index=False)
    result["success"] = True
    result["rows_imported"] = len(players_df)

    return result


def apply_player_priors_import(
    import_file: Path | str,
    output_dir: Path | str | None = None,
    create_backup: bool = True,
) -> dict[str, Any]:
    """Apply a player priors import file to data/processed/player_award_priors.csv."""
    if isinstance(import_file, str):
        import_file = Path(import_file)
    if output_dir is None:
        output_dir = C.PROJECT_ROOT / C.PROCESSED_DATA_DIR
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    result = {"type": "player_priors", "success": False, "errors": [], "warnings": []}

    try:
        import_df = pd.read_csv(import_file)
    except Exception as e:
        result["errors"] = [f"Failed to read import file: {e}"]
        return result

    missing_cols = [c for c in C.IMPORT_PLAYER_PRIORS_REQUIRED_COLUMNS if c not in import_df.columns]
    if missing_cols:
        result["errors"] = [f"Missing required columns: {missing_cols}"]
        return result

    priors_df = import_df[C.IMPORT_PLAYER_PRIORS_REQUIRED_COLUMNS].copy()
    if "source" not in priors_df.columns or priors_df["source"].fillna("").eq("").all():
        priors_df = _add_metadata_columns(priors_df)

    target_file = output_dir / C.PLAYER_AWARD_PRIORS_FILE
    backup_path = ""
    if create_backup and target_file.exists():
        backup_dir = output_dir / "backups"
        backup_path = str(_backup_file(target_file, backup_dir))

    priors_df.to_csv(target_file, index=False)
    result["success"] = True
    result["rows_imported"] = len(priors_df)
    result["backup_path"] = backup_path
    return result


def append_import_audit(
    target: str,
    import_file: str,
    rows: int,
    overwritten: bool,
    status: str,
    backup_path: str = "",
) -> str:
    """Append a row to the population import audit log."""
    audit_path = (
        C.PROJECT_ROOT
        / C.OFFICIAL_POPULATION_REPORTS_DIR
        / C.OFFICIAL_POPULATION_IMPORT_AUDIT_FILE
    )
    audit_path.parent.mkdir(parents=True, exist_ok=True)

    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target": target,
        "import_file": import_file,
        "rows": rows,
        "overwritten": overwritten,
        "status": status,
        "backup_path": backup_path,
    }
    if audit_path.is_file():
        audit_df = pd.read_csv(audit_path)
        audit_df = pd.concat([audit_df, pd.DataFrame([row])], ignore_index=True)
    else:
        audit_df = pd.DataFrame([row])
    audit_df.to_csv(audit_path, index=False)
    return str(audit_path)


def apply_official_import_file(
    import_file: Path | str,
    template_type: str | None = None,
    output_dir: Path | str | None = None,
    create_backup: bool = True,
    re_prepare: bool = True,
) -> dict[str, Any]:
    """Apply an official import file based on its type.

    This is the main entry point for applying imports. It auto-detects the
    import type from the filename if not specified, applies the import,
    and optionally re-prepares the data.

    Args:
        import_file: Path to the import CSV file.
        template_type: Type of import (teams, groups, fixtures, venues, players).
            If None, will be inferred from filename.
        output_dir: Output directory. Defaults to OFFICIAL_PROCESSED_DIR.
        create_backup: Whether to create a backup before overwriting.
        re_prepare: Whether to re-run prepare scripts after import.

    Returns:
        Dictionary with import results.
    """
    if isinstance(import_file, str):
        import_file = Path(import_file)

    # Auto-detect type from filename if not specified
    if template_type is None:
        filename = import_file.stem.lower()
        if "team" in filename:
            template_type = "teams"
        elif "group" in filename:
            template_type = "groups"
        elif "fixture" in filename:
            template_type = "fixtures"
        elif "venue" in filename:
            template_type = "venues"
        elif "player" in filename and "prior" in filename:
            template_type = "player_priors"
        elif "player" in filename:
            template_type = "players"
        else:
            return {
                "success": False,
                "errors": [f"Cannot determine import type from filename: {import_file.name}"],
            }

    # Dispatch to appropriate handler
    handlers = {
        "teams": apply_teams_import,
        "groups": apply_groups_import,
        "fixtures": apply_fixtures_import,
        "venues": apply_venues_import,
        "players": apply_players_import,
        "player_priors": apply_player_priors_import,
    }

    if template_type not in handlers:
        return {
            "success": False,
            "errors": [f"Unknown import type: {template_type}"],
        }

    handler = handlers[template_type]
    result = handler(import_file, output_dir, create_backup)

    # Re-prepare data if requested and import was successful
    if result.get("success") and re_prepare:
        try:
            if template_type in ("teams", "groups", "fixtures", "venues"):
                prepare_step17a_official_worldcup_data()
            elif template_type == "players":
                prepare_step17b_official_squads_and_priors()
            elif template_type == "player_priors":
                prepare_step17b_official_squads_and_priors()
        except Exception as e:
            result["warnings"] = result.get("warnings", [])
            result["warnings"].append(f"Re-prepare failed: {e}")

    return result


def apply_all_imports(
    import_dir: Path | str | None = None,
    output_dir: Path | str | None = None,
    create_backup: bool = True,
    re_prepare: bool = True,
) -> dict[str, Any]:
    """Apply all import files in a directory.

    Args:
        import_dir: Directory containing import files. Defaults to OFFICIAL_PROCESSED_DIR.
        output_dir: Output directory. Defaults to OFFICIAL_PROCESSED_DIR.
        create_backup: Whether to create backups before overwriting.
        re_prepare: Whether to re-run prepare scripts after all imports.

    Returns:
        Dictionary with combined import results.
    """
    if import_dir is None:
        import_dir = C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR
    elif isinstance(import_dir, str):
        import_dir = Path(import_dir)

    if output_dir is None:
        output_dir = C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)

    results = {
        "imports": [],
        "total_success": 0,
        "total_failed": 0,
        "errors": [],
        "warnings": [],
    }

    # Find all import files
    import_files = list(import_dir.glob("import_*.csv"))

    for import_file in import_files:
        result = apply_official_import_file(
            import_file,
            output_dir=output_dir,
            create_backup=create_backup,
            re_prepare=False,  # Don't re-prepare until all imports are done
        )
        results["imports"].append(result)
        if result.get("success"):
            results["total_success"] += 1
        else:
            results["total_failed"] += 1
            results["errors"].extend(result.get("errors", []))
        results["warnings"].extend(result.get("warnings", []))

    # Re-prepare after all imports
    if re_prepare and results["total_success"] > 0:
        try:
            prepare_step17a_official_worldcup_data()
            prepare_step17b_official_squads_and_priors()
        except Exception as e:
            results["warnings"].append(f"Re-prepare failed: {e}")

    return results


def create_import_report(
    results: dict[str, Any],
    output_dir: Path | str | None = None,
) -> Path:
    """Create a report of import results.

    Args:
        results: Results from apply_official_import_file or apply_all_imports.
        output_dir: Output directory. Defaults to OFFICIAL_PROCESSED_DIR.

    Returns:
        Path to the report file.
    """
    if output_dir is None:
        output_dir = C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    report = {
        "import_timestamp": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }

    report_path = output_dir / C.OFFICIAL_IMPORT_RESULTS_FILE
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    return report_path