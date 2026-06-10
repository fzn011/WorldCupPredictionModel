"""Step 15 Monte Carlo preparation orchestrator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.simulation.monte_carlo import (
    build_champion_probabilities,
    build_finalists_table,
    build_semifinalists_table,
    build_simulation_results_table,
    build_team_stage_counts,
    build_team_stage_probabilities,
    create_monte_carlo_summary,
    run_monte_carlo_simulations,
    validate_monte_carlo_outputs,
)
import src.utils.constants as C

PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")
MONTE_CARLO_SIMULATION_RESULTS_FILE = getattr(C, "MONTE_CARLO_SIMULATION_RESULTS_FILE", "monte_carlo_simulation_results.csv")
MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE = getattr(C, "MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE", "monte_carlo_team_stage_probabilities.csv")
MONTE_CARLO_CHAMPION_PROBABILITIES_FILE = getattr(C, "MONTE_CARLO_CHAMPION_PROBABILITIES_FILE", "monte_carlo_champion_probabilities.csv")
MONTE_CARLO_FINALISTS_FILE = getattr(C, "MONTE_CARLO_FINALISTS_FILE", "monte_carlo_finalists.csv")
MONTE_CARLO_SEMIFINALISTS_FILE = getattr(C, "MONTE_CARLO_SEMIFINALISTS_FILE", "monte_carlo_semifinalists.csv")
MONTE_CARLO_SUMMARY_FILE = getattr(C, "MONTE_CARLO_SUMMARY_FILE", "monte_carlo_summary.json")
MONTE_CARLO_VALIDATION_REPORT_FILE = getattr(C, "MONTE_CARLO_VALIDATION_REPORT_FILE", "monte_carlo_validation_report.csv")

DEFAULT_MONTE_CARLO_SIMULATIONS = int(getattr(C, "DEFAULT_MONTE_CARLO_SIMULATIONS", 100))
DEFAULT_MONTE_CARLO_SEED = int(getattr(C, "DEFAULT_MONTE_CARLO_SEED", 42))


def _save_csv(df: pd.DataFrame, file_name: str) -> str:
    path = PROCESSED_DATA_DIR / file_name
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return str(path)


def _json_safe(value: Any) -> Any:
    if isinstance(value, pd.DataFrame):
        return value.to_dict(orient="records")
    if isinstance(value, pd.Series):
        return value.to_dict()
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def _save_json(payload: dict[str, Any], file_name: str) -> str:
    path = PROCESSED_DATA_DIR / file_name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(_json_safe(payload), f, ensure_ascii=False, indent=2)
    return str(path)


def prepare_step15_monte_carlo_simulation(
    num_simulations: int = DEFAULT_MONTE_CARLO_SIMULATIONS,
    base_seed: int = DEFAULT_MONTE_CARLO_SEED,
    predictor: Any | None = None,
) -> dict[str, Any]:
    """Run and persist Step 15 Monte Carlo tournament simulation artifacts."""
    num_simulations = int(max(1, num_simulations))
    base_seed = int(base_seed)

    raw = run_monte_carlo_simulations(
        num_simulations=num_simulations,
        base_seed=base_seed,
        predictor=predictor,
    )

    simulation_results_df = build_simulation_results_table(raw["simulation_results"])
    successful_simulations = int((simulation_results_df["status"] == "success").sum()) if not simulation_results_df.empty else 0

    stage_counts_df = build_team_stage_counts(raw["path_reports"])
    team_stage_probabilities_df = build_team_stage_probabilities(stage_counts_df, successful_simulations=max(1, successful_simulations))
    champion_probabilities_df = build_champion_probabilities(simulation_results_df)
    finalists_df = build_finalists_table(simulation_results_df)
    semifinalists_df = build_semifinalists_table(raw["path_reports"], successful_simulations=max(1, successful_simulations))

    validation_passed, validation_report_df = validate_monte_carlo_outputs(
        simulation_results_df=simulation_results_df,
        team_stage_probabilities_df=team_stage_probabilities_df,
        champion_probabilities_df=champion_probabilities_df,
        num_simulations=num_simulations,
    )

    summary = create_monte_carlo_summary(
        simulation_results_df=simulation_results_df,
        champion_probabilities_df=champion_probabilities_df,
        team_stage_probabilities_df=team_stage_probabilities_df,
        validation_passed=validation_passed,
        num_simulations=num_simulations,
        base_seed=base_seed,
        cache_info=raw.get("cache_info", {}),
    )

    simulation_results_path = _save_csv(simulation_results_df, MONTE_CARLO_SIMULATION_RESULTS_FILE)
    team_stage_probabilities_path = _save_csv(team_stage_probabilities_df, MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE)
    champion_probabilities_path = _save_csv(champion_probabilities_df, MONTE_CARLO_CHAMPION_PROBABILITIES_FILE)
    finalists_path = _save_csv(finalists_df, MONTE_CARLO_FINALISTS_FILE)
    semifinalists_path = _save_csv(semifinalists_df, MONTE_CARLO_SEMIFINALISTS_FILE)
    validation_report_path = _save_csv(validation_report_df, MONTE_CARLO_VALIDATION_REPORT_FILE)
    summary_path = _save_json(summary, MONTE_CARLO_SUMMARY_FILE)

    summary.update(
        {
            "simulation_results_path": simulation_results_path,
            "team_stage_probabilities_path": team_stage_probabilities_path,
            "champion_probabilities_path": champion_probabilities_path,
            "finalists_path": finalists_path,
            "semifinalists_path": semifinalists_path,
            "validation_report_path": validation_report_path,
            "summary_path": summary_path,
        }
    )
    return summary


if __name__ == "__main__":
    print(prepare_step15_monte_carlo_simulation())
