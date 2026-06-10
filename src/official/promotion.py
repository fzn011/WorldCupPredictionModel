"""Official-final promotion gate for Step 17D."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C
from src.official.final_readiness import evaluate_official_final_readiness


def _flag_path() -> Path:
    return C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR / C.OFFICIAL_FINAL_MODE_FLAG_FILE


def load_official_final_mode() -> dict[str, Any]:
    """Return official_final mode flag status."""
    path = _flag_path()
    if not path.is_file():
        return {"official_final_enabled": False, "promoted_at": None, "readiness_summary": {}}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def can_promote_to_official_final() -> tuple[bool, dict[str, Any]]:
    """Check if promotion to official_final is allowed."""
    try:
        report = evaluate_official_final_readiness()
    except Exception as exc:
        return False, {
            "status": "blocked",
            "is_official_final_ready": False,
            "blocker_count": 1,
            "warning_count": 0,
            "blockers": ["validation_failed"],
            "summary": {},
            "error": str(exc),
        }

    final_ready = bool(report.get("is_official_final_ready"))
    summary = {
        "status": report.get("status"),
        "is_official_final_ready": final_ready,
        "blocker_count": report.get("summary", {}).get("blocker_count", 0),
        "warning_count": report.get("summary", {}).get("warning_count", 0),
        "blockers": [b.get("id", "unknown") for b in report.get("blockers", [])],
        "summary": report.get("summary", {}),
    }
    return final_ready, summary


def _save_promotion_report(result: dict[str, Any]) -> str:
    reports_dir = C.PROJECT_ROOT / C.OFFICIAL_POPULATION_REPORTS_DIR
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / C.OFFICIAL_POPULATION_PROMOTION_REPORT_FILE

    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": result.get("status"),
        "official_final_enabled": result.get("official_final_enabled", False),
        "reason": result.get("reason", ""),
    }
    if report_path.is_file():
        existing = pd.read_csv(report_path)
        updated = pd.concat([existing, pd.DataFrame([row])], ignore_index=True)
    else:
        updated = pd.DataFrame([row])
    updated.to_csv(report_path, index=False)
    return str(report_path)


def promote_to_official_final(confirmed: bool = False) -> dict[str, Any]:
    """Promote to official_final mode when readiness passes and user confirms."""
    final_ready, readiness_summary = can_promote_to_official_final()

    if not confirmed:
        return {
            "status": "confirmation_required",
            "official_final_enabled": False,
            "readiness_summary": readiness_summary,
            "message": "Promotion requires --confirm flag after reviewing readiness.",
        }

    if not final_ready:
        result = {
            "status": "blocked",
            "official_final_enabled": False,
            "readiness_summary": readiness_summary,
            "message": "Promotion blocked: official final readiness checks have not passed.",
        }
        _save_promotion_report(result)
        return result

    flag = {
        "official_final_enabled": True,
        "promoted_at": datetime.now(timezone.utc).isoformat(),
        "readiness_summary": readiness_summary,
    }
    path = _flag_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(flag, f, indent=2)

    result = {
        "status": "promoted",
        "official_final_enabled": True,
        "flag_path": str(path),
        "readiness_summary": readiness_summary,
    }
    _save_promotion_report(result)
    return result


def demote_from_official_final(reason: str = "") -> dict[str, Any]:
    """Disable official_final mode."""
    flag = {
        "official_final_enabled": False,
        "demoted_at": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
    }
    path = _flag_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(flag, f, indent=2)

    result = {
        "status": "demoted",
        "official_final_enabled": False,
        "flag_path": str(path),
        "reason": reason,
    }
    _save_promotion_report(result)
    return result
