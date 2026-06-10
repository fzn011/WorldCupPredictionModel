"""Import preview and diff utilities for Step 17D."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import src.utils.constants as C


def infer_key_columns(target_name: str) -> list[str]:
    """Infer key columns for comparing import vs current official data."""
    mapping = {
        "teams": ["team"],
        "groups": ["group", "slot"],
        "fixtures": ["match_id"],
        "venues": ["venue_id"],
        "players": ["player_id"],
        "player_priors": ["player", "team"],
    }
    if target_name not in mapping:
        raise ValueError(f"Unknown target: {target_name}")
    keys = mapping[target_name]
    current_path = _resolve_current_path(target_name)
    if current_path is not None:
        current_df = pd.read_csv(current_path)
        if target_name == "venues" and "venue_id" not in current_df.columns and "stadium" in current_df.columns:
            return ["stadium"]
        available = [k for k in keys if k in current_df.columns]
        if available:
            return available
    return keys


def _resolve_current_path(target_name: str) -> Path | None:
    if target_name == "player_priors":
        path = C.PROJECT_ROOT / C.PROCESSED_DATA_DIR / C.PLAYER_AWARD_PRIORS_FILE
    else:
        file_map = {
            "teams": C.OFFICIAL_TEAMS_FILE,
            "groups": C.OFFICIAL_GROUPS_FILE,
            "fixtures": C.OFFICIAL_FIXTURES_FILE,
            "venues": C.OFFICIAL_VENUES_FILE,
            "players": C.OFFICIAL_PLAYERS_FILE,
        }
        path = C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR / file_map[target_name]
    return path if path.is_file() else None


def compare_import_to_current(
    import_df: pd.DataFrame,
    current_df: pd.DataFrame,
    key_columns: list[str],
    dataset_name: str,
) -> pd.DataFrame:
    """Compare an import DataFrame against the current official file."""
    rows: list[dict[str, str]] = []

    def _key(row: pd.Series) -> str:
        parts = []
        for col in key_columns:
            val = row.get(col, "") if col in row.index else ""
            parts.append("" if pd.isna(val) else str(val).strip())
        return "|".join(parts)

    import_keys = {_key(import_df.loc[i]): i for i in import_df.index}
    current_keys = {_key(current_df.loc[i]): i for i in current_df.index}

    all_keys = set(import_keys) | set(current_keys)
    compare_columns = sorted(set(import_df.columns) | set(current_df.columns))

    for key in sorted(all_keys):
        in_import = key in import_keys
        in_current = key in current_keys

        if in_import and not in_current:
            rows.append(
                {
                    "dataset": dataset_name,
                    "change_type": "added_row",
                    "key": key,
                    "column": "",
                    "old_value": "",
                    "new_value": "",
                    "message": f"Row '{key}' will be added",
                }
            )
            continue

        if in_current and not in_import:
            rows.append(
                {
                    "dataset": dataset_name,
                    "change_type": "removed_row",
                    "key": key,
                    "column": "",
                    "old_value": "",
                    "new_value": "",
                    "message": f"Row '{key}' will be removed",
                }
            )
            continue

        import_row = import_df.loc[import_keys[key]]
        current_row = current_df.loc[current_keys[key]]
        row_changed = False

        for col in compare_columns:
            old_val = "" if col not in current_row.index or pd.isna(current_row[col]) else str(current_row[col])
            new_val = "" if col not in import_row.index or pd.isna(import_row[col]) else str(import_row[col])
            if old_val != new_val:
                row_changed = True
                rows.append(
                    {
                        "dataset": dataset_name,
                        "change_type": "changed_value",
                        "key": key,
                        "column": col,
                        "old_value": old_val,
                        "new_value": new_val,
                        "message": f"Column '{col}' changed for '{key}'",
                    }
                )

        if not row_changed:
            rows.append(
                {
                    "dataset": dataset_name,
                    "change_type": "unchanged",
                    "key": key,
                    "column": "",
                    "old_value": "",
                    "new_value": "",
                    "message": f"Row '{key}' unchanged",
                }
            )

    return pd.DataFrame(rows)


def preview_official_import(import_path: str, target_name: str) -> pd.DataFrame:
    """Load import and current target, then produce a diff report."""
    import_file = Path(import_path)
    if not import_file.is_file():
        raise FileNotFoundError(f"Import file not found: {import_path}")

    import_df = pd.read_csv(import_file)
    current_path = _resolve_current_path(target_name)

    if current_path is None:
        key_columns = infer_key_columns(target_name)
        rows = []
        for idx in import_df.index:
            key_parts = []
            for col in key_columns:
                val = import_df.loc[idx, col] if col in import_df.columns else ""
                key_parts.append("" if pd.isna(val) else str(val).strip())
            rows.append(
                {
                    "dataset": target_name,
                    "change_type": "added_row",
                    "key": "|".join(key_parts),
                    "column": "",
                    "old_value": "",
                    "new_value": "",
                    "message": "No current file; all rows are new",
                }
            )
        return pd.DataFrame(rows)

    current_df = pd.read_csv(current_path)
    key_columns = infer_key_columns(target_name)
    return compare_import_to_current(import_df, current_df, key_columns, target_name)


def save_import_diff_report(
    diff_df: pd.DataFrame,
    output_path: str | None = None,
) -> str:
    """Save the import diff report CSV."""
    if output_path is None:
        output_path = str(
            C.PROJECT_ROOT
            / C.OFFICIAL_POPULATION_REPORTS_DIR
            / C.OFFICIAL_POPULATION_DIFF_REPORT_FILE
        )
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    diff_df.to_csv(path, index=False)
    return str(path)
