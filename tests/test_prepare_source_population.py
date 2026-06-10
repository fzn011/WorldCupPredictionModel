"""Tests for Step 17E prepare_source_population orchestrator."""

from __future__ import annotations

from pathlib import Path

import src.utils.constants as C
from src.official.prepare_source_population import prepare_step17e_source_assisted_population


def test_prepare_step17e_returns_status(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    result = prepare_step17e_source_assisted_population(
        download_sources=False,
        parse_sources=False,
        create_pack=True,
    )
    assert result["status"] in {"source_population_ready", "needs_manual_review"}
    assert result["final_ready"] is False
    assert Path(result["summary_path"]).is_file()


def test_import_pack_path_exists_when_create_pack_true(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    result = prepare_step17e_source_assisted_population(create_pack=True, parse_sources=False)
    if result.get("import_pack_path"):
        assert Path(result["import_pack_path"]).is_file()
