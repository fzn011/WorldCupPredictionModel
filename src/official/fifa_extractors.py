"""Official FIFA HTML snapshot extractors for Step 17F."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pandas as pd

import src.utils.constants as C
from src.utils.team_name_mapping import standardize_team_name


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_source_audit_row(
    dataset: str,
    source: str,
    status: str,
    rows_extracted: int,
    warnings: str = "",
    notes: str = "",
) -> dict[str, Any]:
    return {
        "dataset": dataset,
        "source": source,
        "status": status,
        "rows_extracted": rows_extracted,
        "warnings": warnings,
        "notes": notes,
        "extracted_at": _now(),
    }


def normalize_fifa_team_name(raw_name: str) -> str:
    """Normalize FIFA display names to project canonical team names."""
    if not raw_name or not str(raw_name).strip():
        return ""
    name = str(raw_name).strip()
    if name in C.FIFA_TEAM_NAME_ALIASES:
        name = C.FIFA_TEAM_NAME_ALIASES[name]
    return standardize_team_name(name)


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


def _audit_df(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=[
        "dataset", "source", "status", "rows_extracted", "warnings", "notes", "extracted_at",
    ])


def extract_teams_from_fifa_snapshot(html_path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Parse saved FIFA teams page; returns (teams_df, audit_df)."""
    html = _read_html(html_path)
    audits: list[dict] = []
    if not html:
        audits.append(make_source_audit_row("teams", "fifa_teams_page", "failed", 0, notes="Missing snapshot"))
        return pd.DataFrame(columns=C.IMPORT_TEAMS_REQUIRED_COLUMNS), _audit_df(audits)

    names: list[str] = []
    soup = _soup(html)
    if soup is not None:
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            if "/teams/" in href or "team" in href.lower():
                text = normalize_fifa_team_name(a.get_text(strip=True))
                if text and 2 < len(text) < 50:
                    names.append(text)
        for tag in soup.find_all(["span", "div", "h2", "h3"]):
            text = normalize_fifa_team_name(tag.get_text(strip=True))
            if text and re.match(r"^[A-Za-z\u00C0-\u024f\s'\-]{3,40}$", text):
                if text.lower() not in {"teams", "schedule", "news"}:
                    names.append(text)
    else:
        for m in re.findall(r'"teamName"\s*:\s*"([^"]+)"', html):
            names.append(normalize_fifa_team_name(m))

    names = list(dict.fromkeys(n for n in names if n))
    rows = []
    for i, team in enumerate(names[: C.OFFICIAL_REQUIRED_TEAM_COUNT]):
        rows.append(
            {
                "team": team,
                "team_code": "",
                "confederation": "",
                "group": "",
                "group_slot": "",
                "is_host": 0,
                "qualified": 1,
                "source": "fifa_teams_page",
            }
        )

    status = "parsed" if len(rows) >= C.OFFICIAL_REQUIRED_TEAM_COUNT else "partial"
    warn = "" if len(rows) >= C.OFFICIAL_REQUIRED_TEAM_COUNT else "Group/slot may need manual fill"
    audits.append(make_source_audit_row("teams", "fifa_teams_page", status, len(rows), warnings=warn))
    return pd.DataFrame(rows, columns=C.IMPORT_TEAMS_REQUIRED_COLUMNS), _audit_df(audits)


