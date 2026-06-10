"""Generate Step 16 Monte Carlo report artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.reports.prepare_monte_carlo_report import prepare_step16_monte_carlo_report  # noqa: E402


def main() -> int:
    try:
        summary = prepare_step16_monte_carlo_report()
    except FileNotFoundError:
        print("Run python scripts/run_monte_carlo.py --simulations 10 --seed 42 first.")
        return 0

    print("=== Step 16 Monte Carlo Report Summary ===")
    for key in [
        "status",
        "top_champion",
        "top_champion_probability",
        "validation_status",
        "report_path",
        "summary_cards_path",
        "dashboard_export_path",
        "champion_chart_path",
        "stage_heatmap_path",
    ]:
        print(f"{key}: {summary.get(key)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
