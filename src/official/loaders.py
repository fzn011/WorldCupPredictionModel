"""Loaders for official World Cup 2026 data artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

import src.utils.constants as C
from src.utils.team_name_mapping import standardize_team_name

PROJECT_ROOT = getattr(C, "PROJECT_ROOT", Path(__file__).resolve().parents[2])
OFFICIAL_PROCESSED_DIR = PROJECT_ROOT / str(getattr(C, "OFFICIAL_PROCESSED_DIR", "data/official/processed"))
OFFICIAL_TEAMS_FILE = getattr(C, "OFFICIAL_TEAMS_FILE", "official_teams.csv")
OFFICIAL_GROUPS_FILE = getattr(C, "OFFICIAL_GROUPS_FILE", "official_groups.csv")
OFFICIAL_FIXTURES_FILE = getattr(C, "OFFICIAL_FIXTURES_FILE", "official_fixtures.csv")
OFFICIAL_VENUES_FILE = getattr(C, "OFFICIAL_VENUES_FILE", "official_venues.csv")
OFFICIAL_MATCH_CALENDAR_FILE = getattr(C, "OFFICIAL_MATCH_CALENDAR_FILE", "official_match_calendar.csv")
OFFICIAL_SOURCE_MANIFEST_FILE = getattr(C, "OFFICIAL_SOURCE_MANIFEST_FILE", "source_manifest.json")


def official_path(filename: str) -> Path:
    """Return a path under `data/official/processed/`."""
    return OFFICIAL_PROCESSED_DIR / filename



def _load_csv_required(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Official data file not found: {path}")
    return pd.read_csv(path)



def load_official_teams(path: str | None = None) -> pd.DataFrame:
    """Load official teams table and standardize team names."""
    df = _load_csv_required(Path(path) if path else official_path(OFFICIAL_TEAMS_FILE))
    if "team" in df.columns:
        df["team"] = df["team"].map(standardize_team_name)
    return df



def load_official_groups(path: str | None = None) -> pd.DataFrame:
    """Load official groups table and standardize team names."""
    df = _load_csv_required(Path(path) if path else official_path(OFFICIAL_GROUPS_FILE))
    if "team" in df.columns:
        df["team"] = df["team"].map(standardize_team_name)
    return df



def load_official_fixtures(path: str | None = None) -> pd.DataFrame:
    """Load official fixtures table and standardize fixture team names."""
    df = _load_csv_required(Path(path) if path else official_path(OFFICIAL_FIXTURES_FILE))
    for column in ["team_a", "team_b"]:
        if column in df.columns:
            df[column] = df[column].map(standardize_team_name)
    return df



def load_official_venues(path: str | None = None) -> pd.DataFrame:
    """Load official venues table."""
    return _load_csv_required(Path(path) if path else official_path(OFFICIAL_VENUES_FILE))



def load_official_match_calendar(path: str | None = None) -> pd.DataFrame:
    """Load official match calendar table."""
    return _load_csv_required(Path(path) if path else official_path(OFFICIAL_MATCH_CALENDAR_FILE))



def load_source_manifest(path: str | None = None) -> dict:
    """Load official source manifest JSON."""
    manifest_path = Path(path) if path else official_path(OFFICIAL_SOURCE_MANIFEST_FILE)
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Official source manifest not found: {manifest_path}")
    with manifest_path.open("r", encoding="utf-8") as f:
        return json.load(f)



def _filter_valid_team_names(values: list) -> list[str]:
    invalid = {"", "nan", "none", "tbd", "to be determined"}
    out: set[str] = set()
    for value in values:
        if pd.isna(value):
            continue
        name = standardize_team_name(str(value).strip())
        lower = name.lower()
        if not name or lower in invalid or lower.startswith("tbd"):
            continue
        out.add(name)
    return sorted(out)


def _load_teams_dataframe_for_list() -> pd.DataFrame:
    """Prefer populated official teams (48) over processed official teams."""
    populated_path = C.PROJECT_ROOT / C.OFFICIAL_POPULATED_DATA_DIR / C.POPULATED_OFFICIAL_TEAMS_FILE
    processed_path = official_path(OFFICIAL_TEAMS_FILE)

    populated_df = pd.DataFrame()
    if populated_path.is_file():
        try:
            populated_df = pd.read_csv(populated_path)
        except Exception:
            populated_df = pd.DataFrame()

    if not populated_df.empty and "team" in populated_df.columns:
        valid = _filter_valid_team_names(populated_df["team"].tolist())
        if len(valid) >= C.OFFICIAL_REQUIRED_TEAM_COUNT:
            if "source" in populated_df.columns:
                from src.official.source_labels import is_official_source_label, is_sample_source_label

                if populated_df["source"].fillna("").astype(str).map(is_official_source_label).any():
                    return populated_df
                if not populated_df["source"].fillna("").astype(str).map(is_sample_source_label).all():
                    return populated_df
            else:
                return populated_df

    if processed_path.is_file():
        try:
            return pd.read_csv(processed_path)
        except Exception:
            pass
    return populated_df


def get_official_team_list() -> list[str]:
    """Return sorted official team names, preferring populated 48-team data when available."""
    teams_df = _load_teams_dataframe_for_list()
    if "team" not in teams_df.columns:
        return []
    return _filter_valid_team_names(teams_df["team"].tolist())



def is_official_team(team_name: str) -> bool:
    """Return whether a team name exists in the official World Cup 2026 team list."""
    return standardize_team_name(team_name) in set(get_official_team_list())
