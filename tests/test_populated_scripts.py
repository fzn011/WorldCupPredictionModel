"""Smoke tests for Step 17F CLI scripts."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run_script(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / script), *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )


def test_prepare_populated_official_data_script():
    result = _run_script("prepare_populated_official_data.py")
    assert result.returncode == 0
    assert "Step 17F" in result.stdout


def test_apply_populated_official_data_preview_script():
    result = _run_script("apply_populated_official_data.py", "--preview")
    assert result.returncode == 0
    assert "ready_for_apply" in result.stdout


def test_import_fifa_schedule_file_missing_args():
    result = _run_script("import_fifa_schedule_file.py")
    assert result.returncode != 0


def test_import_fifa_squad_file_missing_args():
    result = _run_script("import_fifa_squad_file.py")
    assert result.returncode != 0
