"""Tests for official_final promotion gate."""

from __future__ import annotations

from pathlib import Path

from src.official.promotion import (
    demote_from_official_final,
    load_official_final_mode,
    promote_to_official_final,
)


def test_promote_without_confirmation_returns_confirmation_required():
    result = promote_to_official_final(confirmed=False)
    assert result["status"] == "confirmation_required"
    assert result["official_final_enabled"] is False


def test_promote_blocks_when_readiness_false(tmp_path, monkeypatch):
    flag_path = tmp_path / "official_final_mode.json"
    monkeypatch.setattr("src.official.promotion._flag_path", lambda: flag_path)
    monkeypatch.setattr(
        "src.official.promotion.can_promote_to_official_final",
        lambda: (False, {"is_official_final_ready": False, "blocker_count": 3}),
    )

    result = promote_to_official_final(confirmed=True)
    assert result["status"] == "blocked"
    assert result["official_final_enabled"] is False


def test_demote_from_official_final_disables_flag(tmp_path, monkeypatch):
    flag_path = tmp_path / "official_final_mode.json"
    monkeypatch.setattr("src.official.promotion._flag_path", lambda: flag_path)

    result = demote_from_official_final(reason="test demote")
    assert result["status"] == "demoted"
    assert result["official_final_enabled"] is False

    loaded = load_official_final_mode()
    assert loaded["official_final_enabled"] is False


def test_load_official_final_mode_returns_false_if_missing(tmp_path, monkeypatch):
    flag_path = tmp_path / "missing_flag.json"
    monkeypatch.setattr("src.official.promotion._flag_path", lambda: flag_path)

    loaded = load_official_final_mode()
    assert loaded["official_final_enabled"] is False
