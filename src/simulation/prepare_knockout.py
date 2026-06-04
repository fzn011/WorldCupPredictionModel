"""Step 13 knockout simulation preparation orchestrator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.simulation.knockout_stage import (
    KNOCKOUT_BRACKET_FILLED_FILE,
    KNOCKOUT_SIMULATION_SUMMARY_FILE,
    KNOCKOUT_SIMULATION_VALIDATION_REPORT_FILE,
    KNOCKOUT_SIMULATED_MATCHES_FILE,
    SINGLE_TOURNAMENT_RESULT_FILE,
    create_knockout_summary,
    simulate_knockout_stage,
    validate_knockout_simulation,
)
import src.utils.constants as C

PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")


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


def prepare_step13_knockout_simulation(random_seed: int = 42) -> dict[str, Any]:
    """Run the full Step 13 knockout simulation pipeline and persist outputs."""
    result = simulate_knockout_stage(random_seed=random_seed)
    validation_passed, validation_report_df = validate_knockout_simulation(
        simulated_matches_df=result["simulated_matches"],
        result_summary=result,
    )
    summary = create_knockout_summary(result, validation_passed, random_seed)

    bracket_filled_path = _save_csv(result["bracket_filled"], KNOCKOUT_BRACKET_FILLED_FILE)
    simulated_matches_path = _save_csv(result["simulated_matches"], KNOCKOUT_SIMULATED_MATCHES_FILE)
    validation_report_path = _save_csv(validation_report_df, KNOCKOUT_SIMULATION_VALIDATION_REPORT_FILE)

    single_result_payload = {
        "seeded_qualifiers": result["seeded_qualifiers"],
        "bracket_filled": result["bracket_filled"],
        "simulated_matches": result["simulated_matches"],
        "champion": result.get("champion"),
        "runner_up": result.get("runner_up"),
        "third_place": result.get("third_place"),
        "fourth_place": result.get("fourth_place"),
        "validation_passed": validation_passed,
        "validation_report": validation_report_df,
        "summary": summary,
    }
    single_result_path = _save_json(single_result_payload, SINGLE_TOURNAMENT_RESULT_FILE)

    summary_path = PROCESSED_DATA_DIR / KNOCKOUT_SIMULATION_SUMMARY_FILE
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(_json_safe(summary), f, ensure_ascii=False, indent=2)

    summary.update(
        {
            "knockout_bracket_filled_path": bracket_filled_path,
            "knockout_simulated_matches_path": simulated_matches_path,
            "single_tournament_result_path": single_result_path,
            "validation_report_path": validation_report_path,
            "knockout_simulation_summary_path": str(summary_path),
        }
    )

    return summary


if __name__ == "__main__":
    print(prepare_step13_knockout_simulation())
