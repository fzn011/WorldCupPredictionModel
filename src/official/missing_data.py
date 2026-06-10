"""Missing-data reporting utilities for Step 17D."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import src.utils.constants as C


def find_missing_or_placeholder_values(
    df: pd.DataFrame,
    dataset_name: str,
    required_columns: list[str],
    placeholder_values: list[str],
) -> pd.DataFrame:
    """Find missing columns, missing values, and placeholder values in a DataFrame."""
    rows: list[dict[str, str]] = []
    placeholders = {str(v).strip() for v in placeholder_values}

    for col in required_columns:
        if col not in df.columns:
            rows.append(
                {
                    "dataset": dataset_name,
                    "row_index": "",
                    "column": col,
                    "value": "",
                    "issue_type": "missing_column",
                    "severity": "error",
                    "message": f"Required column '{col}' is missing",
                }
            )

    if df.empty:
        rows.append(
            {
                "dataset": dataset_name,
                "row_index": "",
                "column": "",
                "value": "",
                "issue_type": "missing_value",
                "severity": "error",
                "message": "Dataset is empty",
            }
        )
        return pd.DataFrame(rows)

    for idx, row in df.iterrows():
        for col in required_columns:
            if col not in df.columns:
                continue
            raw = row[col]
            value = "" if pd.isna(raw) else str(raw).strip()
            if value == "":
                rows.append(
                    {
                        "dataset": dataset_name,
                        "row_index": str(idx),
                        "column": col,
                        "value": value,
                        "issue_type": "missing_value",
                        "severity": "warning",
                        "message": f"Missing value in column '{col}'",
                    }
                )
            elif value in placeholders:
                rows.append(
                    {
                        "dataset": dataset_name,
                        "row_index": str(idx),
                        "column": col,
                        "value": value,
                        "issue_type": "placeholder_value",
                        "severity": "error",
                        "message": f"Placeholder value '{value}' in column '{col}'",
                    }
                )

    return pd.DataFrame(rows)


def _load_official_csv(filename: str, processed_dir: Path) -> pd.DataFrame | None:
    path = processed_dir / filename
    if not path.is_file():
        return None
    return pd.read_csv(path)


def build_official_missing_data_report() -> pd.DataFrame:
    """Build a combined missing-data report across official datasets."""
    official_dir = C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR
    processed_dir = C.PROJECT_ROOT / C.PROCESSED_DATA_DIR
    placeholders = list(C.OFFICIAL_PLACEHOLDER_VALUES)

    datasets: list[tuple[str, Path, str, list[str]]] = [
        ("teams", official_dir, C.OFFICIAL_TEAMS_FILE, C.OFFICIAL_TEAMS_REQUIRED_COLUMNS),
        ("groups", official_dir, C.OFFICIAL_GROUPS_FILE, C.OFFICIAL_GROUPS_REQUIRED_COLUMNS),
        ("fixtures", official_dir, C.OFFICIAL_FIXTURES_FILE, C.OFFICIAL_FIXTURES_REQUIRED_COLUMNS),
        ("venues", official_dir, C.OFFICIAL_VENUES_FILE, C.OFFICIAL_VENUES_REQUIRED_COLUMNS),
        ("players", official_dir, C.OFFICIAL_PLAYERS_FILE, C.OFFICIAL_PLAYERS_REQUIRED_COLUMNS),
        (
            "award_candidates",
            processed_dir,
            C.OFFICIAL_AWARD_CANDIDATES_FILE,
            C.OFFICIAL_AWARD_CANDIDATES_REQUIRED_COLUMNS,
        ),
    ]

    parts: list[pd.DataFrame] = []
    for name, directory, filename, columns in datasets:
        path = directory / filename
        if not path.is_file():
            parts.append(
                pd.DataFrame(
                    [
                        {
                            "dataset": name,
                            "row_index": "",
                            "column": "",
                            "value": "",
                            "issue_type": "missing_value",
                            "severity": "error",
                            "message": f"File not found: {filename}",
                        }
                    ]
                )
            )
            continue
        df = pd.read_csv(path)
        parts.append(find_missing_or_placeholder_values(df, name, columns, placeholders))

    if not parts:
        return pd.DataFrame(
            columns=[
                "dataset",
                "row_index",
                "column",
                "value",
                "issue_type",
                "severity",
                "message",
            ]
        )
    return pd.concat(parts, ignore_index=True)


def save_missing_data_report(
    report_df: pd.DataFrame,
    output_path: str | None = None,
) -> str:
    """Save the missing-data report CSV."""
    if output_path is None:
        output_path = str(
            C.PROJECT_ROOT
            / C.OFFICIAL_POPULATION_REPORTS_DIR
            / C.OFFICIAL_POPULATION_MISSING_DATA_REPORT_FILE
        )
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    report_df.to_csv(path, index=False)
    return str(path)
