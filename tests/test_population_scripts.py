"""Smoke tests for Step 17D population scripts."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run_script(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )


def test_prepare_official_population_pack_script_smoke():
    result = _run_script(["scripts/prepare_official_population_pack.py"])
    assert result.returncode == 0
    assert "population_pack_ready" in result.stdout or "Status:" in result.stdout


def test_promote_official_final_script_smoke():
    result = _run_script(["scripts/promote_official_final.py"])
    assert result.returncode == 0
    combined = (result.stdout + result.stderr).lower()
    assert "confirm" in combined or "confirmation_required" in combined


def test_promote_official_final_confirm_blocked_smoke():
    result = _run_script(["scripts/promote_official_final.py", "--confirm"])
    assert result.returncode == 1
    combined = (result.stdout + result.stderr).lower()
    assert "blocked" in combined or "not pass" in combined or "false" in combined


def test_preview_official_import_script_smoke():
    templates_dir = PROJECT_ROOT / "data/official/import_templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    players_tpl = templates_dir / "official_players_import_template.csv"
    if not players_tpl.is_file():
        _run_script(["scripts/prepare_official_population_pack.py"])

    if players_tpl.is_file():
        result = _run_script([
            "scripts/preview_official_import.py",
            "--target", "players",
            "--file", str(players_tpl),
        ])
        assert result.returncode == 0
        assert "Diff report path" in result.stdout
