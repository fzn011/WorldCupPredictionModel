"""Master Excel workbook generator for Step 17D official data population."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C


def _workbook_dir() -> Path:
    return C.PROJECT_ROOT / C.OFFICIAL_POPULATION_WORKBOOK_DIR


def _sheet_columns() -> dict[str, list[str]]:
    return {
        "Teams": C.IMPORT_TEAMS_REQUIRED_COLUMNS,
        "Groups": C.IMPORT_GROUPS_REQUIRED_COLUMNS,
        "Fixtures": C.IMPORT_FIXTURES_REQUIRED_COLUMNS,
        "Venues": C.IMPORT_VENUES_REQUIRED_COLUMNS,
        "Players": C.IMPORT_PLAYERS_REQUIRED_COLUMNS,
        "Player_Priors": C.IMPORT_PLAYER_PRIORS_REQUIRED_COLUMNS,
    }


def _row_counts() -> dict[str, int]:
    return {
        "Teams": C.OFFICIAL_REQUIRED_TEAM_COUNT,
        "Groups": C.OFFICIAL_REQUIRED_TEAM_COUNT,
        "Fixtures": C.OFFICIAL_TOTAL_MATCHES,
        "Venues": 16,
        "Players": C.OFFICIAL_REQUIRED_TOTAL_PLAYERS,
        "Player_Priors": C.OFFICIAL_REQUIRED_TOTAL_PLAYERS,
    }


def create_master_import_readme(output_path: str | None = None) -> str:
    """Save README for the master import workbook."""
    if output_path is None:
        output_path = str(_workbook_dir() / C.OFFICIAL_MASTER_IMPORT_README_FILE)

    content = f"""# Official World Cup 2026 Master Import Workbook

## Purpose

This workbook (or CSV template pack fallback) supports **manual** entry of verified FIFA
World Cup 2026 data. The application does not fetch or auto-fill official data.

## Sheets

| Sheet | Required rows | Description |
|-------|---------------|-------------|
| Teams | {C.OFFICIAL_REQUIRED_TEAM_COUNT} | Qualified teams with group assignments |
| Groups | {C.OFFICIAL_REQUIRED_TEAM_COUNT} | Group compositions (12×4) |
| Fixtures | {C.OFFICIAL_TOTAL_MATCHES} | Full schedule including knockouts |
| Venues | 16+ | Stadium details |
| Players | {C.OFFICIAL_REQUIRED_TOTAL_PLAYERS} | Squad lists (26 per team) |
| Player_Priors | {C.OFFICIAL_REQUIRED_TOTAL_PLAYERS} | Editable priors for official players |
| Validation_Rules | — | Row counts and field rules |

## Workflow

1. Fill each sheet from official FIFA sources
2. Export individual sheets to CSV matching import template column headers
3. Preview: `python scripts/preview_official_import.py --target <type> --file <csv>`
4. Apply: `python scripts/apply_official_import.py --type <type> <csv>`
5. Re-run readiness: `python scripts/evaluate_official_final_readiness.py`

## Verification fields

When filling data, include where possible: {", ".join(C.OFFICIAL_VERIFICATION_FIELDS)}

Do **not** use `sample_to_be_verified` as a source value for production data.
"""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return str(path)


def _validation_rules_df() -> pd.DataFrame:
    rows = []
    for sheet, count in _row_counts().items():
        rows.append(
            {
                "sheet": sheet,
                "required_rows": count,
                "required_columns": ", ".join(_sheet_columns().get(sheet, [])),
                "notes": "Fill from official FIFA sources only",
            }
        )
    return pd.DataFrame(rows)


def create_master_import_workbook(output_path: str | None = None) -> str:
    """Create master Excel workbook with import template sheets."""
    if output_path is None:
        output_path = str(_workbook_dir() / C.OFFICIAL_MASTER_IMPORT_WORKBOOK_FILE)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    readme_lines = [
        "Official World Cup 2026 Master Import Workbook",
        "Fill each sheet manually from verified FIFA sources.",
        "Do not use sample_to_be_verified as source.",
        f"Required teams: {C.OFFICIAL_REQUIRED_TEAM_COUNT}",
        f"Required fixtures: {C.OFFICIAL_TOTAL_MATCHES}",
        f"Required players: {C.OFFICIAL_REQUIRED_TOTAL_PLAYERS}",
    ]
    readme_df = pd.DataFrame({"Instruction": readme_lines})

    try:
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            readme_df.to_excel(writer, sheet_name="README", index=False)
            for sheet_name, columns in _sheet_columns().items():
                count = _row_counts().get(sheet_name, 0)
                df = pd.DataFrame(columns=columns)
                for _ in range(count):
                    df.loc[len(df)] = {col: "" for col in columns}
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            _validation_rules_df().to_excel(writer, sheet_name="Validation_Rules", index=False)
        return str(path)
    except ImportError:
        # Fallback: write CSV templates alongside readme
        fallback_dir = path.parent / "csv_fallback"
        fallback_dir.mkdir(parents=True, exist_ok=True)
        for sheet_name, columns in _sheet_columns().items():
            count = _row_counts().get(sheet_name, 0)
            df = pd.DataFrame(columns=columns)
            for _ in range(count):
                df.loc[len(df)] = {col: "" for col in columns}
            df.to_csv(fallback_dir / f"{sheet_name.lower()}_template.csv", index=False)
        _validation_rules_df().to_csv(fallback_dir / "validation_rules.csv", index=False)
        readme_df.to_csv(fallback_dir / "readme.csv", index=False)
        raise


def generate_population_workbook_pack() -> dict[str, Any]:
    """Generate master workbook and readme; fallback gracefully if openpyxl missing."""
    notes: list[str] = []
    readme_path = create_master_import_readme()
    workbook_path = ""

    try:
        workbook_path = create_master_import_workbook()
        status = "ok"
    except ImportError:
        status = "fallback"
        workbook_path = str(_workbook_dir() / "csv_fallback")
        notes.append(
            "openpyxl not installed; CSV fallback templates written to csv_fallback/ "
            "instead of Excel workbook. Install openpyxl for .xlsx support."
        )
    except Exception as exc:
        status = "fallback"
        workbook_path = readme_path
        notes.append(f"Workbook generation failed ({exc}); README and CSV templates available.")

    return {
        "status": status,
        "workbook_path": workbook_path,
        "readme_path": readme_path,
        "notes": notes,
    }
