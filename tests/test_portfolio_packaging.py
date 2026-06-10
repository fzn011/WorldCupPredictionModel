"""Tests for Step 19 portfolio packaging."""

from __future__ import annotations

from src.portfolio.packaging import (
    generate_demo_script,
    generate_limitations_doc,
    generate_portfolio_readme,
    prepare_step19_portfolio_pack,
)


def test_prepare_step19_portfolio_pack_creates_docs(tmp_path, monkeypatch):
    monkeypatch.setattr("src.portfolio.packaging.PROJECT_ROOT", tmp_path)
    monkeypatch.setattr("src.portfolio.packaging.PORTFOLIO_DIR", tmp_path / "portfolio")
    monkeypatch.setattr("src.portfolio.packaging.ASSETS_DIR", tmp_path / "portfolio" / "assets")
    monkeypatch.setattr("src.portfolio.packaging.SCREENSHOTS_DIR", tmp_path / "portfolio" / "screenshots")

    result = prepare_step19_portfolio_pack()
    assert result["status"] == "ok"
    assert (tmp_path / "portfolio" / "PORTFOLIO_README.md").is_file()
    assert (tmp_path / "portfolio" / "demo_script.md").is_file()


def test_generated_docs_contain_required_sections(tmp_path, monkeypatch):
    monkeypatch.setattr("src.portfolio.packaging.PORTFOLIO_DIR", tmp_path / "portfolio")
    (tmp_path / "portfolio").mkdir(parents=True)

    readme = generate_portfolio_readme()
    demo = generate_demo_script()
    limits = generate_limitations_doc()

    assert "Problem statement" in readme
    assert "Demo Script" in demo or "Intro" in demo
    assert "Limitations" in limits or "uncertainty" in limits.lower()
