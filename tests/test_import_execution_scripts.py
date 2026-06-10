"""Smoke tests for Step 17G CLI scripts."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / script), *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )


def test_run_official_import_execution_script():
    result = _run("run_official_import_execution.py")
    assert result.returncode == 0
    assert "Step 17G" in result.stdout


def test_fix_and_check_future_team_filter_script():
    result = _run("fix_and_check_future_team_filter.py")
    assert result.returncode == 0
    assert "Future Team Filter" in result.stdout
