"""Defensive parsers for official FIFA source snapshots (Step 17E)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C

NOW_ISO = lambda: datetime.now(timezone.utc).isoformat()  # noqa: E731


def _parse_report_row(source: str, entity: str, status: str, message: str, count: int = 0) -> dict:
    return {
        "source": source,
        "entity": entity,
        "status": status,
        "message": message,
        "rows_extracted": count,
        "parsed_at": NOW_ISO(),
    }


def _read_html(html_path: str) -> str:
    path = Path(html_path)
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _soup(html: str):
    try:
        from bs4 import BeautifulSoup

        return BeautifulSoup(html, "html.parser")
    except ImportError:
        return None


def _slug_team_id(name: str, idx: int) -> str:
    clean = re.sub(r"[^a-zA-Z0-9]+", "_", name.strip()).strip("_").lower()
    return f"team_{clean or idx:03d}"


def teams_to_groups_df(teams_df: pd.DataFrame) -> pd.DataFrame:
    """Derive groups import rows from staged teams."""
    if teams_df.empty:
        return pd.DataFrame(columns=C.IMPORT_GROUPS_REQUIRED_COLUMNS)
    rows = []
    for _, row in teams_df.iterrows():
        group = str(row.get("group", "")).strip()
        slot = row.get("group_slot", row.get("slot", ""))
        team = str(row.get("team", "")).strip()
        if not team:
            continue
        rows.append(
            {
                "group": group,
                "slot": slot,
                "team": team,
                "team_code": row.get("team_code", ""),
                "confederation": row.get("confederation", ""),
                "is_host": row.get("is_host", 0),
                "source": row.get("source", "fifa_teams_page"),
            }
        )
    return pd.DataFrame(rows, columns=C.IMPORT_GROUPS_REQUIRED_COLUMNS)


def parse_fifa_teams_snapshot(html_path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Parse teams page snapshot; returns (teams_df, parse_report_df)."""
    reports = []
    html = _read_html(html_path)
    if not html:
        reports.append(_parse_report_row("teams", "teams", "failed", "HTML snapshot missing", 0))
        return pd.DataFrame(columns=C.IMPORT_TEAMS_REQUIRED_COLUMNS), pd.DataFrame(reports)

    team_names: list[str] = []
    soup = _soup(html)
    if soup is not None:
        for tag in soup.find_all(["a", "span", "div", "h2", "h3", "p"]):
            text = tag.get_text(strip=True)
            if not text or len(text) > 60:
                continue
            if re.match(r"^[A-Z][a-zA-Z\s'\u00C0-\u024f\u0100-\u017f-]{2,40}$", text):
                if text.lower() not in {"teams", "schedule", "news", "tickets", "shop"}:
                    team_names.append(text)
    else:
        for match in re.findall(r'data-team-name="([^"]+)"', html):
            team_names.append(match.strip())
        for match in re.findall(r'"teamName"\s*:\s*"([^"]+)"', html):
            team_names.append(match.strip())

    team_names = list(dict.fromkeys(t for t in team_names if t))
    rows = []
    for i, name in enumerate(team_names[: C.OFFICIAL_REQUIRED_TEAM_COUNT]):
        rows.append(
            {
                "team": name,
                "team_code": "",
                "confederation": "",
                "group": "",
                "group_slot": "",
                "is_host": 0,
                "qualified": 1,
                "source": "fifa_teams_page",
            }
        )

    teams_df = pd.DataFrame(rows, columns=C.IMPORT_TEAMS_REQUIRED_COLUMNS)
    status = "parsed" if len(rows) >= C.OFFICIAL_REQUIRED_TEAM_COUNT else "partial"
    msg = (
        f"Extracted {len(rows)} team names from teams page."
        if rows
        else "No structured team names found; use manual workbook import."
    )
    if len(rows) < C.OFFICIAL_REQUIRED_TEAM_COUNT:
        msg += " Group/slot fields may need manual review."
    reports.append(_parse_report_row("teams", "teams", status, msg, len(rows)))
    return teams_df, pd.DataFrame(reports)


