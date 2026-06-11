"""Resolve missing official team names from groups, populated, and fixture sources."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C
from src.official.loaders import official_path
from src.utils.team_name_mapping import slugify_team_name, standardize_team_name

PROJECT_ROOT = getattr(C, "PROJECT_ROOT", Path(__file__).resolve().parents[2])
OFFICIAL_PROCESSED_DIR = PROJECT_ROOT / str(getattr(C, "OFFICIAL_PROCESSED_DIR", "data/official/processed"))
OFFICIAL_POPULATED_DIR = PROJECT_ROOT / str(getattr(C, "OFFICIAL_POPULATED_DATA_DIR", "data/official/populated"))

OFFICIAL_TEAMS_FILE = getattr(C, "OFFICIAL_TEAMS_FILE", "official_teams.csv")
OFFICIAL_GROUPS_FILE = getattr(C, "OFFICIAL_GROUPS_FILE", "official_groups.csv")
OFFICIAL_FIXTURES_FILE = getattr(C, "OFFICIAL_FIXTURES_FILE", "official_fixtures.csv")
POPULATED_OFFICIAL_TEAMS_FILE = getattr(C, "POPULATED_OFFICIAL_TEAMS_FILE", "populated_official_teams.csv")

_INVALID_TEAM_TOKENS = frozenset({"", "nan", "none", "nat", "<na>", "null", "tbd", "to be determined"})

TEAMS_USER_COLUMN_ORDER = [
    "Team",
    "Code",
    "Group",
    "Slot",
    "Confederation",
    "Host nation",
    "Qualified",
    "Source",
    "Last updated",
]

TEAMS_TECHNICAL_COLUMNS = ["Team ID"]


def is_valid_team_name(value: Any) -> bool:
    """Return True when value is a displayable team label."""
    if value is None:
        return False
    if isinstance(value, float) and pd.isna(value):
        return False
    token = str(value).strip()
    if not token:
        return False
    lower = token.lower()
    if lower in _INVALID_TEAM_TOKENS:
        return False
    return not lower.startswith("tbd")


def teams_need_name_repair(df: pd.DataFrame) -> bool:
    """True when any row lacks a usable team name."""
    if df.empty or "team" not in df.columns:
        return False
    return bool((~df["team"].map(is_valid_team_name)).any())


def _read_csv_if_exists(path: Path) -> pd.DataFrame:
    if not path.is_file():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def _team_id_row_index(team_id: Any) -> int | None:
    match = re.match(r"team_(\d+)$", str(team_id).strip(), flags=re.IGNORECASE)
    if not match:
        return None
    return int(match.group(1)) - 1


def _normalize_groups_lookup(groups_df: pd.DataFrame) -> pd.DataFrame:
    if groups_df.empty:
        return pd.DataFrame()
    lookup = groups_df.reset_index(drop=True).copy()
    if "team" in lookup.columns:
        lookup["team"] = lookup["team"].map(standardize_team_name)
    lookup["_row_index"] = range(len(lookup))
    return lookup


def _normalize_populated_lookup(populated_df: pd.DataFrame) -> pd.DataFrame:
    if populated_df.empty:
        return pd.DataFrame()
    lookup = populated_df.reset_index(drop=True).copy()
    if "team" in lookup.columns:
        lookup["team"] = lookup["team"].map(standardize_team_name)
    lookup["_row_index"] = range(len(lookup))
    return lookup


def _lookup_by_group_slot(source_df: pd.DataFrame, group: Any, slot: Any) -> dict[str, Any]:
    if source_df.empty or "team" not in source_df.columns:
        return {}
    slot_col = "group_slot" if "group_slot" in source_df.columns else "slot"
    if "group" not in source_df.columns or slot_col not in source_df.columns:
        return {}
    group_token = str(group).strip().upper()
    try:
        slot_num = int(pd.to_numeric(slot, errors="coerce"))
    except (TypeError, ValueError):
        return {}
    if not group_token or pd.isna(slot_num):
        return {}
    matched = source_df[
        (source_df["group"].astype(str).str.strip().str.upper() == group_token)
        & (pd.to_numeric(source_df[slot_col], errors="coerce") == slot_num)
    ]
    if matched.empty:
        return {}
    return matched.iloc[0].to_dict()


def _lookup_by_team_id_slug(source_df: pd.DataFrame, team_id: Any) -> dict[str, Any]:
    if source_df.empty or "team" not in source_df.columns:
        return {}
    token = str(team_id).strip().lower()
    if not token:
        return {}
    for _, row in source_df.iterrows():
        team = row.get("team")
        if not is_valid_team_name(team):
            continue
        slug = slugify_team_name(str(team))
        if slug and slug.replace("-", "_") == token.replace("-", "_"):
            return row.to_dict()
        if token == slug:
            return row.to_dict()
    return {}


def _lookup_by_row_index(source_df: pd.DataFrame, row_index: int | None) -> dict[str, Any]:
    if source_df.empty or row_index is None or row_index < 0 or row_index >= len(source_df):
        return {}
    return source_df.iloc[int(row_index)].to_dict()


def _coalesce_field(row: pd.Series, field: str, patch: dict[str, Any], *, aliases: tuple[str, ...] = ()) -> Any:
    current = row.get(field)
    if field == "team":
        if is_valid_team_name(current):
            return standardize_team_name(str(current))
    elif pd.notna(current) and str(current).strip() not in {"", "nan"}:
        return current

    keys = (field, *aliases)
    for key in keys:
        if key not in patch:
            continue
        value = patch.get(key)
        if field == "team":
            if is_valid_team_name(value):
                return standardize_team_name(str(value))
        elif pd.notna(value) and str(value).strip() not in {"", "nan"}:
            return value
    return current


def _build_patch_for_row(
    row: pd.Series,
    *,
    groups_lookup: pd.DataFrame,
    populated_lookup: pd.DataFrame,
) -> dict[str, Any]:
    patches: list[dict[str, Any]] = []

    group_val = row.get("group")
    slot_val = row.get("group_slot", row.get("slot"))
    if pd.notna(group_val) and pd.notna(slot_val):
        for source_df in (populated_lookup, groups_lookup):
            patch = _lookup_by_group_slot(source_df, group_val, slot_val)
            if patch:
                patches.append(patch)

    row_index = _team_id_row_index(row.get("team_id"))
    if row_index is None:
        row_index = int(row.name) if isinstance(row.name, int) else None

    for source_df in (populated_lookup, groups_lookup):
        patch = _lookup_by_row_index(source_df, row_index)
        if patch:
            patches.append(patch)

    patch = _lookup_by_team_id_slug(populated_lookup, row.get("team_id"))
    if patch:
        patches.append(patch)
    patch = _lookup_by_team_id_slug(groups_lookup, row.get("team_id"))
    if patch:
        patches.append(patch)

    merged: dict[str, Any] = {}
    for patch in reversed(patches):
        merged.update({key: value for key, value in patch.items() if pd.notna(value)})
    return merged


def enrich_official_teams_dataframe(
    teams_df: pd.DataFrame,
    *,
    groups_df: pd.DataFrame | None = None,
    populated_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Fill missing team metadata using official groups and populated team tables."""
    if teams_df.empty:
        return teams_df.copy()

    out = teams_df.copy()
    for col in ("team", "team_code", "confederation", "group", "source", "last_verified_at"):
        if col in out.columns:
            out[col] = out[col].astype(object)

    if groups_df is None:
        groups_df = _read_csv_if_exists(official_path(OFFICIAL_GROUPS_FILE))
    if populated_df is None:
        populated_df = _read_csv_if_exists(OFFICIAL_POPULATED_DIR / POPULATED_OFFICIAL_TEAMS_FILE)

    groups_lookup = _normalize_groups_lookup(groups_df)
    populated_lookup = _normalize_populated_lookup(populated_df)

    for idx, row in out.iterrows():
        if is_valid_team_name(row.get("team")):
            out.at[idx, "team"] = standardize_team_name(str(row.get("team")))
            continue

        patch = _build_patch_for_row(row, groups_lookup=groups_lookup, populated_lookup=populated_lookup)
        if not patch:
            continue

        out.at[idx, "team"] = _coalesce_field(row, "team", patch)
        out.at[idx, "team_code"] = _coalesce_field(row, "team_code", patch)
        out.at[idx, "confederation"] = _coalesce_field(row, "confederation", patch)
        out.at[idx, "group"] = _coalesce_field(row, "group", patch)
        out.at[idx, "group_slot"] = _coalesce_field(row, "group_slot", patch, aliases=("slot",))
        out.at[idx, "is_host"] = _coalesce_field(row, "is_host", patch)
        out.at[idx, "qualified"] = _coalesce_field(row, "qualified", patch, aliases=())
        if not pd.notna(row.get("source")) or str(row.get("source")).strip() in {"", "nan"}:
            source_val = patch.get("source")
            if pd.notna(source_val) and str(source_val).strip() not in {"", "nan"}:
                out.at[idx, "source"] = source_val

    if "team" in out.columns:
        out["team"] = out["team"].map(lambda value: standardize_team_name(value) if is_valid_team_name(value) else value)

    return out


