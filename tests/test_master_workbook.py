"""Tests for master workbook generation."""

from __future__ import annotations

from pathlib import Path

from src.official.master_workbook import (
    create_master_import_readme,
    generate_population_workbook_pack,
)


def test_generate_population_workbook_pack_creates_artifacts(tmp_path, monkeypatch):
    workbook_dir = tmp_path / "workbooks"
    monkeypatch.setattr("src.official.master_workbook._workbook_dir", lambda: workbook_dir)

    result = generate_population_workbook_pack()
    assert result["status"] in ("ok", "fallback")
    assert Path(result["readme_path"]).is_file()

    if result["status"] == "ok":
        assert Path(result["workbook_path"]).is_file()
    else:
        assert "notes" in result


def test_create_master_import_readme_writes_file(tmp_path):
    path = tmp_path / "readme.md"
    saved = create_master_import_readme(str(path))
    assert Path(saved).is_file()
    content = Path(saved).read_text(encoding="utf-8")
    assert "Manual" in content or "manual" in content
