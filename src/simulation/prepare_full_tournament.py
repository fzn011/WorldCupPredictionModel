"""Step 14 full-tournament single-run preparation orchestrator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.simulation.full_tournament import run_full_tournament_single
import src.utils.constants as C

PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")
FULL_TOURNAMENT_SIMULATED_MATCHES_FILE = getattr(C, "FULL_TOURNAMENT_SIMULATED_MATCHES_FILE", "full_tournament_simulated_matches.csv")
FULL_TOURNAMENT_GROUP_TABLES_FILE = getattr(C, "FULL_TOURNAMENT_GROUP_TABLES_FILE", "full_tournament_group_tables.csv")
FULL_TOURNAMENT_KNOCKOUT_MATCHES_FILE = getattr(C, "FULL_TOURNAMENT_KNOCKOUT_MATCHES_FILE", "full_tournament_knockout_matches.csv")
FULL_TOURNAMENT_STAGE_RESULTS_FILE = getattr(C, "FULL_TOURNAMENT_STAGE_RESULTS_FILE", "full_tournament_stage_results.csv")
FULL_TOURNAMENT_PATH_REPORT_FILE = getattr(C, "FULL_TOURNAMENT_PATH_REPORT_FILE", "full_tournament_path_report.csv")
FULL_TOURNAMENT_RESULT_FILE = getattr(C, "FULL_TOURNAMENT_RESULT_FILE", "single_world_cup_result.json")
FULL_TOURNAMENT_SUMMARY_FILE = getattr(C, "FULL_TOURNAMENT_SUMMARY_FILE", "full_tournament_summary.json")
FULL_TOURNAMENT_VALIDATION_REPORT_FILE = getattr(C, "FULL_TOURNAMENT_VALIDATION_REPORT_FILE", "full_tournament_validation_report.csv")


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


def prepare_step14_full_tournament_single_run(random_seed: int = 42) -> dict[str, Any]:
    """Run Step 14 full single-run tournament orchestration and persist outputs."""
    result = run_full_tournament_single(random_seed=random_seed)
    summary = dict(result.get("summary", {}))

    full_matches_path = _save_csv(result["full_match_log"], FULL_TOURNAMENT_SIMULATED_MATCHES_FILE)
    group_tables_path = _save_csv(result["group_result"]["group_rankings"], FULL_TOURNAMENT_GROUP_TABLES_FILE)
    knockout_matches_path = _save_csv(result["knockout_result"]["knockout_simulated_matches"], FULL_TOURNAMENT_KNOCKOUT_MATCHES_FILE)
    stage_results_path = _save_csv(result["stage_results"], FULL_TOURNAMENT_STAGE_RESULTS_FILE)
    path_report_path = _save_csv(result["path_report"], FULL_TOURNAMENT_PATH_REPORT_FILE)
    validation_report_path = _save_csv(result["full_validation_report"], FULL_TOURNAMENT_VALIDATION_REPORT_FILE)

    single_world_cup_payload = {
        "random_seed": int(random_seed),
        "champion": summary.get("champion"),
        "runner_up": summary.get("runner_up"),
        "third_place": summary.get("third_place"),
        "fourth_place": summary.get("fourth_place"),
        "group_summary": result["group_result"].get("group_summary", {}),
        "knockout_summary": result["knockout_result"].get("knockout_summary", {}),
        "stage_results": result["stage_results"],
        "path_report": result["path_report"],
        "full_validation_report": result["full_validation_report"],
        "summary": summary,
    }
    result_json_path = _save_json(single_world_cup_payload, FULL_TOURNAMENT_RESULT_FILE)
    summary_json_path = _save_json(summary, FULL_TOURNAMENT_SUMMARY_FILE)

    summary.update(
        {
            "full_tournament_matches_path": full_matches_path,
            "full_tournament_group_tables_path": group_tables_path,
            "full_tournament_knockout_matches_path": knockout_matches_path,
            "full_tournament_stage_results_path": stage_results_path,
            "full_tournament_path_report_path": path_report_path,
            "full_tournament_result_path": result_json_path,
            "full_tournament_summary_path": summary_json_path,
            "validation_report_path": validation_report_path,
        }
    )

    return summary


if __name__ == "__main__":
    print(prepare_step14_full_tournament_single_run())
