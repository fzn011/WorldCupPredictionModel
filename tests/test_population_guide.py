"""Tests for population guide generation."""

from __future__ import annotations

from pathlib import Path

from src.official.population_guide import generate_population_guide_markdown, save_population_guide


def test_generate_population_guide_markdown_returns_required_sections():
    md = generate_population_guide_markdown()
    for section in (
        "## 1. Overview",
        "## 2. Data modes",
        "## 3. Required files",
        "## 10. Applying imports",
        "## 12. Promoting to official_final",
        "## 14. Final checklist",
    ):
        assert section in md
    assert "sample_to_be_verified" in md
    assert "does not scrape" in md.lower() or "does not scrape" in md


def test_save_population_guide_writes_file(tmp_path):
    path = tmp_path / "guide.md"
    saved = save_population_guide(str(path))
    assert Path(saved).is_file()
    assert Path(saved).read_text(encoding="utf-8")
