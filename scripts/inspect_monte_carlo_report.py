"""Inspect Step 16 Monte Carlo report artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import src.utils.constants as C

PROJECT_ROOT = getattr(C, "PROJECT_ROOT", Path(__file__).resolve().parents[1])
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
MONTE_CARLO_REPORT_MD_FILE = getattr(C, "MONTE_CARLO_REPORT_MD_FILE", "monte_carlo_report.md")
MONTE_CARLO_SUMMARY_CARDS_FILE = getattr(C, "MONTE_CARLO_SUMMARY_CARDS_FILE", "monte_carlo_summary_cards.csv")
MONTE_CARLO_DASHBOARD_EXPORT_FILE = getattr(C, "MONTE_CARLO_DASHBOARD_EXPORT_FILE", "monte_carlo_dashboard_export.csv")
MONTE_CARLO_CHAMPION_CHART_FILE = getattr(C, "MONTE_CARLO_CHAMPION_CHART_FILE", "monte_carlo_champion_probabilities.png")
MONTE_CARLO_STAGE_HEATMAP_FILE = getattr(C, "MONTE_CARLO_STAGE_HEATMAP_FILE", "monte_carlo_stage_heatmap.png")


def main() -> int:
    report_path = REPORTS_DIR / MONTE_CARLO_REPORT_MD_FILE
    cards_path = REPORTS_DIR / MONTE_CARLO_SUMMARY_CARDS_FILE
    export_path = REPORTS_DIR / MONTE_CARLO_DASHBOARD_EXPORT_FILE
    champion_chart_path = FIGURES_DIR / MONTE_CARLO_CHAMPION_CHART_FILE
    stage_heatmap_path = FIGURES_DIR / MONTE_CARLO_STAGE_HEATMAP_FILE

    if not all(path.is_file() for path in [report_path, cards_path, export_path, champion_chart_path, stage_heatmap_path]):
        print("Report artifacts are missing.")
        print("Run: python scripts/generate_monte_carlo_report.py")
        return 0

    cards_df = pd.read_csv(cards_path)
    export_df = pd.read_csv(export_path)
    report_text = report_path.read_text(encoding="utf-8").splitlines()

    print("=== Step 16 Monte Carlo Report Inspection ===")
    print(f"report_path_exists: {report_path.is_file()}")
    print(f"summary_cards_path_exists: {cards_path.is_file()}")
    print(f"dashboard_export_path_exists: {export_path.is_file()}")
    print(f"champion_chart_exists: {champion_chart_path.is_file()} -> {champion_chart_path}")
    print(f"stage_heatmap_exists: {stage_heatmap_path.is_file()} -> {stage_heatmap_path}")
    print()
    print("Summary cards preview:")
    print(cards_df.to_string(index=False))
    print()
    print("Dashboard export sections:")
    print(export_df["section"].value_counts().to_string())
    print()
    print("Markdown report preview (first 40 lines):")
    for line in report_text[:40]:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
