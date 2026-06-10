"""Tests for Step 17F FIFA HTML extractors."""

from __future__ import annotations

from pathlib import Path

from src.official.fifa_extractors import (
    extract_fixtures_from_fifa_schedule_snapshot,
    extract_players_from_fifa_squad_article_snapshot,
    extract_squad_links_from_fifa_snapshot,
    extract_teams_from_fifa_snapshot,
    normalize_fifa_team_name,
)


def test_normalize_fifa_team_name_aliases():
    assert normalize_fifa_team_name("Korea Republic") == "South Korea"
    assert normalize_fifa_team_name("USA") == "United States"


def test_extract_teams_from_fifa_snapshot(tmp_path):
    html = """
    <html><body>
    <a href="/teams/mexico">Mexico</a>
    <a href="/teams/brazil">Brazil</a>
    <span>Argentina</span>
    </body></html>
    """
    path = tmp_path / "teams.html"
    path.write_text(html, encoding="utf-8")
    teams_df, audit_df = extract_teams_from_fifa_snapshot(str(path))
    assert not teams_df.empty
    assert "Mexico" in teams_df["team"].values
    assert not audit_df.empty


def test_extract_fixtures_from_fifa_schedule_snapshot(tmp_path):
    html = """
    <html><body>
    <div>Thursday, 11 June 2026</div>
    <li>Mexico vs South Africa</li>
    <li>Brazil v Argentina</li>
    </body></html>
    """
    path = tmp_path / "schedule.html"
    path.write_text(html, encoding="utf-8")
    fixtures_df, venues_df, audit_df = extract_fixtures_from_fifa_schedule_snapshot(str(path))
    assert len(fixtures_df) >= 2
    assert fixtures_df.iloc[0]["team_a"] == "Mexico"
    assert not audit_df.empty


def test_extract_squad_links_from_fifa_snapshot(tmp_path):
    html = """
    <html><body>
    <a href="https://www.fifa.com/en/articles/mexico-squad">Mexico squad</a>
    </body></html>
    """
    path = tmp_path / "squads.html"
    path.write_text(html, encoding="utf-8")
    links_df, audit_df = extract_squad_links_from_fifa_snapshot(str(path))
    assert not links_df.empty
    assert "squad" in links_df.iloc[0]["squad_url"].lower()


def test_extract_players_from_fifa_squad_article_snapshot(tmp_path):
    html = """
    <html><body>
    <table>
    <tr><th>Player</th><th>Pos</th></tr>
    <tr><td>Lionel Messi</td><td>FW</td></tr>
    <tr><td>Emiliano Martinez</td><td>GK</td></tr>
    </table>
    </body></html>
    """
    path = tmp_path / "arg_squad.html"
    path.write_text(html, encoding="utf-8")
    players_df, audit_df = extract_players_from_fifa_squad_article_snapshot(str(path), "Argentina")
    assert len(players_df) == 2
    assert "Lionel Messi" in players_df["player_name"].values
