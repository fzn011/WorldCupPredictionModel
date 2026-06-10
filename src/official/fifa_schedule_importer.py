"""FIFA downloadable schedule file importer for Step 17F."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C
from src.official.fifa_extractors import make_source_audit_row, normalize_fifa_team_name


def _populated_dir() -> Path:
    p = C.PROJECT_ROOT / C.OFFICIAL_POPULATED_DATA_DIR
    p.mkdir(parents=True, exist_ok=True)
    return p


def _reports_dir() -> Path:
    p = C.PROJECT_ROOT / C.OFFICIAL_POPULATED_REPORTS_DIR
    p.mkdir(parents=True, exist_ok=True)
    return p


def _read_file(path: str) -> pd.DataFrame:
    p = Path(path)
    if p.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(p)
    return pd.read_csv(p)


def _col_map(df: pd.DataFrame) -> dict[str, str]:
    lower = {c.lower().strip(): c for c in df.columns}
    mapping = {}
    aliases = {
        "match_number": ["match number", "match_number", "match no", "matchno", "no"],
        "match_id": ["match id", "match_id"],
        "date": ["date", "match date"],
        "time": ["time", "kickoff", "kickoff local", "kickoff_local"],
        "group": ["group"],
        "stage": ["stage", "round"],
        "venue": ["venue"],
        "stadium": ["stadium"],
        "city": ["city", "host city"],
        "country": ["country", "host country"],
        "team_a": ["team a", "team_a", "home", "home team"],
        "team_b": ["team b", "team_b", "away", "away team"],
        "match": ["match"],
    }
    for key, opts in aliases.items():
        for opt in opts:
            if opt in lower:
                mapping[key] = lower[opt]
                break
    return mapping


def normalize_schedule_to_official_schema(schedule_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Normalize schedule file to fixtures + venues + audit."""
    cmap = _col_map(schedule_df)
    audits: list[dict] = []
    fixtures: list[dict] = []
    venues: dict[str, dict] = {}

    for idx, row in schedule_df.iterrows():
        team_a = team_b = ""
        if "match" in cmap and pd.notna(row.get(cmap["match"], "")):
            m = str(row[cmap["match"]])
            if " vs " in m.lower():
                parts = re_split_vs(m)
                team_a, team_b = parts[0], parts[1]
        if "team_a" in cmap:
            team_a = normalize_fifa_team_name(str(row.get(cmap["team_a"], team_a)))
        if "team_b" in cmap:
            team_b = normalize_fifa_team_name(str(row.get(cmap["team_b"], team_b)))

        match_num = row.get(cmap.get("match_number", ""), idx + 1)
        try:
            match_num = int(match_num)
        except (TypeError, ValueError):
            match_num = idx + 1

        stadium = str(row.get(cmap.get("stadium", ""), "") or row.get(cmap.get("venue", ""), "")).strip()
        city = str(row.get(cmap.get("city", ""), "")).strip()
        country = str(row.get(cmap.get("country", ""), "")).strip()
        group = str(row.get(cmap.get("group", ""), "")).strip()
        stage = str(row.get(cmap.get("stage", ""), "")).strip() or (
            "Group Stage" if match_num <= C.OFFICIAL_GROUP_STAGE_MATCHES else "Knockout"
        )
        date_val = str(row.get(cmap.get("date", ""), "")).strip()
        kickoff = str(row.get(cmap.get("time", ""), "")).strip()

        fixtures.append(
            {
                "match_id": f"wc2026_m{match_num:03d}",
                "match_number": match_num,
                "stage": stage,
                "group": group,
                "date": date_val,
                "kickoff_local": kickoff,
                "kickoff_utc": "",
                "timezone": "",
                "venue": stadium,
                "stadium": stadium,
                "city": city,
                "country": country,
                "team_a": team_a,
                "team_b": team_b,
                "team_a_code": "",
                "team_b_code": "",
                "team_a_group_slot": "",
                "team_b_group_slot": "",
                "status": "scheduled",
                "source": "fifa_downloadable_schedule",
            }
        )
        if stadium and stadium not in venues:
            vid = re_sub_slug(stadium)
            venues[stadium] = {
                "venue_id": f"v_{vid}",
                "stadium": stadium,
                "venue": stadium,
                "city": city,
                "country": country,
                "timezone": "",
                "capacity": "",
                "latitude": "",
                "longitude": "",
                "source": "fifa_downloadable_schedule",
            }

    fdf = pd.DataFrame(fixtures, columns=C.IMPORT_FIXTURES_REQUIRED_COLUMNS)
    vdf = pd.DataFrame(list(venues.values()), columns=C.IMPORT_VENUES_REQUIRED_COLUMNS)
    status = "parsed" if len(fdf) >= C.OFFICIAL_TOTAL_MATCHES else "partial"
    audits.append(make_source_audit_row("fixtures", "fifa_downloadable_schedule", status, len(fdf)))
    return fdf, vdf, pd.DataFrame(audits)


def re_split_vs(m: str) -> tuple[str, str]:
    import re

    parts = re.split(r"\s+vs\s+", m, flags=re.I)
    if len(parts) == 2:
        return normalize_fifa_team_name(parts[0]), normalize_fifa_team_name(parts[1])
    return "", ""


def re_sub_slug(s: str) -> str:
    import re

    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:32] or "venue"


def load_fifa_downloadable_schedule(path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load and normalize FIFA schedule CSV/XLSX."""
    df = _read_file(path)
    fixtures_df, venues_df, _ = normalize_schedule_to_official_schema(df)
    return fixtures_df, venues_df


def save_populated_schedule_outputs(
    fixtures_df: pd.DataFrame,
    venues_df: pd.DataFrame,
    audit_df: pd.DataFrame,
) -> dict[str, Any]:
    """Save populated fixtures, venues, and audit."""
    out_dir = _populated_dir()
    rep_dir = _reports_dir()
    fpath = out_dir / C.POPULATED_OFFICIAL_FIXTURES_FILE
    vpath = out_dir / C.POPULATED_OFFICIAL_VENUES_FILE
    fixtures_df.to_csv(fpath, index=False)
    venues_df.to_csv(vpath, index=False)
    audit_path = rep_dir / C.OFFICIAL_POPULATION_SOURCE_AUDIT_FILE
    if audit_path.is_file() and not audit_df.empty:
        audit_df = pd.concat([pd.read_csv(audit_path), audit_df], ignore_index=True)
    if not audit_df.empty:
        audit_df.to_csv(audit_path, index=False)
    return {"fixtures_path": str(fpath), "venues_path": str(vpath), "audit_path": str(audit_path)}
