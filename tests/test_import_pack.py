"""Tests for Step 17E import pack export."""

from __future__ import annotations

from pathlib import Path

import src.utils.constants as C
from src.official.import_pack import create_import_pack_summary, create_import_pack_zip


def test_create_import_pack_zip_creates_file(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    (tmp_path / C.OFFICIAL_SOURCE_STAGING_DIR).mkdir(parents=True, exist_ok=True)
    (tmp_path / C.OFFICIAL_SOURCE_EXPORTS_DIR).mkdir(parents=True, exist_ok=True)
    (tmp_path / C.OFFICIAL_SOURCE_DATA_DIR).mkdir(parents=True, exist_ok=True)
    reg = tmp_path / C.OFFICIAL_SOURCE_DATA_DIR / C.OFFICIAL_SOURCE_REGISTRY_FILE
    reg.write_text("{}", encoding="utf-8")

    zip_path = create_import_pack_zip()
    assert Path(zip_path).is_file()
    summary = create_import_pack_summary()
    assert "status" in summary
    assert "files_included" in summary
