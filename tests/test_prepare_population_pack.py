"""Tests for Step 17D population pack orchestrator."""

from __future__ import annotations

from pathlib import Path

from src.official.prepare_population_pack import prepare_step17d_official_data_population_pack
from src.utils.constants import PROJECT_ROOT


def test_prepare_step17d_returns_population_pack_ready():
    result = prepare_step17d_official_data_population_pack()
    assert result["status"] == "population_pack_ready"
    assert Path(result["guide_path"]).is_file()
    assert Path(result["missing_data_report_path"]).is_file()
    assert Path(result["workbook_readme_path"]).is_file()
    assert result["final_ready"] is False


def test_prepare_step17d_creates_templates_and_guide():
    result = prepare_step17d_official_data_population_pack()
    template_dir = Path(result["template_dir"])
    assert template_dir.is_dir()
    assert any(template_dir.glob("*.csv"))
    assert (PROJECT_ROOT / "data/official/population/official_data_population_guide.md").is_file()