def repair_official_teams_artifact(
    *,
    persist: bool = True,
    teams_df: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, bool]:
    """Repair processed official teams and optionally persist to disk."""
    path = official_path(OFFICIAL_TEAMS_FILE)
    original = teams_df.copy() if teams_df is not None else _read_csv_if_exists(path)
    if original.empty:
        return original, False

    repaired = enrich_official_teams_dataframe(original)
    changed = teams_need_name_repair(original) and not teams_need_name_repair(repaired)

    if persist and changed:
        path.parent.mkdir(parents=True, exist_ok=True)
        repaired.to_csv(path, index=False)

    return repaired, changed


def _format_bool(value: Any) -> str:
    if pd.isna(value):
        return "—"
    try:
        return "Yes" if int(value) == 1 else "No"
    except (TypeError, ValueError):
        token = str(value).strip().lower()
        if token in {"true", "yes", "y"}:
            return "Yes"
        if token in {"false", "no", "n"}:
            return "No"
    return str(value)


def format_official_teams_for_display(
    teams_df: pd.DataFrame,
    *,
    include_technical: bool = False,
) -> pd.DataFrame:
    """Return a user-friendly teams table for Streamlit previews."""
    if teams_df.empty:
        return teams_df.copy()

    df = enrich_official_teams_dataframe(teams_df)
    display = pd.DataFrame(
        {
            "Team": df.get("team", pd.Series(dtype=str)),
            "Code": df.get("team_code", pd.Series(dtype=str)),
            "Group": df.get("group", pd.Series(dtype=str)),
            "Slot": df.get("group_slot", pd.Series(dtype=str)),
            "Confederation": df.get("confederation", pd.Series(dtype=str)),
            "Host nation": df.get("is_host", pd.Series(dtype=str)).map(_format_bool),
            "Qualified": df.get("qualified", pd.Series(dtype=str)).map(_format_bool),
            "Source": df.get("source", pd.Series(dtype=str)),
            "Last updated": df.get("last_verified_at", pd.Series(dtype=str)),
        }
    )
    if include_technical and "team_id" in df.columns:
        display.insert(0, "Team ID", df["team_id"])

    sort_cols = [col for col in ("Group", "Slot", "Team") if col in display.columns]
    if sort_cols:
        display = display.sort_values(sort_cols, na_position="last").reset_index(drop=True)

    if include_technical:
        return display
    return display[TEAMS_USER_COLUMN_ORDER]
