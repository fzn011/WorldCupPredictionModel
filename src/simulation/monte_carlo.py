"""Step 15 Monte Carlo full-tournament simulation utilities."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.models.prediction_cache import CachedMatchPredictor
from src.simulation.full_tournament import run_full_tournament_single
import src.utils.constants as C

TOURNAMENT_STAGE_GROUP = getattr(C, "TOURNAMENT_STAGE_GROUP", "group_stage")
TOURNAMENT_STAGE_ROUND_OF_32 = getattr(C, "TOURNAMENT_STAGE_ROUND_OF_32", "round_of_32")
TOURNAMENT_STAGE_ROUND_OF_16 = getattr(C, "TOURNAMENT_STAGE_ROUND_OF_16", "round_of_16")
TOURNAMENT_STAGE_QUARTER_FINAL = getattr(C, "TOURNAMENT_STAGE_QUARTER_FINAL", "quarter_final")
TOURNAMENT_STAGE_SEMI_FINAL = getattr(C, "TOURNAMENT_STAGE_SEMI_FINAL", "semi_final")
TOURNAMENT_STAGE_THIRD_PLACE = getattr(C, "TOURNAMENT_STAGE_THIRD_PLACE", "third_place")
TOURNAMENT_STAGE_FINAL = getattr(C, "TOURNAMENT_STAGE_FINAL", "final")

DEFAULT_MONTE_CARLO_SIMULATIONS = int(getattr(C, "DEFAULT_MONTE_CARLO_SIMULATIONS", 100))
DEFAULT_MONTE_CARLO_SEED = int(getattr(C, "DEFAULT_MONTE_CARLO_SEED", 42))
MAX_MONTE_CARLO_SIMULATIONS = int(getattr(C, "MAX_MONTE_CARLO_SIMULATIONS", 5000))

_INVALID_TEAM_TOKENS = frozenset({"", "none", "nan", "nat", "<na>", "null"})


def _is_valid_team_name(value: Any) -> bool:
    """Return True when value is a usable team label for aggregation tables."""
    if value is None:
        return False
    if isinstance(value, float) and pd.isna(value):
        return False
    token = str(value).strip()
    if not token:
        return False
    return token.lower() not in _INVALID_TEAM_TOKENS

MONTE_CARLO_STAGE_COLUMNS = list(
    getattr(
        C,
        "MONTE_CARLO_STAGE_COLUMNS",
        [
            "group_stage",
            "round_of_32",
            "round_of_16",
            "quarter_final",
            "semi_final",
            "final",
            "champion",
        ],
    )
)


def run_single_tournament_for_monte_carlo(
    simulation_id: int,
    random_seed: int,
    predictor: Any | None = None,
) -> dict[str, Any]:
    """Run one full tournament simulation for Monte Carlo and extract key outputs."""
    try:
        result = run_full_tournament_single(random_seed=int(random_seed), predictor=predictor)
        summary = dict(result.get("summary", {}))
        return {
            "simulation_id": int(simulation_id),
            "random_seed": int(random_seed),
            "status": "success",
            "validation_passed": bool(summary.get("validation_passed", False)),
            "champion": summary.get("champion"),
            "runner_up": summary.get("runner_up"),
            "third_place": summary.get("third_place"),
            "fourth_place": summary.get("fourth_place"),
            "summary": summary,
            "path_report": result.get("path_report", pd.DataFrame()),
            "stage_results": result.get("stage_results", pd.DataFrame()),
            "error_message": None,
        }
    except Exception as exc:  # pragma: no cover - safety path
        return {
            "simulation_id": int(simulation_id),
            "random_seed": int(random_seed),
            "status": "failed",
            "validation_passed": False,
            "champion": None,
            "runner_up": None,
            "third_place": None,
            "fourth_place": None,
            "summary": {},
            "path_report": pd.DataFrame(),
            "stage_results": pd.DataFrame(),
            "error_message": str(exc),
        }


def run_monte_carlo_simulations(
    num_simulations: int = DEFAULT_MONTE_CARLO_SIMULATIONS,
    base_seed: int = DEFAULT_MONTE_CARLO_SEED,
    predictor: Any | None = None,
) -> dict[str, Any]:
    """Run repeated full-tournament simulations with resilient error handling."""
    num_simulations = int(max(1, num_simulations))
    base_seed = int(base_seed)
    shared_predictor = predictor if predictor is not None else CachedMatchPredictor()

    simulation_results: list[dict[str, Any]] = []
    path_reports: list[dict[str, Any]] = []
    stage_results: list[dict[str, Any]] = []

    for simulation_id in range(1, num_simulations + 1):
        derived_seed = base_seed + simulation_id
        single = run_single_tournament_for_monte_carlo(
            simulation_id=simulation_id,
            random_seed=derived_seed,
            predictor=shared_predictor,
        )

        simulation_results.append(single)

        if single.get("status") == "success":
            path_reports.append(
                {
                    "simulation_id": simulation_id,
                    "random_seed": derived_seed,
                    "path_report": single.get("path_report", pd.DataFrame()),
                }
            )
            stage_results.append(
                {
                    "simulation_id": simulation_id,
                    "random_seed": derived_seed,
                    "stage_results": single.get("stage_results", pd.DataFrame()),
                }
            )

        if num_simulations <= 20 or simulation_id % 10 == 0 or simulation_id == num_simulations:
            successful_so_far = sum(1 for row in simulation_results if row.get("status") == "success")
            print(
                f"[monte-carlo] completed {simulation_id}/{num_simulations} "
                f"(success={successful_so_far}, failed={simulation_id - successful_so_far})"
            )

    cache_info = shared_predictor.cache_info() if hasattr(shared_predictor, "cache_info") else {}

    return {
        "simulation_results": simulation_results,
        "path_reports": path_reports,
        "stage_results": stage_results,
        "cache_info": cache_info,
    }


def build_simulation_results_table(simulation_results: list[dict[str, Any]]) -> pd.DataFrame:
    """Create a flat per-simulation outcome table."""
    rows: list[dict[str, Any]] = []
    for result in simulation_results:
        rows.append(
            {
                "simulation_id": int(result.get("simulation_id", 0)),
                "random_seed": int(result.get("random_seed", 0)),
                "status": str(result.get("status", "failed")),
                "validation_passed": bool(result.get("validation_passed", False)),
                "champion": result.get("champion"),
                "runner_up": result.get("runner_up"),
                "third_place": result.get("third_place"),
                "fourth_place": result.get("fourth_place"),
                "error_message": result.get("error_message"),
            }
        )
    return pd.DataFrame(rows)


def _stage_level_from_row(row: pd.Series) -> int:
    reached_round = str(row.get("reached_round", TOURNAMENT_STAGE_GROUP))
    final_position = str(row.get("final_position", ""))

    if final_position == "champion":
        return 6

    if reached_round == TOURNAMENT_STAGE_FINAL:
        return 5
    if reached_round in {TOURNAMENT_STAGE_SEMI_FINAL, TOURNAMENT_STAGE_THIRD_PLACE}:
        return 4
    if reached_round == TOURNAMENT_STAGE_QUARTER_FINAL:
        return 3
    if reached_round == TOURNAMENT_STAGE_ROUND_OF_16:
        return 2
    if reached_round == TOURNAMENT_STAGE_ROUND_OF_32:
        return 1
    return 0


def build_team_stage_counts(path_reports: list[dict[str, Any] | pd.DataFrame]) -> pd.DataFrame:
    """Aggregate per-team stage reach counts across successful simulations."""
    rows: list[dict[str, Any]] = []

    for idx, payload in enumerate(path_reports, start=1):
        if isinstance(payload, dict):
            simulation_id = int(payload.get("simulation_id", idx))
            path_report = payload.get("path_report", pd.DataFrame())
        else:
            simulation_id = idx
            path_report = payload

        if not isinstance(path_report, pd.DataFrame) or path_report.empty:
            continue

        team_col_present = "team" in path_report.columns
        if not team_col_present:
            continue

        for _, row in path_report.iterrows():
            team = str(row.get("team", "")).strip()
            if not _is_valid_team_name(team):
                continue
            stage_level = _stage_level_from_row(row)
            rows.append(
                {
                    "simulation_id": simulation_id,
                    "team": team,
                    "group_stage": 1,
                    "round_of_32": int(stage_level >= 1),
                    "round_of_16": int(stage_level >= 2),
                    "quarter_final": int(stage_level >= 3),
                    "semi_final": int(stage_level >= 4),
                    "final": int(stage_level >= 5),
                    "champion": int(stage_level >= 6),
                }
            )

    if not rows:
        return pd.DataFrame(
            columns=[
                "team",
                "simulations",
                "group_stage_count",
                "round_of_32_count",
                "round_of_16_count",
                "quarter_final_count",
                "semi_final_count",
                "final_count",
                "champion_count",
            ]
        )

    expanded = pd.DataFrame(rows)
    grouped = (
        expanded.groupby("team", as_index=False)
        .agg(
            simulations=("simulation_id", "nunique"),
            group_stage_count=("group_stage", "sum"),
            round_of_32_count=("round_of_32", "sum"),
            round_of_16_count=("round_of_16", "sum"),
            quarter_final_count=("quarter_final", "sum"),
            semi_final_count=("semi_final", "sum"),
            final_count=("final", "sum"),
            champion_count=("champion", "sum"),
        )
        .sort_values(["champion_count", "final_count", "semi_final_count", "team"], ascending=[False, False, False, True])
        .reset_index(drop=True)
    )
    return grouped


def build_team_stage_probabilities(stage_counts_df: pd.DataFrame, successful_simulations: int) -> pd.DataFrame:
    """Convert stage counts to stage progression probabilities."""
    successful_simulations = int(max(1, successful_simulations))

    if stage_counts_df.empty:
        return pd.DataFrame(
            columns=[
                "team",
                "simulations",
                "group_stage_count",
                "round_of_32_count",
                "round_of_16_count",
                "quarter_final_count",
                "semi_final_count",
                "final_count",
                "champion_count",
                "round_of_32_probability",
                "round_of_16_probability",
                "quarter_final_probability",
                "semi_final_probability",
                "final_probability",
                "champion_probability",
            ]
        )

    df = stage_counts_df.copy()
    df["simulations"] = successful_simulations
    df["round_of_32_probability"] = df["round_of_32_count"] / successful_simulations
    df["round_of_16_probability"] = df["round_of_16_count"] / successful_simulations
    df["quarter_final_probability"] = df["quarter_final_count"] / successful_simulations
    df["semi_final_probability"] = df["semi_final_count"] / successful_simulations
    df["final_probability"] = df["final_count"] / successful_simulations
    df["champion_probability"] = df["champion_count"] / successful_simulations

    return df.sort_values(["champion_probability", "final_probability", "team"], ascending=[False, False, True]).reset_index(drop=True)


def build_champion_probabilities(simulation_results_df: pd.DataFrame) -> pd.DataFrame:
    """Build champion frequency/probability table from successful simulations."""
    if simulation_results_df.empty:
        return pd.DataFrame(columns=["team", "champion_count", "champion_probability"])

    successful = simulation_results_df.loc[
        (simulation_results_df["status"] == "success")
        & simulation_results_df["champion"].apply(_is_valid_team_name)
    ].copy()
    if successful.empty:
        return pd.DataFrame(columns=["team", "champion_count", "champion_probability"])

    total = len(successful)
    counts = (
        successful["champion"]
        .astype(str)
        .value_counts(dropna=False)
        .rename_axis("team")
        .reset_index(name="champion_count")
    )
    counts["champion_probability"] = counts["champion_count"] / total
    return counts.sort_values(["champion_probability", "champion_count", "team"], ascending=[False, False, True]).reset_index(drop=True)


def build_finalists_table(simulation_results_df: pd.DataFrame) -> pd.DataFrame:
    """Build finalists frequency table from champion and runner-up outcomes."""
    if simulation_results_df.empty:
        return pd.DataFrame(
            columns=[
                "team",
                "champion_count",
                "runner_up_count",
                "final_appearance_count",
                "final_appearance_probability",
                "champion_probability",
            ]
        )

    successful = simulation_results_df.loc[simulation_results_df["status"] == "success"].copy()
    if successful.empty:
        return pd.DataFrame(
            columns=[
                "team",
                "champion_count",
                "runner_up_count",
                "final_appearance_count",
                "final_appearance_probability",
                "champion_probability",
            ]
        )

    total = len(successful)
    champion_counts = (
        successful.loc[successful["champion"].apply(_is_valid_team_name), "champion"]
        .astype(str)
        .value_counts()
        .to_dict()
    )
    runner_counts = (
        successful.loc[successful["runner_up"].apply(_is_valid_team_name), "runner_up"]
        .astype(str)
        .value_counts()
        .to_dict()
    )

    teams = sorted(set(champion_counts.keys()).union(set(runner_counts.keys())))
    rows = []
    for team in teams:
        if not _is_valid_team_name(team):
            continue
        champ = int(champion_counts.get(team, 0))
        runner = int(runner_counts.get(team, 0))
        finals = champ + runner
        rows.append(
            {
                "team": team,
                "champion_count": champ,
                "runner_up_count": runner,
                "final_appearance_count": finals,
                "final_appearance_probability": finals / total,
                "champion_probability": champ / total,
            }
        )

    return pd.DataFrame(rows).sort_values(["final_appearance_probability", "champion_probability", "team"], ascending=[False, False, True]).reset_index(drop=True)


def build_semifinalists_table(path_reports: list[dict[str, Any] | pd.DataFrame], successful_simulations: int) -> pd.DataFrame:
    """Build semifinal appearance frequencies from path reports."""
    successful_simulations = int(max(1, successful_simulations))
    rows: list[str] = []

    for payload in path_reports:
        if isinstance(payload, dict):
            path_report = payload.get("path_report", pd.DataFrame())
        else:
            path_report = payload

        if not isinstance(path_report, pd.DataFrame) or path_report.empty or "team" not in path_report.columns:
            continue

        df = path_report.copy()
        stage_levels = df.apply(_stage_level_from_row, axis=1)
        semifinal_teams = df.loc[stage_levels >= 4, "team"].astype(str).tolist()
        rows.extend([team for team in semifinal_teams if _is_valid_team_name(team)])

    if not rows:
        return pd.DataFrame(columns=["team", "semifinal_count", "semifinal_probability"])

    counts = pd.Series(rows).value_counts().rename_axis("team").reset_index(name="semifinal_count")
    counts["semifinal_probability"] = counts["semifinal_count"] / successful_simulations
    return counts.sort_values(["semifinal_probability", "semifinal_count", "team"], ascending=[False, False, True]).reset_index(drop=True)


def validate_monte_carlo_outputs(
    simulation_results_df: pd.DataFrame,
    team_stage_probabilities_df: pd.DataFrame,
    champion_probabilities_df: pd.DataFrame,
    num_simulations: int,
) -> tuple[bool, pd.DataFrame]:
    """Validate key Monte Carlo output consistency and probability sanity."""
    checks: list[dict[str, Any]] = []

    def _add(check: str, expected: Any, actual: Any, passed: bool) -> None:
        checks.append({"check": check, "expected": expected, "actual": actual, "passed": bool(passed)})

    num_simulations = int(max(1, num_simulations))

    rows_count = int(len(simulation_results_df))
    _add("simulation_results_row_count", num_simulations, rows_count, rows_count == num_simulations)

    successful_df = simulation_results_df.loc[simulation_results_df.get("status", pd.Series(dtype=str)) == "success"].copy() if not simulation_results_df.empty else pd.DataFrame()
    successful_count = int(len(successful_df))
    _add("at_least_one_successful_simulation", ">=1", successful_count, successful_count >= 1)

    successful_champions = (
        int(successful_df["champion"].apply(_is_valid_team_name).sum())
        if not successful_df.empty and "champion" in successful_df.columns
        else 0
    )
    _add("every_success_has_champion", successful_count, successful_champions, successful_champions == successful_count)

    champion_probability_sum = float(champion_probabilities_df["champion_probability"].sum()) if not champion_probabilities_df.empty else 0.0
    sum_close = bool(np.isclose(champion_probability_sum, 1.0, atol=1e-6)) if successful_count > 0 and not champion_probabilities_df.empty else successful_count == 0
    _add("champion_probabilities_sum_close_to_1", "~1.0", round(champion_probability_sum, 8), sum_close)

    has_stage_rows = int(len(team_stage_probabilities_df))
    _add("team_stage_probabilities_has_rows", ">=1", has_stage_rows, has_stage_rows >= 1)

    if not champion_probabilities_df.empty and "champion_probability" in champion_probabilities_df.columns:
        min_prob = float(champion_probabilities_df["champion_probability"].min())
        max_prob = float(champion_probabilities_df["champion_probability"].max())
        in_range = 0.0 <= min_prob <= 1.0 and 0.0 <= max_prob <= 1.0
    else:
        min_prob = max_prob = -1.0
        in_range = False
    _add("champion_probability_in_range", "0<=p<=1", f"min={min_prob:.6f}, max={max_prob:.6f}", in_range)

    report_df = pd.DataFrame(checks)
    return (bool(report_df["passed"].all()) if not report_df.empty else False), report_df


def create_monte_carlo_summary(
    simulation_results_df: pd.DataFrame,
    champion_probabilities_df: pd.DataFrame,
    team_stage_probabilities_df: pd.DataFrame,
    validation_passed: bool,
    num_simulations: int,
    base_seed: int,
    cache_info: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create high-level Monte Carlo summary payload."""
    num_simulations = int(max(1, num_simulations))
    base_seed = int(base_seed)

    successful_simulations = int((simulation_results_df["status"] == "success").sum()) if not simulation_results_df.empty and "status" in simulation_results_df.columns else 0
    failed_simulations = int(num_simulations - successful_simulations)

    top_champion = None
    top_champion_probability = 0.0
    if not champion_probabilities_df.empty:
        top_champion = champion_probabilities_df.iloc[0]["team"]
        top_champion_probability = float(champion_probabilities_df.iloc[0]["champion_probability"])

    top_finalist = None
    if not team_stage_probabilities_df.empty and "final_probability" in team_stage_probabilities_df.columns:
        top_finalist = team_stage_probabilities_df.sort_values(["final_probability", "champion_probability"], ascending=[False, False]).iloc[0]["team"]

    return {
        "status": "ok" if validation_passed else "validation_failed",
        "num_simulations": num_simulations,
        "successful_simulations": successful_simulations,
        "failed_simulations": failed_simulations,
        "base_seed": base_seed,
        "validation_passed": bool(validation_passed),
        "top_champion": top_champion,
        "top_champion_probability": top_champion_probability,
        "top_finalist": top_finalist,
        "cache_info": cache_info or {},
        "notes": [
            "Monte Carlo probabilities are estimated from repeated sampled tournament simulations. They are not certainties and depend on model quality, fixture assumptions, and sample size.",
        ],
    }
