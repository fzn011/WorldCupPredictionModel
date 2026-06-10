"""Population status tracking for Step 17D official data population."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import src.utils.constants as C


def initialize_population_status() -> dict[str, Any]:
    """Return a fresh population status structure."""
    steps = {
        step: {"status": "not_started", "notes": ""}
        for step in C.OFFICIAL_POPULATION_REQUIRED_STEPS
    }
    return {
        "status": "in_progress",
        "steps": steps,
        "last_updated_at": datetime.now(timezone.utc).isoformat(),
        "official_final_ready": False,
        "notes": [],
    }


def _status_path(path: str | None = None) -> Path:
    if path is None:
        return C.PROJECT_ROOT / C.OFFICIAL_POPULATION_DIR / C.OFFICIAL_POPULATION_STATUS_FILE
    return Path(path)


def load_population_status(path: str | None = None) -> dict[str, Any]:
    """Load population status from disk, initializing if missing."""
    status_file = _status_path(path)
    if not status_file.is_file():
        return initialize_population_status()
    with open(status_file, encoding="utf-8") as f:
        return json.load(f)


def save_population_status(status: dict[str, Any], path: str | None = None) -> str:
    """Persist population status to disk."""
    status_file = _status_path(path)
    status_file.parent.mkdir(parents=True, exist_ok=True)
    status["last_updated_at"] = datetime.now(timezone.utc).isoformat()
    with open(status_file, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2)
    return str(status_file)


def update_population_step(step_name: str, status: str, notes: str = "") -> dict[str, Any]:
    """Update a single population step status."""
    if step_name not in C.OFFICIAL_POPULATION_REQUIRED_STEPS:
        raise ValueError(f"Unknown step: {step_name}")
    if status not in C.OFFICIAL_POPULATION_ALLOWED_STATUSES:
        raise ValueError(f"Invalid status: {status}. Allowed: {C.OFFICIAL_POPULATION_ALLOWED_STATUSES}")

    population = load_population_status()
    population["steps"][step_name] = {"status": status, "notes": notes}
    save_population_status(population)
    return population


def summarize_population_status(status: dict[str, Any]) -> dict[str, Any]:
    """Summarize population workflow progress."""
    steps = status.get("steps", {})
    total_steps = len(C.OFFICIAL_POPULATION_REQUIRED_STEPS)
    completed = sum(1 for s in steps.values() if s.get("status") in ("imported", "final_ready"))
    blocked = sum(1 for s in steps.values() if s.get("status") == "blocked")
    in_progress = sum(1 for s in steps.values() if s.get("status") in ("in_progress", "needs_review", "ready_for_import"))

    if status.get("official_final_ready"):
        overall = "final_ready"
    elif blocked > 0:
        overall = "blocked"
    elif completed == total_steps:
        overall = "ready_for_import"
    else:
        overall = status.get("status", "in_progress")

    return {
        "overall_status": overall,
        "completed_steps": completed,
        "total_steps": total_steps,
        "blocked_steps": blocked,
        "in_progress_steps": in_progress,
        "official_final_ready": bool(status.get("official_final_ready")),
    }
