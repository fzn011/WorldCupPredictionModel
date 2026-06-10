"""Generate manual import templates for official World Cup 2026 data.

This module provides functions to generate CSV templates that can be used
to manually import verified official data from FIFA sources.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C
from src.utils.team_name_mapping import standardize_team_name


def _create_empty_dataframe(columns: list[str]) -> pd.DataFrame:
    """Create an empty DataFrame with the specified columns."""
    return pd.DataFrame(columns=columns)


def generate_teams_import_template(
    output_dir: Path | str | None = None,
    existing_teams_df: pd.DataFrame | None = None,
) -> Path:
    """Generate import template for teams data.

    Args:
        output_dir: Output directory. Defaults to OFFICIAL_PROCESSED_DIR.
        existing_teams_df: Optional existing teams DataFrame to pre-populate.

    Returns:
        Path to the generated template file.
    """
    if output_dir is None:
        output_dir = C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    columns = C.IMPORT_TEAMS_REQUIRED_COLUMNS.copy()

    if existing_teams_df is not None and not existing_teams_df.empty:
        # Extract relevant columns from existing data
        template_df = pd.DataFrame()
        for col in columns:
            src_col = col
            if src_col in existing_teams_df.columns:
                template_df[col] = existing_teams_df[src_col]
            else:
                template_df[col] = ""
    else:
        # Create empty template with 48 rows for all teams
        template_df = pd.DataFrame(columns=columns)
        # Pre-fill with empty rows
        for _ in range(C.OFFICIAL_REQUIRED_TEAM_COUNT):
            template_df.loc[len(template_df)] = {col: "" for col in columns}

    output_path = output_dir / C.OFFICIAL_IMPORT_TEAMS_TEMPLATE_FILE
    template_df.to_csv(output_path, index=False)
    return output_path


def generate_groups_import_template(
    output_dir: Path | str | None = None,
    existing_groups_df: pd.DataFrame | None = None,
) -> Path:
    """Generate import template for groups data.

    Args:
        output_dir: Output directory. Defaults to OFFICIAL_PROCESSED_DIR.
        existing_groups_df: Optional existing groups DataFrame to pre-populate.

    Returns:
        Path to the generated template file.
    """
    if output_dir is None:
        output_dir = C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    columns = C.IMPORT_GROUPS_REQUIRED_COLUMNS.copy()

    if existing_groups_df is not None and not existing_groups_df.empty:
        template_df = pd.DataFrame()
        for col in columns:
            if col in existing_groups_df.columns:
                template_df[col] = existing_groups_df[col]
            else:
                template_df[col] = ""
    else:
        # Create empty template with 48 rows (12 groups x 4 teams)
        template_df = pd.DataFrame(columns=columns)
        for _ in range(C.OFFICIAL_REQUIRED_TEAM_COUNT):
            template_df.loc[len(template_df)] = {col: "" for col in columns}

    output_path = output_dir / C.OFFICIAL_IMPORT_GROUPS_TEMPLATE_FILE
    template_df.to_csv(output_path, index=False)
    return output_path


def generate_fixtures_import_template(
    output_dir: Path | str | None = None,
    existing_fixtures_df: pd.DataFrame | None = None,
) -> Path:
    """Generate import template for fixtures data.

    Args:
        output_dir: Output directory. Defaults to OFFICIAL_PROCESSED_DIR.
        existing_fixtures_df: Optional existing fixtures DataFrame to pre-populate.

    Returns:
        Path to the generated template file.
    """
    if output_dir is None:
        output_dir = C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    columns = C.IMPORT_FIXTURES_REQUIRED_COLUMNS.copy()

    if existing_fixtures_df is not None and not existing_fixtures_df.empty:
        template_df = pd.DataFrame()
        for col in columns:
            if col in existing_fixtures_df.columns:
                template_df[col] = existing_fixtures_df[col]
            else:
                template_df[col] = ""
    else:
        # Create empty template with 104 rows for all matches
        template_df = pd.DataFrame(columns=columns)
        for _ in range(C.OFFICIAL_TOTAL_MATCHES):
            template_df.loc[len(template_df)] = {col: "" for col in columns}

    output_path = output_dir / C.OFFICIAL_IMPORT_FIXTURES_TEMPLATE_FILE
    template_df.to_csv(output_path, index=False)
    return output_path


def generate_venues_import_template(
    output_dir: Path | str | None = None,
    existing_venues_df: pd.DataFrame | None = None,
) -> Path:
    """Generate import template for venues data.

    Args:
        output_dir: Output directory. Defaults to OFFICIAL_PROCESSED_DIR.
        existing_venues_df: Optional existing venues DataFrame to pre-populate.

    Returns:
        Path to the generated template file.
    """
    if output_dir is None:
        output_dir = C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    columns = C.IMPORT_VENUES_REQUIRED_COLUMNS.copy()

    if existing_venues_df is not None and not existing_venues_df.empty:
        template_df = pd.DataFrame()
        for col in columns:
            if col in existing_venues_df.columns:
                template_df[col] = existing_venues_df[col]
            else:
                template_df[col] = ""
    else:
        # Create empty template with 16 rows for all venues
        template_df = pd.DataFrame(columns=columns)
        for _ in range(16):  # 16 venues for World Cup 2026
            template_df.loc[len(template_df)] = {col: "" for col in columns}

    output_path = output_dir / C.OFFICIAL_IMPORT_VENUES_TEMPLATE_FILE
    template_df.to_csv(output_path, index=False)
    return output_path


def generate_players_import_template(
    output_dir: Path | str | None = None,
    existing_players_df: pd.DataFrame | None = None,
) -> Path:
    """Generate import template for players data.

    Args:
        output_dir: Output directory. Defaults to OFFICIAL_PROCESSED_DIR.
        existing_players_df: Optional existing players DataFrame to pre-populate.

    Returns:
        Path to the generated template file.
    """
    if output_dir is None:
        output_dir = C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    columns = C.IMPORT_PLAYERS_REQUIRED_COLUMNS.copy()

    if existing_players_df is not None and not existing_players_df.empty:
        template_df = pd.DataFrame()
        for col in columns:
            if col in existing_players_df.columns:
                template_df[col] = existing_players_df[col]
            else:
                template_df[col] = ""
    else:
        # Create empty template with 1248 rows for all players
        template_df = pd.DataFrame(columns=columns)
        for _ in range(C.OFFICIAL_REQUIRED_TOTAL_PLAYERS):
            template_df.loc[len(template_df)] = {col: "" for col in columns}

    output_path = output_dir / C.OFFICIAL_IMPORT_PLAYERS_TEMPLATE_FILE
    template_df.to_csv(output_path, index=False)
    return output_path


def generate_squads_import_template(
    output_dir: Path | str | None = None,
    existing_squads_df: pd.DataFrame | None = None,
) -> Path:
    """Generate import template for squads summary data.

    Args:
        output_dir: Output directory. Defaults to OFFICIAL_PROCESSED_DIR.
        existing_squads_df: Optional existing squads DataFrame to pre-populate.

    Returns:
        Path to the generated template file.
    """
    if output_dir is None:
        output_dir = C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    columns = C.IMPORT_SQUADS_REQUIRED_COLUMNS.copy()

    if existing_squads_df is not None and not existing_squads_df.empty:
        template_df = pd.DataFrame()
        for col in columns:
            if col in existing_squads_df.columns:
                template_df[col] = existing_squads_df[col]
            else:
                template_df[col] = ""
    else:
        # Create empty template with 48 rows for all teams
        template_df = pd.DataFrame(columns=columns)
        for _ in range(C.OFFICIAL_REQUIRED_TEAM_COUNT):
            template_df.loc[len(template_df)] = {col: "" for col in columns}

    output_path = output_dir / C.OFFICIAL_IMPORT_SQUADS_TEMPLATE_FILE
    template_df.to_csv(output_path, index=False)
    return output_path


def generate_all_import_templates(
    output_dir: Path | str | None = None,
    include_existing_data: bool = True,
) -> dict[str, Path]:
    """Generate all import templates at once.

    Args:
        output_dir: Output directory. Defaults to OFFICIAL_PROCESSED_DIR.
        include_existing_data: If True, pre-populate templates with existing data.

    Returns:
        Dictionary mapping template names to their file paths.
    """
    if output_dir is None:
        output_dir = C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Try to load existing data if requested
    existing_data = {}
    if include_existing_data:
        for file_name, key in [
            (C.OFFICIAL_TEAMS_FILE, "teams"),
            (C.OFFICIAL_GROUPS_FILE, "groups"),
            (C.OFFICIAL_FIXTURES_FILE, "fixtures"),
            (C.OFFICIAL_VENUES_FILE, "venues"),
            (C.OFFICIAL_PLAYERS_FILE, "players"),
            (C.OFFICIAL_SQUADS_FILE, "squads"),
        ]:
            path = output_dir / file_name
            if path.exists():
                existing_data[key] = pd.read_csv(path)

    templates = {}

    # Generate each template
    templates["teams"] = generate_teams_import_template(
        output_dir, existing_data.get("teams")
    )
    templates["groups"] = generate_groups_import_template(
        output_dir, existing_data.get("groups")
    )
    templates["fixtures"] = generate_fixtures_import_template(
        output_dir, existing_data.get("fixtures")
    )
    templates["venues"] = generate_venues_import_template(
        output_dir, existing_data.get("venues")
    )
    templates["players"] = generate_players_import_template(
        output_dir, existing_data.get("players")
    )
    templates["squads"] = generate_squads_import_template(
        output_dir, existing_data.get("squads")
    )

    return templates


def create_import_manifest(
    templates: dict[str, Path],
    output_dir: Path | str | None = None,
) -> Path:
    """Create a manifest file documenting all generated templates.

    Args:
        templates: Dictionary of template names to file paths.
        output_dir: Output directory. Defaults to OFFICIAL_PROCESSED_DIR.

    Returns:
        Path to the manifest file.
    """
    if output_dir is None:
        output_dir = C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "templates": {},
        "instructions": {
            "teams": "Fill in all 48 qualified teams with their group assignments.",
            "groups": "Fill in group compositions (12 groups x 4 teams = 48 rows).",
            "fixtures": "Fill in all 104 match fixtures with dates, venues, and teams.",
            "venues": "Fill in all 16 venue details including stadium name, city, country.",
            "players": "Fill in all 1248 player details (48 teams x 26 players).",
            "squads": "Fill in squad summaries for each of the 48 teams.",
        },
        "required_columns": {
            "teams": C.IMPORT_TEAMS_REQUIRED_COLUMNS,
            "groups": C.IMPORT_GROUPS_REQUIRED_COLUMNS,
            "fixtures": C.IMPORT_FIXTURES_REQUIRED_COLUMNS,
            "venues": C.IMPORT_VENUES_REQUIRED_COLUMNS,
            "players": C.IMPORT_PLAYERS_REQUIRED_COLUMNS,
            "squads": C.IMPORT_SQUADS_REQUIRED_COLUMNS,
        },
    }

    for name, path in templates.items():
        manifest["templates"][name] = {
            "file": str(path),
            "exists": path.exists(),
        }

    manifest_path = output_dir / "import_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    return manifest_path


def validate_import_file(
    file_path: Path | str,
    template_type: str,
) -> tuple[bool, list[str]]:
    """Validate an import file against its expected schema.

    Args:
        file_path: Path to the import file.
        template_type: Type of template (teams, groups, fixtures, venues, players, squads).

    Returns:
        Tuple of (is_valid, list_of_error_messages).
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    if not file_path.exists():
        return False, [f"File not found: {file_path}"]

    # Get required columns for this template type
    column_map = {
        "teams": C.IMPORT_TEAMS_REQUIRED_COLUMNS,
        "groups": C.IMPORT_GROUPS_REQUIRED_COLUMNS,
        "fixtures": C.IMPORT_FIXTURES_REQUIRED_COLUMNS,
        "venues": C.IMPORT_VENUES_REQUIRED_COLUMNS,
        "players": C.IMPORT_PLAYERS_REQUIRED_COLUMNS,
        "squads": C.IMPORT_SQUADS_REQUIRED_COLUMNS,
    }

    if template_type not in column_map:
        return False, [f"Unknown template type: {template_type}"]

    required_columns = column_map[template_type]

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return False, [f"Failed to read CSV: {e}"]

    errors = []

    # Check required columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        errors.append(f"Missing required columns: {missing_columns}")

    # Note: We don't check for empty rows in templates since they are expected
    # to have empty values that will be filled in by users

    # Type-specific validations
    if template_type == "teams" and not df.empty:
        if len(df) != C.OFFICIAL_REQUIRED_TEAM_COUNT:
            errors.append(f"Expected {C.OFFICIAL_REQUIRED_TEAM_COUNT} teams, got {len(df)}")

    elif template_type == "groups" and not df.empty:
        if len(df) != C.OFFICIAL_REQUIRED_TEAM_COUNT:
            errors.append(f"Expected {C.OFFICIAL_REQUIRED_TEAM_COUNT} group entries, got {len(df)}")

    elif template_type == "fixtures" and not df.empty:
        if len(df) != C.OFFICIAL_TOTAL_MATCHES:
            errors.append(f"Expected {C.OFFICIAL_TOTAL_MATCHES} fixtures, got {len(df)}")

    elif template_type == "players" and not df.empty:
        if len(df) != C.OFFICIAL_REQUIRED_TOTAL_PLAYERS:
            errors.append(f"Expected {C.OFFICIAL_REQUIRED_TOTAL_PLAYERS} players, got {len(df)}")

    is_valid = len(errors) == 0
    return is_valid, errors