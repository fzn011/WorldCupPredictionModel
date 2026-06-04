"""Tournament group loading, validation, and persistence utilities."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import src.utils.constants as C
from src.utils.team_name_mapping import standardize_team_name

PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")
SAMPLE_DATA_DIR = getattr(C, "SAMPLE_DATA_DIR", Path("data") / "sample")
TOURNAMENT_GROUPS_FILE = getattr(C, "TOURNAMENT_GROUPS_FILE", "tournament_groups.csv")
WC2026_GROUPS = getattr(C, "WC2026_GROUPS", ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"])
WC2026_TEAMS_PER_GROUP = getattr(C, "WC2026_TEAMS_PER_GROUP", 4)
WC2026_TOTAL_TEAMS = getattr(C, "WC2026_TOTAL_TEAMS", 48)

REQUIRED_GROUP_COLUMNS: list[str] = ["group", "slot", "team", "confederation", "is_host"]


def _report_row(check: str, passed: bool, details: str) -> dict[str, object]:
    return {"section": "groups", "check": check, "passed": bool(passed), "details": details}


def load_tournament_groups(path: str | None = None) -> pd.DataFrame:
    """Load tournament groups from processed file with sample fallback."""
    if path:
        file_path = Path(path)
    else:
        processed_path = PROCESSED_DATA_DIR / TOURNAMENT_GROUPS_FILE
        sample_path = SAMPLE_DATA_DIR / "sample_tournament_groups.csv"
        file_path = processed_path if processed_path.is_file() else sample_path

    if not file_path.is_file():
        raise FileNotFoundError(
            f"Tournament groups file not found at {file_path}. "
            "Create data/sample/sample_tournament_groups.csv or run prepare script."
        )

    df = pd.read_csv(file_path)
    missing = [column for column in REQUIRED_GROUP_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Tournament groups file missing required columns: {missing}")

    out = df.copy()
    out["group"] = out["group"].astype(str).str.strip().str.upper()
    out["slot"] = pd.to_numeric(out["slot"], errors="coerce").astype("Int64")
    out["team"] = out["team"].map(standardize_team_name)
    out["confederation"] = out["confederation"].astype(str).str.strip()
    out["is_host"] = pd.to_numeric(out["is_host"], errors="coerce").fillna(0).astype(int)
    return out


def validate_tournament_groups(groups_df: pd.DataFrame) -> tuple[bool, pd.DataFrame]:
    """Validate tournament groups against 2026 format requirements."""
    rows: list[dict[str, object]] = []

    missing_columns = [column for column in REQUIRED_GROUP_COLUMNS if column not in groups_df.columns]
    rows.append(
        _report_row(
            "required_columns_present",
            not missing_columns,
            "all required columns found" if not missing_columns else f"missing columns: {missing_columns}",
        )
    )

    groups_present = sorted(groups_df["group"].dropna().astype(str).str.upper().unique().tolist()) if "group" in groups_df.columns else []
    expected_groups = sorted(WC2026_GROUPS)
    rows.append(
        _report_row(
            "all_groups_present",
            groups_present == expected_groups,
            f"expected={expected_groups}, found={groups_present}",
        )
    )

    valid_group_size = True
    group_size_detail = ""
    if "group" in groups_df.columns:
        counts = groups_df.groupby("group")["team"].count().to_dict()
        invalid = {group: count for group, count in counts.items() if count != WC2026_TEAMS_PER_GROUP}
        valid_group_size = not invalid and len(counts) == len(WC2026_GROUPS)
        group_size_detail = f"counts={counts}" if valid_group_size else f"invalid_counts={invalid}, counts={counts}"
    rows.append(_report_row("group_size_exactly_4", valid_group_size, group_size_detail or "unable to evaluate"))

    valid_slots = True
    slot_detail = ""
    if {"group", "slot"}.issubset(set(groups_df.columns)):
        invalid_slots: dict[str, list[int]] = {}
        for group, part in groups_df.groupby("group"):
            slots = sorted([int(x) for x in part["slot"].dropna().tolist()])
            if slots != [1, 2, 3, 4]:
                invalid_slots[str(group)] = slots
        valid_slots = not invalid_slots
        slot_detail = "slots are 1..4 per group" if valid_slots else f"invalid_slots={invalid_slots}"
    rows.append(_report_row("slots_1_to_4_per_group", valid_slots, slot_detail or "unable to evaluate"))

    total_rows = int(len(groups_df))
    rows.append(
        _report_row(
            "total_teams_48",
            total_rows == WC2026_TOTAL_TEAMS,
            f"expected={WC2026_TOTAL_TEAMS}, found={total_rows}",
        )
    )

    duplicate_teams = (
        groups_df[groups_df["team"].duplicated()]["team"].tolist() if "team" in groups_df.columns else []
    )
    rows.append(
        _report_row(
            "no_duplicate_team_names",
            len(duplicate_teams) == 0,
            "no duplicates" if not duplicate_teams else f"duplicates={duplicate_teams}",
        )
    )

    report_df = pd.DataFrame(rows)
    return bool(report_df["passed"].all()), report_df


def create_group_lookup(groups_df: pd.DataFrame) -> dict[str, dict[int, str]]:
    """Create nested dictionary: {group: {slot: team}}."""
    lookup: dict[str, dict[int, str]] = {}
    for _, row in groups_df.iterrows():
        group = str(row["group"]).upper()
        slot = int(row["slot"])
        team = str(row["team"])
        lookup.setdefault(group, {})[slot] = team
    return lookup


def save_tournament_groups(groups_df: pd.DataFrame, output_path: str | None = None) -> str:
    """Save tournament groups to processed data folder."""
    path = Path(output_path) if output_path else PROCESSED_DATA_DIR / TOURNAMENT_GROUPS_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    groups_df.to_csv(path, index=False)
    return str(path)
