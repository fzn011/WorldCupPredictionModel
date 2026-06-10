"""Tests for Step 17E official source downloader."""

from __future__ import annotations

import json
from pathlib import Path

from src.official.source_downloader import (
    download_official_source,
    ensure_source_dirs,
    save_snapshot_manifest,
)


def test_download_official_source_rejects_invalid_domains(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = download_official_source("teams", url="https://evil.example/teams")
    assert result["success"] is False
    assert "not allowed" in result["error_message"].lower()


def test_save_snapshot_manifest_writes_json(tmp_path, monkeypatch):
    import src.utils.constants as C

    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    ensure_source_dirs()
    path = save_snapshot_manifest({"teams": {"success": True}})
    assert Path(path).is_file()
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    assert "downloads" in data
