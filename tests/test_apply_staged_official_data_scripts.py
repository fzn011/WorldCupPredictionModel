"""Smoke tests for Step 17E CLI scripts."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )


def test_prepare_source_population_script_smoke():
    result = _run(["scripts/prepare_source_population.py"])
    assert result.returncode == 0
    assert "Step 17E" in result.stdout


def test_export_official_import_pack_script_smoke():
    _run(["scripts/prepare_source_population.py"])
    result = _run(["scripts/export_official_import_pack.py"])
    assert result.returncode == 0
    assert "Zip path" in result.stdout


def test_apply_staged_official_data_preview_smoke():
    result = _run(["scripts/apply_staged_official_data.py", "--target", "teams", "--preview"])
    assert result.returncode == 0


def test_ingest_manual_official_file_help_smoke():
    result = _run(["scripts/ingest_manual_official_file.py", "--help"])
    assert result.returncode == 0
