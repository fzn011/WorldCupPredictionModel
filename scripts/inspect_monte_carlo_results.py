"""Inspect Step 15 Monte Carlo simulation outputs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import src.utils.constants as C

PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")
MONTE_CARLO_SIMULATION_RESULTS_FILE = getattr(C, "MONTE_CARLO_SIMULATION_RESULTS_FILE", "monte_carlo_simulation_results.csv")
MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE = getattr(C, "MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE", "monte_carlo_team_stage_probabilities.csv")
MONTE_CARLO_CHAMPION_PROBABILITIES_FILE = getattr(C, "MONTE_CARLO_CHAMPION_PROBABILITIES_FILE", "monte_carlo_champion_probabilities.csv")
MONTE_CARLO_FINALISTS_FILE = getattr(C, "MONTE_CARLO_FINALISTS_FILE", "monte_carlo_finalists.csv")
MONTE_CARLO_SEMIFINALISTS_FILE = getattr(C, "MONTE_CARLO_SEMIFINALISTS_FILE", "monte_carlo_semifinalists.csv")
MONTE_CARLO_SUMMARY_FILE = getattr(C, "MONTE_CARLO_SUMMARY_FILE", "monte_carlo_summary.json")
MONTE_CARLO_VALIDATION_REPORT_FILE = getattr(C, "MONTE_CARLO_VALIDATION_REPORT_FILE", "monte_carlo_validation_report.csv")


def _path(name: str) -> Path:
    return PROCESSED_DATA_DIR / name


def _safe_read_csv(path: Path) -> pd.DataFrame | None:
    if not path.is_file():
        return None
    return pd.read_csv(path)


def _safe_read_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    simulation_results = _safe_read_csv(_path(MONTE_CARLO_SIMULATION_RESULTS_FILE))
    stage_probabilities = _safe_read_csv(_path(MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE))
    champion_probabilities = _safe_read_csv(_path(MONTE_CARLO_CHAMPION_PROBABILITIES_FILE))
    finalists = _safe_read_csv(_path(MONTE_CARLO_FINALISTS_FILE))
    semifinalists = _safe_read_csv(_path(MONTE_CARLO_SEMIFINALISTS_FILE))
    summary = _safe_read_json(_path(MONTE_CARLO_SUMMARY_FILE))
    validation = _safe_read_csv(_path(MONTE_CARLO_VALIDATION_REPORT_FILE))

    if any(item is None for item in [simulation_results, stage_probabilities, champion_probabilities, finalists, semifinalists, summary, validation]):
        print("Missing Monte Carlo outputs.")
        print("Run: python scripts/run_monte_carlo.py --simulations 100 --seed 42")
        return 0

    print("=== Step 15 Monte Carlo Inspection ===")
    print("Summary:")
    for k, v in summary.items():
        print(f"{k}: {v}")
    print()

    print("Top 20 champion probabilities:")
    print(champion_probabilities.head(20).to_string(index=False))
    print()

    print("Top 20 stage probabilities:")
    print(stage_probabilities.head(20).to_string(index=False))
    print()

    print("Finalists table:")
    print(finalists.to_string(index=False))
    print()

    print("Semifinalists table:")
    print(semifinalists.to_string(index=False))
    print()

    print("Validation report:")
    print(validation.to_string(index=False))
    print()

    print(f"simulation_results_rows: {len(simulation_results)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
