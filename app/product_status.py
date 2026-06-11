"""Unified product-facing data status (single source of truth for UI)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from app.streamlit_paths import OFFICIAL_PROCESSED_DIR
except ModuleNotFoundError:
    from streamlit_paths import OFFICIAL_PROCESSED_DIR

import src.utils.constants as C


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_product_data_status(*, refresh_readiness: bool = False) -> dict[str, Any]:
    """Merge official summary, final mode, and readiness into one UI status dict."""
    official_summary = _read_json(
        OFFICIAL_PROCESSED_DIR / getattr(C, "OFFICIAL_DATA_SUMMARY_FILE", "official_data_summary.json")
    )
    mode = _read_json(
        OFFICIAL_PROCESSED_DIR / getattr(C, "OFFICIAL_FINAL_MODE_FLAG_FILE", "official_final_mode.json")
    )

    readiness: dict[str, Any] = {}
    try:
        from src.official.final_readiness import evaluate_official_final_readiness

        readiness = evaluate_official_final_readiness()
    except Exception:
        readiness = {}

    rs = readiness.get("summary", {})
    official_final_enabled = bool(mode.get("official_final_enabled", False))
    readiness_ready = bool(readiness.get("is_official_final_ready", False))

    teams = int(rs.get("teams_count") or official_summary.get("teams_count") or 0)
    fixtures = int(rs.get("fixtures_count") or official_summary.get("fixtures_count") or 0)
    players = int(rs.get("players_count") or official_summary.get("players_count") or 0)
    squads_26 = int(rs.get("teams_with_26_players") or official_summary.get("teams_with_26_players") or 0)

    counts_ok = teams >= 48 and fixtures >= 100 and players >= 1000 and squads_26 >= 48
    is_verified = official_final_enabled or readiness_ready or counts_ok

    if is_verified:
        data_label = "Ready"
        verification_label = "Verified"
    elif counts_ok:
        data_label = "Ready"
        verification_label = "Needs review"
    else:
        data_label = "Needs review"
        verification_label = "Needs review"

    return {
        "official_final_enabled": official_final_enabled,
        "readiness_ready": readiness_ready,
        "is_verified": is_verified,
        "data_label": data_label,
        "verification_label": verification_label,
        "teams_count": teams,
        "fixtures_count": fixtures,
        "players_count": players,
        "teams_with_26_players": squads_26,
        "readiness": readiness,
        "readiness_summary": rs,
        "official_summary": official_summary,
        "mode": mode,
        "awards_allowed": official_final_enabled or readiness_ready or counts_ok,
    }
