"""Official World Cup 2026 data contracts and schema helpers."""

from __future__ import annotations

from typing import Any

import pandas as pd

import src.utils.constants as C

OFFICIAL_DATA_CONTRACTS: dict[str, list[str]] = {
    "teams": list(getattr(C, "OFFICIAL_TEAMS_REQUIRED_COLUMNS", [])),
    "groups": list(getattr(C, "OFFICIAL_GROUPS_REQUIRED_COLUMNS", [])),
    "fixtures": list(getattr(C, "OFFICIAL_FIXTURES_REQUIRED_COLUMNS", [])),
    "venues": list(getattr(C, "OFFICIAL_VENUES_REQUIRED_COLUMNS", [])),
    "match_calendar": list(getattr(C, "OFFICIAL_MATCH_CALENDAR_REQUIRED_COLUMNS", [])),
}


def get_official_contract(name: str) -> list[str]:
    """Return required column list for a named official dataset contract."""
    if name not in OFFICIAL_DATA_CONTRACTS:
        raise KeyError(f"Unknown official data contract: {name}")
    return OFFICIAL_DATA_CONTRACTS[name]



def check_required_columns(df: pd.DataFrame, required_columns: list[str], dataset_name: str) -> tuple[bool, list[str]]:
    """Check required columns for an official dataset and return missing columns."""
    if df is None:
        return False, list(required_columns)
    missing = [column for column in required_columns if column not in df.columns]
    return len(missing) == 0, missing
