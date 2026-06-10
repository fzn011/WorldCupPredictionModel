"""FIFA squad CSV/XLSX importer for Step 17F."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C
from src.official.fifa_extractors import make_source_audit_row, normalize_fifa_team_name

POSITION_MAP = {
    "GK": "GK", "G": "GK", "GOALKEEPER": "GK",
    "DF": "DF", "D": "DF", "DEF": "DF", "DEFENDER": "DF",
    "MF": "MF", "M": "MF", "MID": "MF", "MIDFIELDER": "MF",
    "FW": "FW", "F": "FW", "ATT": "FW", "FORWARD": "FW", "ST": "FW",
}


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


def _col(df: pd.DataFrame, *names: str) -> str | None:
    lower = {c.lower().strip(): c for c in df.columns}
    for n in names:
        if n.lower() in lower:
            return lower[n.lower()]
    return None


def _age_at_tournament(dob: str) -> str:
    if not dob or str(dob).strip() in {"", "nan", "NaT"}:
        return ""
    try:
        dt = pd.to_datetime(dob, errors="coerce")
        if pd.isna(dt):
            return ""
        start = datetime(2026, 6, 11)
        age = start.year - dt.year - ((start.month, start.day) < (dt.month, dt.day))
        return str(age)
    except Exception:
        return ""


def normalize_squad_to_official_schema(squad_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Normalize squad file to official_players schema."""
    rows = []
    for idx, row in squad_df.iterrows():
        team_col = _col(squad_df, "team", "country", "nation")
        team = normalize_fifa_team_name(str(row.get(team_col, ""))) if team_col else ""
        pname_col = _col(squad_df, "player_name", "player", "name")
        pname = str(row.get(pname_col, "")).strip() if pname_col else ""
        if not pname:
            continue
        pos_col = _col(squad_df, "position_code", "pos", "position")
        pos_raw = str(row.get(pos_col, "")).strip().upper() if pos_col else ""
        pos_code = POSITION_MAP.get(pos_raw[:2] if len(pos_raw) >= 2 else pos_raw, pos_raw[:2] if pos_raw else "")
        shirt_col = _col(squad_df, "shirt_number", "no", "number", "shirt")
        dob_col = _col(squad_df, "date_of_birth", "dob", "birth_date")
        dob = str(row.get(dob_col, "")).strip() if dob_col else ""
        club_col = _col(squad_df, "club", "club_name")
        height_col = _col(squad_df, "height_cm", "height")
        tc = _col(squad_df, "team_code", "code")
        rows.append(
            {
                "player_id": f"p_{idx+1:05d}",
                "team": team,
                "team_code": str(row.get(tc, "")).strip() if tc else "",
                "shirt_number": row.get(shirt_col, "") if shirt_col else "",
                "position_code": pos_code,
                "position": pos_code,
                "player_name": pname,
                "first_names": "",
                "last_names": "",
                "name_on_shirt": pname,
                "date_of_birth": dob,
                "age_at_tournament_start": _age_at_tournament(dob),
                "club": str(row.get(club_col, "")).strip() if club_col else "",
                "club_country": "",
                "height_cm": row.get(height_col, "") if height_col else "",
                "source": "fifa_squad_file",
            }
        )
    pdf = pd.DataFrame(rows, columns=C.IMPORT_PLAYERS_REQUIRED_COLUMNS)
    status = "parsed" if len(pdf) >= C.OFFICIAL_REQUIRED_TOTAL_PLAYERS else "partial"
    audit = pd.DataFrame(
        [make_source_audit_row("players", "fifa_squad_file", status, len(pdf))]
    )
    return pdf, audit


def load_fifa_squad_csv_or_xlsx(path: str) -> pd.DataFrame:
    df = _read_file(path)
    players_df, _ = normalize_squad_to_official_schema(df)
    return players_df


def validate_imported_squad_completeness(
    players_df: pd.DataFrame,
    teams_df: pd.DataFrame | None = None,
) -> tuple[bool, pd.DataFrame]:
    """Check squad completeness against 1248 / 48×26 targets."""
    rows = []
    n = len(players_df)
    target = C.OFFICIAL_REQUIRED_TOTAL_PLAYERS
    rows.append({"check": "player_count", "expected": target, "actual": n, "passed": n == target})
    teams = players_df["team"].nunique() if not players_df.empty and "team" in players_df.columns else 0
    rows.append({"check": "team_count", "expected": 48, "actual": teams, "passed": teams == 48})
    per_team = players_df.groupby("team").size() if not players_df.empty else pd.Series(dtype=int)
    bad = (per_team != C.OFFICIAL_REQUIRED_PLAYERS_PER_TEAM).sum() if len(per_team) else 48
    rows.append(
        {
            "check": "players_per_team",
            "expected": 26,
            "actual": f"{48 - bad}/48 teams at 26",
            "passed": bad == 0 and teams == 48,
        }
    )
    report = pd.DataFrame(rows)
    return bool(report["passed"].all()), report


def save_populated_squad_outputs(players_df: pd.DataFrame, audit_df: pd.DataFrame) -> dict[str, Any]:
    out_dir = _populated_dir()
    rep_dir = _reports_dir()
    ppath = out_dir / C.POPULATED_OFFICIAL_PLAYERS_FILE
    players_df.to_csv(ppath, index=False)
    audit_path = rep_dir / C.OFFICIAL_POPULATION_SOURCE_AUDIT_FILE
    if audit_path.is_file() and not audit_df.empty:
        audit_df = pd.concat([pd.read_csv(audit_path), audit_df], ignore_index=True)
    if not audit_df.empty:
        audit_df.to_csv(audit_path, index=False)
    return {"players_path": str(ppath), "audit_path": str(audit_path)}