def extract_fixtures_from_fifa_schedule_snapshot(html_path: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Parse schedule/scores snapshot; returns (fixtures_df, venues_df, audit_df)."""
    html = _read_html(html_path)
    audits: list[dict] = []
    empty_f = pd.DataFrame(columns=C.IMPORT_FIXTURES_REQUIRED_COLUMNS)
    empty_v = pd.DataFrame(columns=C.IMPORT_VENUES_REQUIRED_COLUMNS)
    if not html:
        audits.append(make_source_audit_row("fixtures", "fifa_schedule_page", "failed", 0, notes="Missing snapshot"))
        return empty_f, empty_v, _audit_df(audits)

    fixtures: list[dict] = []
    venues: dict[str, dict] = {}
    current_date = ""
    vs_pat = re.compile(r"(.+?)\s+(?:vs|v\.?)\s+(.+)", re.I)
    date_pat = re.compile(
        r"\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+\d{1,2}\s+\w+\s+2026\b",
        re.I,
    )

    lines: list[str] = []
    soup = _soup(html)
    if soup is not None:
        lines = [el.get_text(" ", strip=True) for el in soup.find_all(["li", "tr", "div", "p", "span"])]
    else:
        lines = [ln.strip() for ln in html.splitlines() if ln.strip()]

    for line in lines:
        if date_pat.search(line):
            current_date = date_pat.search(line).group(0)
            continue
        m = vs_pat.search(line)
        if not m:
            continue
        team_a = normalize_fifa_team_name(m.group(1).strip(" -|•"))
        team_b = normalize_fifa_team_name(m.group(2).strip(" -|•"))
        if not team_a or not team_b:
            continue
        n = len(fixtures) + 1
        stage = "Group Stage" if n <= C.OFFICIAL_GROUP_STAGE_MATCHES else "Knockout"
        fixtures.append(
            {
                "match_id": f"wc2026_m{n:03d}",
                "match_number": n,
                "stage": stage,
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

    status = "parsed" if len(fixtures) >= C.OFFICIAL_TOTAL_MATCHES else "partial"
    audits.append(
        make_source_audit_row(
            "fixtures",
            "fifa_schedule_page",
            status,
            len(fixtures),
            warnings="Kickoff/venue may be blank" if fixtures else "No fixtures parsed",
        )
    )
    audits.append(make_source_audit_row("venues", "fifa_schedule_page", "partial", len(venues)))
    return (
        pd.DataFrame(fixtures, columns=C.IMPORT_FIXTURES_REQUIRED_COLUMNS),
        pd.DataFrame(list(venues.values()), columns=C.IMPORT_VENUES_REQUIRED_COLUMNS),
        _audit_df(audits),
    )


def extract_squad_links_from_fifa_snapshot(html_path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Extract squad announcement links from FIFA hub page."""
    html = _read_html(html_path)
    audits: list[dict] = []
    if not html:
        audits.append(make_source_audit_row("squads", "fifa_squad_announcements_page", "failed", 0))
        return pd.DataFrame(columns=["team", "squad_url", "status", "source"]), _audit_df(audits)

    rows = []
    soup = _soup(html)
    if soup is not None:
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "fifa.com" not in href and not href.startswith("/"):
                continue
            if "squad" in href.lower() or "team" in href.lower():
                team = normalize_fifa_team_name(a.get_text(strip=True))
                if team:
                    url = href if href.startswith("http") else f"https://www.fifa.com{href}"
                    if urlparse(url).netloc.replace("www.", "").endswith("fifa.com"):
                        rows.append(
                            {
                                "team": team,
                                "squad_url": url,
                                "status": "link_found",
                                "source": "fifa_squad_announcements_page",
                            }
                        )

    rows = list({(r["team"], r["squad_url"]): r for r in rows}.values())
    status = "parsed" if rows else "needs_manual_review"
    audits.append(make_source_audit_row("squads", "fifa_squad_announcements_page", status, len(rows)))
    return pd.DataFrame(rows), _audit_df(audits)


def extract_players_from_fifa_squad_article_snapshot(html_path: str, team: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Parse saved individual FIFA squad article if structured tables exist."""
    html = _read_html(html_path)
    audits: list[dict] = []
    team_norm = normalize_fifa_team_name(team)
    if not html:
        audits.append(make_source_audit_row("players", "fifa_squad_article", "failed", 0, notes=f"No snapshot for {team_norm}"))
        return pd.DataFrame(columns=C.IMPORT_PLAYERS_REQUIRED_COLUMNS), _audit_df(audits)

    players: list[dict] = []
    soup = _soup(html)
    if soup is not None:
        for table in soup.find_all("table"):
            headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
            for tr in table.find_all("tr")[1:]:
                cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                if not cells:
                    continue
                pname = cells[0]
                for i, h in enumerate(headers):
                    if "player" in h or "name" in h:
                        pname = cells[i] if i < len(cells) else pname
                if pname:
                    players.append(
                        {
                            "player_id": f"p_{len(players)+1:05d}",
                            "team": team_norm,
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
                            "source": "fifa_squad_article",
                        }
                    )

    status = "parsed" if players else "needs_manual_review"
    msg = "" if players else "No player table in squad article; use squad CSV import"
    audits.append(make_source_audit_row("players", "fifa_squad_article", status, len(players), warnings=msg))
    return pd.DataFrame(players, columns=C.IMPORT_PLAYERS_REQUIRED_COLUMNS), _audit_df(audits)
