#!/usr/bin/env python
"""Prepare final project summary, validation, and portfolio docs."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.portfolio.packaging import prepare_step19_portfolio_pack  # noqa: E402
from src.reports.final_project_report import (  # noqa: E402
    create_final_project_summary,
    create_final_validation_report,
    save_final_project_summary,
)


def main() -> int:
    portfolio = prepare_step19_portfolio_pack()
    summary = create_final_project_summary()
    summary_path = save_final_project_summary(summary)
    validation_df = create_final_validation_report()

    print("=== Step 19 Final Project Pack ===")
    print(f"status: {summary.get('status')}")
    print(f"official_final_enabled: {summary.get('official_final_enabled')}")
    print(f"fixtures_count: {summary.get('fixtures_count')}")
    print(f"players_count: {summary.get('players_count')}")
    print(f"monte_carlo_available: {summary.get('monte_carlo_available')}")
    print(f"awards_available: {summary.get('awards_available')}")
    print(f"summary_path: {summary_path}")
    print(f"validation_report_path: {ROOT / 'data/processed/final_project_validation_report.csv'}")
    for key in ("portfolio_readme", "demo_script", "architecture", "deployment_guide"):
        print(f"{key}: {portfolio.get(key)}")
    passed = bool(validation_df["passed"].all()) if not validation_df.empty else False
    print(f"validation_passed: {passed}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
