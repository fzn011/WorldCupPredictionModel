"""Tests for unified product data status UI helper."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_product_status_merges_fixtures_from_official_summary(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    processed = tmp_path / "official" / "processed"
    processed.mkdir(parents=True)

    (processed / "official_data_summary.json").write_text(
        json.dumps(
            {
                "teams_count": 48,
                "fixtures_count": 104,
                "players_count": 1248,
                "teams_with_26_players": 48,
            }
        ),
        encoding="utf-8",
    )
    (processed / "official_final_mode.json").write_text(
        json.dumps({"official_final_enabled": True}),
        encoding="utf-8",
    )

    monkeypatch.setattr("app.product_status.OFFICIAL_PROCESSED_DIR", processed)

    readiness = {
        "is_official_final_ready": True,
        "summary": {
            "teams_count": 48,
            "players_count": 1248,
            "teams_with_26_players": 48,
        },
    }

    with patch("src.official.final_readiness.evaluate_official_final_readiness", return_value=readiness):
        from app.product_status import load_product_data_status

        status = load_product_data_status()

    assert status["fixtures_count"] == 104
    assert status["data_label"] == "Ready"
    assert status["verification_label"] == "Verified"
    assert status["is_verified"] is True
    assert status["awards_allowed"] is True


def test_product_status_needs_review_when_counts_incomplete(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    processed = tmp_path / "official" / "processed"
    processed.mkdir(parents=True)

    (processed / "official_data_summary.json").write_text(
        json.dumps({"teams_count": 10, "fixtures_count": 0, "players_count": 100}),
        encoding="utf-8",
    )
    (processed / "official_final_mode.json").write_text(
        json.dumps({"official_final_enabled": False}),
        encoding="utf-8",
    )

    monkeypatch.setattr("app.product_status.OFFICIAL_PROCESSED_DIR", processed)

    with patch(
        "src.official.final_readiness.evaluate_official_final_readiness",
        return_value={"is_official_final_ready": False, "summary": {}},
    ):
        from app.product_status import load_product_data_status

        status = load_product_data_status()

    assert status["data_label"] == "Needs review"
    assert status["verification_label"] == "Needs review"
    assert status["is_verified"] is False
    assert status["awards_allowed"] is False
    assert status["awards_blocker"]


def test_awards_allowed_requires_promotion_and_readiness(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    processed = tmp_path / "official" / "processed"
    processed.mkdir(parents=True)

    (processed / "official_data_summary.json").write_text(
        json.dumps(
            {
                "teams_count": 48,
                "fixtures_count": 104,
                "players_count": 1248,
                "teams_with_26_players": 48,
            }
        ),
        encoding="utf-8",
    )
    (processed / "official_final_mode.json").write_text(
        json.dumps({"official_final_enabled": False}),
        encoding="utf-8",
    )

    monkeypatch.setattr("app.product_status.OFFICIAL_PROCESSED_DIR", processed)

    with patch(
        "src.official.final_readiness.evaluate_official_final_readiness",
        return_value={"is_official_final_ready": True, "summary": {"teams_count": 48}},
    ):
        from app.product_status import load_product_data_status

        status = load_product_data_status()

    assert status["awards_allowed"] is False
    assert "Promote" in (status.get("awards_blocker") or "")
