"""Tests for Step 17E FIFA source parsers."""

from __future__ import annotations

from pathlib import Path

from src.official.source_parsers import (
    parse_fifa_schedule_snapshot,
    parse_fifa_squad_announcements_snapshot,
    parse_fifa_teams_snapshot,
)


def test_parse_fifa_teams_snapshot_handles_small_synthetic_html(tmp_path):
    html = tmp_path / "teams.html"
    html.write_text(
        '<html><body><a>Argentina</a><a>Brazil</a><a>France</a></body></html>',
        encoding="utf-8",
    )
    teams_df, report = parse_fifa_teams_snapshot(str(html))
    assert len(teams_df) >= 1
    assert not report.empty


def test_parse_fifa_schedule_snapshot_handles_fixture_html(tmp_path):
    html = tmp_path / "schedule.html"
    html.write_text(
        "<html><body><div>Argentina vs France</div><div>Brazil v Germany</div></body></html>",
        encoding="utf-8",
    )
    fixtures_df, venues_df, report = parse_fifa_schedule_snapshot(str(html))
    assert len(fixtures_df) >= 1
    assert not report.empty


def test_parse_fifa_squad_announcements_returns_empty_with_warning(tmp_path):
    html = tmp_path / "squads.html"
    html.write_text("<html><body><p>Squad announcements hub</p></body></html>", encoding="utf-8")
    players_df, report = parse_fifa_squad_announcements_snapshot(str(html))
    assert players_df.empty
    assert report.iloc[0]["status"] == "needs_manual_review"