def parse_fifa_schedule_snapshot(html_path: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Parse schedule snapshot; returns (fixtures_df, venues_df, parse_report_df)."""
    reports = []
    html = _read_html(html_path)
    empty_fixtures = pd.DataFrame(columns=C.IMPORT_FIXTURES_REQUIRED_COLUMNS)
    empty_venues = pd.DataFrame(columns=C.IMPORT_VENUES_REQUIRED_COLUMNS)

    if not html:
        reports.append(_parse_report_row("schedule", "fixtures", "failed", "HTML snapshot missing", 0))
        return empty_fixtures, empty_venues, pd.DataFrame(reports)

    fixtures_rows: list[dict[str, Any]] = []
    venues_seen: dict[str, dict] = {}
    current_date = ""

    soup = _soup(html)
    lines: list[str] = []
    if soup is not None:
        lines = [el.get_text(" ", strip=True) for el in soup.find_all(["li", "tr", "div", "p"])]
    else:
        lines = [ln.strip() for ln in html.splitlines() if ln.strip()]

    date_pattern = re.compile(
        r"\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+"
        r"\d{1,2}\s+\w+\s+2026\b",
        re.I,
    )
    vs_pattern = re.compile(r"(.+?)\s+(?:vs|v\.?)\s+(.+)", re.I)

    for line in lines:
        if not line:
            continue
        if date_pattern.search(line):
            current_date = date_pattern.search(line).group(0)
            continue
        m = vs_pattern.search(line)
        if m:
            team_a = m.group(1).strip(" -•|")
            team_b = m.group(2).strip(" -•|")
            if len(team_a) < 2 or len(team_b) < 2:
                continue
            match_num = len(fixtures_rows) + 1
            fixtures_rows.append(
                {
                    "match_id": f"wc2026_m{match_num:03d}",
                    "match_number": match_num,
                    "stage": "Group Stage" if match_num <= C.OFFICIAL_GROUP_STAGE_MATCHES else "Knockout",
                    "group": "",
                    "date": current_date,
                    "kickoff_local": "",
                    "kickoff_utc": "",
                    "timezone": "",
                    "venue": "",
                    "stadium": "",
                    "city": "",
                    "country": "",
                    "team_a": team_a,
                    "team_b": team_b,
                    "team_a_code": "",
                    "team_b_code": "",
                    "team_a_group_slot": "",
                    "team_b_group_slot": "",
                    "status": "scheduled",
                    "source": "fifa_schedule_page",
                }
            )

    for row in fixtures_rows:
        stadium = str(row.get("stadium", "")).strip()
        city = str(row.get("city", "")).strip()
        if stadium and stadium not in venues_seen:
            vid = re.sub(r"[^a-z0-9]+", "_", stadium.lower()).strip("_")[:32]
            venues_seen[stadium] = {
                "venue_id": f"v_{vid or len(venues_seen)+1}",
                "stadium": stadium,
                "venue": stadium,
                "city": city,
                "country": row.get("country", ""),
                "timezone": "",
                "capacity": "",
                "latitude": "",
                "longitude": "",
                "source": "fifa_schedule_page",
            }

    fixtures_df = pd.DataFrame(fixtures_rows, columns=C.IMPORT_FIXTURES_REQUIRED_COLUMNS)
    venues_df = pd.DataFrame(list(venues_seen.values()), columns=C.IMPORT_VENUES_REQUIRED_COLUMNS)

    f_status = "parsed" if len(fixtures_rows) >= C.OFFICIAL_TOTAL_MATCHES else "partial"
    f_msg = (
        f"Extracted {len(fixtures_rows)} fixture lines; kickoff/venue may need manual fill."
        if fixtures_rows
        else "No fixture lines parsed; use manual schedule import."
    )
    reports.append(_parse_report_row("schedule", "fixtures", f_status, f_msg, len(fixtures_rows)))
    reports.append(
        _parse_report_row(
            "schedule",
            "venues",
            "partial" if venues_df.empty else "parsed",
            f"Extracted {len(venues_df)} venue hints from schedule page.",
            len(venues_df),
        )
    )
    return fixtures_df, venues_df, pd.DataFrame(reports)


def parse_fifa_squad_announcements_snapshot(html_path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Parse squad announcements hub; may return empty players if tables absent."""
    reports = []
    html = _read_html(html_path)
    empty = pd.DataFrame(columns=C.IMPORT_PLAYERS_REQUIRED_COLUMNS)

    if not html:
        reports.append(_parse_report_row("squads", "players", "failed", "HTML snapshot missing", 0))
        return empty, pd.DataFrame(reports)

    players: list[dict] = []
    soup = _soup(html)
    if soup is not None:
        for table in soup.find_all("table"):
            headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
            if not headers:
                continue
            name_idx = next((i for i, h in enumerate(headers) if "player" in h or "name" in h), None)
            team_idx = next((i for i, h in enumerate(headers) if "team" in h or "country" in h), None)
            for tr in table.find_all("tr")[1:]:
                cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                if not cells:
                    continue
                pname = cells[name_idx] if name_idx is not None and name_idx < len(cells) else ""
                team = cells[team_idx] if team_idx is not None and team_idx < len(cells) else ""
                if pname:
                    players.append(
                        {
                            "player_id": f"p_{len(players)+1:05d}",
                            "team": team,
                            "team_code": "",
                            "shirt_number": "",
                            "position_code": "",
                            "position": "",
                            "player_name": pname,
                            "first_names": "",
                            "last_names": "",
                            "name_on_shirt": pname,
                            "date_of_birth": "",
                            "age_at_tournament_start": "",
                            "club": "",
                            "club_country": "",
                            "height_cm": "",
                            "source": "fifa_squad_announcements_page",
                        }
                    )

    status = "parsed" if players else "needs_manual_review"
    msg = (
        f"Extracted {len(players)} player rows from squad announcements page."
        if players
        else "No embedded squad tables found; manual squad CSV/workbook import required."
    )
    reports.append(_parse_report_row("squads", "players", status, msg, len(players)))
    return pd.DataFrame(players, columns=C.IMPORT_PLAYERS_REQUIRED_COLUMNS), pd.DataFrame(reports)


def _staging_dir() -> Path:
    p = C.PROJECT_ROOT / C.OFFICIAL_SOURCE_STAGING_DIR
    p.mkdir(parents=True, exist_ok=True)
    return p


def _reports_dir() -> Path:
    p = C.PROJECT_ROOT / C.OFFICIAL_SOURCE_REPORTS_DIR
    p.mkdir(parents=True, exist_ok=True)
    return p


def parse_all_source_snapshots() -> dict[str, Any]:
    """Load raw snapshots and write staged CSVs + parse report."""
    raw_dir = C.PROJECT_ROOT / C.OFFICIAL_SOURCE_RAW_DIR
    staging = _staging_dir()
    all_reports: list[pd.DataFrame] = []

    teams_path = raw_dir / "teams.html"
    teams_df, tr = parse_fifa_teams_snapshot(str(teams_path))
    all_reports.append(tr)

    groups_df = teams_to_groups_df(teams_df)

    schedule_path = raw_dir / "schedule.html"
    scores_path = raw_dir / "scores_fixtures.html"
    sched_fix, sched_ven, sr = parse_fifa_schedule_snapshot(str(schedule_path))
    if sched_fix.empty and scores_path.is_file():
        sched_fix, sched_ven, sr2 = parse_fifa_schedule_snapshot(str(scores_path))
        all_reports.append(sr2)
    else:
        all_reports.append(sr)

    squads_path = raw_dir / "squad_announcements.html"
    players_df, pr = parse_fifa_squad_announcements_snapshot(str(squads_path))
    all_reports.append(pr)

    outputs: dict[str, str] = {}
    if not teams_df.empty:
        p = staging / C.STAGED_OFFICIAL_TEAMS_FILE
        teams_df.to_csv(p, index=False)
        outputs["teams"] = str(p)
    if not groups_df.empty:
        p = staging / C.STAGED_OFFICIAL_GROUPS_FILE
        groups_df.to_csv(p, index=False)
        outputs["groups"] = str(p)
    if not sched_fix.empty:
        p = staging / C.STAGED_OFFICIAL_FIXTURES_FILE
        sched_fix.to_csv(p, index=False)
        outputs["fixtures"] = str(p)
    if not sched_ven.empty:
        p = staging / C.STAGED_OFFICIAL_VENUES_FILE
        sched_ven.to_csv(p, index=False)
        outputs["venues"] = str(p)
    if not players_df.empty:
        p = staging / C.STAGED_OFFICIAL_PLAYERS_FILE
        players_df.to_csv(p, index=False)
        outputs["players"] = str(p)

    parse_report = pd.concat(all_reports, ignore_index=True) if all_reports else pd.DataFrame()
    report_path = _reports_dir() / C.OFFICIAL_SOURCE_PARSE_REPORT_FILE
    parse_report.to_csv(report_path, index=False)

    return {
        "staged_paths": outputs,
        "parse_report_path": str(report_path),
        "staged_teams_count": len(teams_df),
        "staged_groups_count": len(groups_df),
        "staged_fixtures_count": len(sched_fix),
        "staged_venues_count": len(sched_ven),
        "staged_players_count": len(players_df),
        "parse_warnings_count": int((parse_report["status"] != "parsed").sum()) if not parse_report.empty else 0,
    }


def build_source_coverage_report(staged_counts: dict[str, int]) -> pd.DataFrame:
    """Compare staged counts to official targets."""
    targets = {
        "teams": C.OFFICIAL_REQUIRED_TEAM_COUNT,
        "groups": C.OFFICIAL_REQUIRED_TEAM_COUNT,
        "fixtures": C.OFFICIAL_TOTAL_MATCHES,
        "venues": 16,
        "players": C.OFFICIAL_REQUIRED_TOTAL_PLAYERS,
    }
    rows = []
    for entity, target in targets.items():
        actual = staged_counts.get(entity, 0)
        rows.append(
            {
                "entity": entity,
                "target_count": target,
                "staged_count": actual,
                "coverage_pct": round(100.0 * actual / target, 1) if target else 0.0,
                "complete": actual >= target,
            }
        )
    return pd.DataFrame(rows)
