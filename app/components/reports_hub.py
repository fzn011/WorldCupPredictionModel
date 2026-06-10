"""Shared Reports & Downloads hub for homepage and dedicated Streamlit page."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

import src.utils.constants as C
from app.components.ui import render_download_card, render_section_header

try:
    from app.streamlit_paths import OFFICIAL_PROCESSED_DIR, PROCESSED_DATA_DIR, PROJECT_ROOT, REPORTS_DIR
except ModuleNotFoundError:  # pragma: no cover
    from streamlit_paths import OFFICIAL_PROCESSED_DIR, PROCESSED_DATA_DIR, PROJECT_ROOT, REPORTS_DIR  # type: ignore


def render_reports_hub() -> None:
    """Render grouped download cards for Monte Carlo, awards, official data, and portfolio."""
    portfolio_dir = PROJECT_ROOT / str(getattr(C, "PORTFOLIO_DIR", "portfolio"))

    render_section_header("Reports & Downloads", subtitle="Export simulation, awards, and official data artifacts.")
    g1, g2 = st.columns(2)
    with g1:
        render_section_header("Monte Carlo", subtitle="Tournament simulation forecasts")
        render_download_card(
            "Champion probabilities",
            "Team-level tournament outcome estimates",
            PROCESSED_DATA_DIR / getattr(C, "MONTE_CARLO_CHAMPION_PROBABILITIES_FILE", "monte_carlo_champion_probabilities.csv"),
        )
        render_download_card(
            "Monte Carlo summary",
            "Run metadata and top champion",
            PROCESSED_DATA_DIR / getattr(C, "MONTE_CARLO_SUMMARY_FILE", "monte_carlo_summary.json"),
            mime="application/json",
        )
        render_download_card(
            "Monte Carlo report",
            "Markdown narrative report",
            REPORTS_DIR / getattr(C, "MONTE_CARLO_REPORT_MD_FILE", "monte_carlo_report.md"),
            mime="text/markdown",
        )
    with g2:
        render_section_header("Awards analytics", subtitle="Official candidates only — not FIFA predictions")
        render_download_card(
            "Combined awards table",
            "All award categories in one CSV",
            PROCESSED_DATA_DIR / getattr(C, "WORLD_CUP_AWARDS_PREDICTIONS_FILE", "world_cup_awards_predictions.csv"),
        )
        render_download_card(
            "Awards summary",
            "Validation and top picks",
            PROCESSED_DATA_DIR / getattr(C, "WORLD_CUP_AWARDS_SUMMARY_FILE", "world_cup_awards_summary.json"),
            mime="application/json",
        )
        render_download_card(
            "Awards report",
            "Markdown awards narrative",
            REPORTS_DIR / getattr(C, "WORLD_CUP_AWARDS_REPORT_FILE", "world_cup_awards_report.md"),
            mime="text/markdown",
        )

    g3, g4 = st.columns(2)
    with g3:
        render_section_header("Official data", subtitle="Readiness and validation")
        render_download_card(
            "Official data summary",
            "Teams, fixtures, and players snapshot",
            OFFICIAL_PROCESSED_DIR / getattr(C, "OFFICIAL_DATA_SUMMARY_FILE", "official_data_summary.json"),
            mime="application/json",
        )
        render_download_card(
            "Final readiness report",
            "Production data gate checklist",
            OFFICIAL_PROCESSED_DIR / "official_final_readiness_report.json",
            mime="application/json",
        )
    with g4:
        render_section_header("Portfolio pack", subtitle="Demo and reproducibility")
        render_download_card(
            "Portfolio README",
            "Project overview for reviewers",
            portfolio_dir / "PORTFOLIO_README.md",
            mime="text/markdown",
        )
        render_download_card(
            "Demo script",
            "Walkthrough guide",
            portfolio_dir / "demo_script.md",
            mime="text/markdown",
        )
        render_download_card(
            "Final project summary",
            "Latest pipeline status",
            PROCESSED_DATA_DIR / "final_project_summary.json",
            mime="application/json",
        )
