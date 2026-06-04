"""Inspect Step 13 knockout simulation outputs."""

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
KNOCKOUT_BRACKET_FILLED_FILE = getattr(C, "KNOCKOUT_BRACKET_FILLED_FILE", "knockout_bracket_filled.csv")
KNOCKOUT_SIMULATED_MATCHES_FILE = getattr(C, "KNOCKOUT_SIMULATED_MATCHES_FILE", "knockout_simulated_matches.csv")
SINGLE_TOURNAMENT_RESULT_FILE = getattr(C, "SINGLE_TOURNAMENT_RESULT_FILE", "single_tournament_result.json")
KNOCKOUT_SIMULATION_SUMMARY_FILE = getattr(C, "KNOCKOUT_SIMULATION_SUMMARY_FILE", "knockout_simulation_summary.json")
KNOCKOUT_SIMULATION_VALIDATION_REPORT_FILE = getattr(
    C,
    "KNOCKOUT_SIMULATION_VALIDATION_REPORT_FILE",
    "knockout_simulation_validation_report.csv",
)


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
    bracket = _safe_read_csv(_path(KNOCKOUT_BRACKET_FILLED_FILE))
    matches = _safe_read_csv(_path(KNOCKOUT_SIMULATED_MATCHES_FILE))
    validation = _safe_read_csv(_path(KNOCKOUT_SIMULATION_VALIDATION_REPORT_FILE))
    summary = _safe_read_json(_path(KNOCKOUT_SIMULATION_SUMMARY_FILE))
    single_result = _safe_read_json(_path(SINGLE_TOURNAMENT_RESULT_FILE))

    if bracket is None or matches is None or validation is None or summary is None or single_result is None:
        print("Missing knockout outputs.")
        print("Run: python scripts/simulate_knockout_stage.py --seed 42")
        return 0

    print("=== Step 13 Knockout Simulation Inspection ===")
    print(f"champion: {summary.get('champion')}")
    print(f"runner_up: {summary.get('runner_up')}")
    print(f"third_place: {summary.get('third_place')}")
    print(f"fourth_place: {summary.get('fourth_place')}")
    print(f"validation_passed: {summary.get('validation_passed')}")
    print()

    round_counts = matches.groupby("round")["match_id"].count().to_dict()
    print("Match count by round:")
    for round_name in ["round_of_32", "round_of_16", "quarter_final", "semi_final", "third_place", "final"]:
        print(f"  {round_name}: {round_counts.get(round_name, 0)}")
    print()

    print("Full bracket results:")
    display_cols = [
        "round",
        "match_id",
        "team_a",
        "team_b",
        "simulated_team_a_score",
        "simulated_team_b_score",
        "outcome_method",
        "winner",
        "loser",
    ]
    print(matches[display_cols].to_string(index=False))
    print()

    print("Validation report:")
    print(validation.to_string(index=False))
    print()

    print("Bracket structure preview:")
    print(bracket[[col for col in ["round", "match_id", "team_a", "team_b", "source_a", "source_b", "winner_to"] if col in bracket.columns]].to_string(index=False))
    print()

    print("Single tournament result keys:")
    print(sorted(single_result.keys()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
