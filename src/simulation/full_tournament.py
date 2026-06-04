"""Step 14 full tournament single-run simulation module."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.simulation.group_stage import (
    build_group_tables,
    create_group_stage_summary,
    rank_group_tables,
    select_group_qualifiers,
    simulate_group_stage,
    validate_group_stage_simulation,
)
from src.simulation.knockout_stage import (
    create_knockout_summary,
    simulate_knockout_stage,
    validate_knockout_simulation,
)
from src.tournament.fixtures import load_tournament_fixtures
import src.utils.constants as C

FULL_TOURNAMENT_RUN_TYPE_SINGLE = getattr(C, "FULL_TOURNAMENT_RUN_TYPE_SINGLE", "single_run")
FULL_TOURNAMENT_STAGE_GROUP = getattr(C, "FULL_TOURNAMENT_STAGE_GROUP", "group_stage")
FULL_TOURNAMENT_STAGE_KNOCKOUT = getattr(C, "FULL_TOURNAMENT_STAGE_KNOCKOUT", "knockout_stage")

TOURNAMENT_STAGE_ROUND_OF_32 = getattr(C, "TOURNAMENT_STAGE_ROUND_OF_32", "round_of_32")
TOURNAMENT_STAGE_ROUND_OF_16 = getattr(C, "TOURNAMENT_STAGE_ROUND_OF_16", "round_of_16")
TOURNAMENT_STAGE_QUARTER_FINAL = getattr(C, "TOURNAMENT_STAGE_QUARTER_FINAL", "quarter_final")
TOURNAMENT_STAGE_SEMI_FINAL = getattr(C, "TOURNAMENT_STAGE_SEMI_FINAL", "semi_final")
TOURNAMENT_STAGE_THIRD_PLACE = getattr(C, "TOURNAMENT_STAGE_THIRD_PLACE", "third_place")
TOURNAMENT_STAGE_FINAL = getattr(C, "TOURNAMENT_STAGE_FINAL", "final")


def _empty_df(columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=columns)


def run_group_stage_for_full_tournament(random_seed: int = 42) -> dict[str, Any]:
    """Run a fresh Step 12-like group-stage simulation for the full tournament flow."""
    fixtures_df = load_tournament_fixtures()
    simulated_group_matches = simulate_group_stage(fixtures_df=fixtures_df, random_seed=random_seed)
    group_tables = build_group_tables(simulated_group_matches)
    group_rankings = rank_group_tables(group_tables)

    automatic_qualifiers, best_third_placed, round_of_32_qualifiers = select_group_qualifiers(group_rankings)
    group_validation_passed, group_validation_report = validate_group_stage_simulation(
        simulated_matches_df=simulated_group_matches,
        ranked_tables_df=group_rankings,
        qualifiers_df=round_of_32_qualifiers,
    )

    group_summary = create_group_stage_summary(
        simulated_matches_df=simulated_group_matches,
        ranked_tables_df=group_rankings,
        automatic_qualifiers_df=automatic_qualifiers,
        best_third_df=best_third_placed,
        qualifiers_df=round_of_32_qualifiers,
        validation_passed=group_validation_passed,
        random_seed=random_seed,
    )

    return {
        "simulated_group_matches": simulated_group_matches,
        "group_tables": group_tables,
        "group_rankings": group_rankings,
        "automatic_qualifiers": automatic_qualifiers,
        "best_third_placed": best_third_placed,
        "round_of_32_qualifiers": round_of_32_qualifiers,
        "group_validation_passed": group_validation_passed,
        "group_validation_report": group_validation_report,
        "group_summary": group_summary,
    }


def run_knockout_stage_for_full_tournament(
    round_of_32_qualifiers: pd.DataFrame,
    random_seed: int = 42,
) -> dict[str, Any]:
    """Run Step 13 knockout simulation using in-memory fresh qualifiers."""
    knockout_result = simulate_knockout_stage(
        qualifiers_df=round_of_32_qualifiers,
        random_seed=random_seed,
    )
    knockout_validation_passed, knockout_validation_report = validate_knockout_simulation(
        simulated_matches_df=knockout_result["simulated_matches"],
        result_summary=knockout_result,
    )
    knockout_summary = create_knockout_summary(
        knockout_result,
        validation_passed=knockout_validation_passed,
        random_seed=random_seed,
    )

    return {
        "seeded_qualifiers": knockout_result["seeded_qualifiers"],
        "knockout_bracket_filled": knockout_result["bracket_filled"],
        "knockout_simulated_matches": knockout_result["simulated_matches"],
        "champion": knockout_result.get("champion"),
        "runner_up": knockout_result.get("runner_up"),
        "third_place": knockout_result.get("third_place"),
        "fourth_place": knockout_result.get("fourth_place"),
        "knockout_validation_passed": knockout_validation_passed,
        "knockout_validation_report": knockout_validation_report,
        "knockout_summary": knockout_summary,
    }


def create_full_tournament_stage_results(
    group_result: dict[str, Any],
    knockout_result: dict[str, Any],
) -> pd.DataFrame:
    """Create compact stage-level summary rows for the full tournament run."""
    knockout_matches = knockout_result.get("knockout_simulated_matches", pd.DataFrame())
    round_counts = (
        knockout_matches.groupby("round")["match_id"].count().to_dict()
        if isinstance(knockout_matches, pd.DataFrame) and not knockout_matches.empty and "round" in knockout_matches.columns
        else {}
    )

    rows = [
        {
            "stage": FULL_TOURNAMENT_STAGE_GROUP,
            "matches": int(len(group_result.get("simulated_group_matches", pd.DataFrame()))),
            "teams_in_stage": 48,
            "teams_advancing": 32,
            "winner_or_output": "Round-of-32 qualifiers selected",
            "validation_passed": bool(group_result.get("group_validation_passed", False)),
        },
        {
            "stage": TOURNAMENT_STAGE_ROUND_OF_32,
            "matches": int(round_counts.get(TOURNAMENT_STAGE_ROUND_OF_32, 0)),
            "teams_in_stage": 32,
            "teams_advancing": 16,
            "winner_or_output": "16 teams advance to round_of_16",
            "validation_passed": bool(knockout_result.get("knockout_validation_passed", False)),
        },
        {
            "stage": TOURNAMENT_STAGE_ROUND_OF_16,
            "matches": int(round_counts.get(TOURNAMENT_STAGE_ROUND_OF_16, 0)),
            "teams_in_stage": 16,
            "teams_advancing": 8,
            "winner_or_output": "8 teams advance to quarter_final",
            "validation_passed": bool(knockout_result.get("knockout_validation_passed", False)),
        },
        {
            "stage": TOURNAMENT_STAGE_QUARTER_FINAL,
            "matches": int(round_counts.get(TOURNAMENT_STAGE_QUARTER_FINAL, 0)),
            "teams_in_stage": 8,
            "teams_advancing": 4,
            "winner_or_output": "4 teams advance to semi_final",
            "validation_passed": bool(knockout_result.get("knockout_validation_passed", False)),
        },
        {
            "stage": TOURNAMENT_STAGE_SEMI_FINAL,
            "matches": int(round_counts.get(TOURNAMENT_STAGE_SEMI_FINAL, 0)),
            "teams_in_stage": 4,
            "teams_advancing": 2,
            "winner_or_output": "2 teams advance to final",
            "validation_passed": bool(knockout_result.get("knockout_validation_passed", False)),
        },
        {
            "stage": TOURNAMENT_STAGE_THIRD_PLACE,
            "matches": int(round_counts.get(TOURNAMENT_STAGE_THIRD_PLACE, 0)),
            "teams_in_stage": 2,
            "teams_advancing": 1,
            "winner_or_output": str(knockout_result.get("third_place", "unknown")),
            "validation_passed": bool(knockout_result.get("knockout_validation_passed", False)),
        },
        {
            "stage": TOURNAMENT_STAGE_FINAL,
            "matches": int(round_counts.get(TOURNAMENT_STAGE_FINAL, 0)),
            "teams_in_stage": 2,
            "teams_advancing": 1,
            "winner_or_output": str(knockout_result.get("champion", "unknown")),
            "validation_passed": bool(knockout_result.get("knockout_validation_passed", False)),
        },
    ]

    return pd.DataFrame(rows)


def create_full_tournament_path_report(
    group_result: dict[str, Any],
    knockout_result: dict[str, Any],
) -> pd.DataFrame:
    """Build a team-level tournament path report from group stage to final placements."""
    rankings = group_result.get("group_rankings", pd.DataFrame()).copy()
    if rankings.empty:
        return _empty_df(
            [
                "team",
                "group",
                "group_rank",
                "qualification_type",
                "points",
                "goal_difference",
                "goals_for",
                "reached_round",
                "final_position",
            ]
        )

    qualifiers = group_result.get("round_of_32_qualifiers", pd.DataFrame())
    qualifiers_lookup = qualifiers.set_index("team") if isinstance(qualifiers, pd.DataFrame) and not qualifiers.empty else pd.DataFrame()
    qualified_teams = set(qualifiers["team"].astype(str).tolist()) if isinstance(qualifiers, pd.DataFrame) and "team" in qualifiers.columns else set()

    report = rankings[["team", "group", "group_rank", "points", "goal_difference", "goals_for"]].copy()
    report["team"] = report["team"].astype(str)
    report["qualification_type"] = report["team"].map(
        lambda team: str(qualifiers_lookup.loc[team, "qualification_type"])
        if not qualifiers_lookup.empty and team in qualifiers_lookup.index
        else "eliminated_group_stage"
    )
    report["reached_round"] = report["team"].map(
        lambda team: TOURNAMENT_STAGE_ROUND_OF_32 if team in qualified_teams else FULL_TOURNAMENT_STAGE_GROUP
    )
    report["final_position"] = report["team"].map(
        lambda team: "eliminated_round_of_32" if team in qualified_teams else "eliminated_group_stage"
    )

    knockout_matches = knockout_result.get("knockout_simulated_matches", pd.DataFrame())
    if isinstance(knockout_matches, pd.DataFrame) and not knockout_matches.empty:
        elimination_mapping = {
            TOURNAMENT_STAGE_ROUND_OF_32: "eliminated_round_of_32",
            TOURNAMENT_STAGE_ROUND_OF_16: "eliminated_round_of_16",
            TOURNAMENT_STAGE_QUARTER_FINAL: "eliminated_quarter_final",
            TOURNAMENT_STAGE_SEMI_FINAL: "eliminated_semi_final",
        }
        for _, row in knockout_matches.sort_values(["round", "match_id"]).iterrows():
            loser = str(row.get("loser", ""))
            round_name = str(row.get("round", ""))
            if loser and loser in set(report["team"]):
                if round_name in elimination_mapping:
                    report.loc[report["team"] == loser, "reached_round"] = round_name
                    report.loc[report["team"] == loser, "final_position"] = elimination_mapping[round_name]

    champion = str(knockout_result.get("champion", ""))
    runner_up = str(knockout_result.get("runner_up", ""))
    third_place = str(knockout_result.get("third_place", ""))
    fourth_place = str(knockout_result.get("fourth_place", ""))

    if champion:
        report.loc[report["team"] == champion, ["reached_round", "final_position"]] = [TOURNAMENT_STAGE_FINAL, "champion"]
    if runner_up:
        report.loc[report["team"] == runner_up, ["reached_round", "final_position"]] = [TOURNAMENT_STAGE_FINAL, "runner_up"]
    if third_place:
        report.loc[report["team"] == third_place, ["reached_round", "final_position"]] = [TOURNAMENT_STAGE_THIRD_PLACE, "third_place"]
    if fourth_place:
        report.loc[report["team"] == fourth_place, ["reached_round", "final_position"]] = [TOURNAMENT_STAGE_THIRD_PLACE, "fourth_place"]

    return report.sort_values(["group", "group_rank", "team"]).reset_index(drop=True)


def create_full_tournament_match_log(
    group_matches: pd.DataFrame,
    knockout_matches: pd.DataFrame,
) -> pd.DataFrame:
    """Combine group-stage and knockout-stage match logs into one normalized table."""
    normalized_columns = [
        "stage",
        "round",
        "match_id",
        "group",
        "matchday",
        "date",
        "team_a",
        "team_b",
        "team_a_score",
        "team_b_score",
        "simulated_result",
        "winner",
        "loser",
        "model_type",
        "outcome_method",
    ]

    group_df = group_matches.copy() if isinstance(group_matches, pd.DataFrame) else pd.DataFrame()
    if not group_df.empty:
        group_df = group_df.assign(
            stage=FULL_TOURNAMENT_STAGE_GROUP,
            round=FULL_TOURNAMENT_STAGE_GROUP,
            loser=None,
            outcome_method="regular_time",
            simulated_result=group_df.get("simulated_result"),
            team_a_score=group_df.get("team_a_score"),
            team_b_score=group_df.get("team_b_score"),
        )
    else:
        group_df = _empty_df(normalized_columns)

    knockout_df = knockout_matches.copy() if isinstance(knockout_matches, pd.DataFrame) else pd.DataFrame()
    if not knockout_df.empty:
        knockout_df = knockout_df.assign(
            stage=FULL_TOURNAMENT_STAGE_KNOCKOUT,
            round=knockout_df.get("round"),
            group=None,
            matchday=None,
            simulated_result=knockout_df.get("normal_time_result"),
            team_a_score=knockout_df.get("simulated_team_a_score"),
            team_b_score=knockout_df.get("simulated_team_b_score"),
            outcome_method=knockout_df.get("outcome_method"),
        )
    else:
        knockout_df = _empty_df(normalized_columns)

    for column in normalized_columns:
        if column not in group_df.columns:
            group_df[column] = None
        if column not in knockout_df.columns:
            knockout_df[column] = None

    full_df = pd.concat(
        [group_df[normalized_columns], knockout_df[normalized_columns]],
        ignore_index=True,
    )
    return full_df


def validate_full_tournament(
    group_result: dict[str, Any],
    knockout_result: dict[str, Any],
    full_match_log: pd.DataFrame,
    path_report: pd.DataFrame,
) -> tuple[bool, pd.DataFrame]:
    """Validate full-tournament outputs for Step 14."""
    checks: list[dict[str, Any]] = []

    def _add(check: str, expected: Any, actual: Any, passed: bool) -> None:
        checks.append({"check": check, "expected": expected, "actual": actual, "passed": bool(passed)})

    group_matches = group_result.get("simulated_group_matches", pd.DataFrame())
    knockout_matches = knockout_result.get("knockout_simulated_matches", pd.DataFrame())
    qualifiers = group_result.get("round_of_32_qualifiers", pd.DataFrame())

    _add("group_validation_passed", True, bool(group_result.get("group_validation_passed", False)), bool(group_result.get("group_validation_passed", False)))
    _add("knockout_validation_passed", True, bool(knockout_result.get("knockout_validation_passed", False)), bool(knockout_result.get("knockout_validation_passed", False)))
    _add("group_matches_count", 72, int(len(group_matches)), int(len(group_matches)) == 72)
    _add("knockout_matches_count", 32, int(len(knockout_matches)), int(len(knockout_matches)) == 32)
    _add("full_match_log_count", 104, int(len(full_match_log)), int(len(full_match_log)) == 104)
    _add("round_of_32_qualifiers_count", 32, int(len(qualifiers)), int(len(qualifiers)) == 32)

    champion = knockout_result.get("champion")
    runner_up = knockout_result.get("runner_up")
    third_place = knockout_result.get("third_place")
    _add("champion_exists", True, bool(champion), bool(champion))
    _add("runner_up_exists", True, bool(runner_up), bool(runner_up))
    _add("third_place_exists", True, bool(third_place), bool(third_place))

    _add("path_report_team_count", 48, int(len(path_report)), int(len(path_report)) == 48)
    if not path_report.empty and "final_position" in path_report.columns:
        champion_count = int((path_report["final_position"] == "champion").sum())
        runner_up_count = int((path_report["final_position"] == "runner_up").sum())
        third_place_count = int((path_report["final_position"] == "third_place").sum())
    else:
        champion_count = runner_up_count = third_place_count = 0

    _add("exactly_one_champion", 1, champion_count, champion_count == 1)
    _add("exactly_one_runner_up", 1, runner_up_count, runner_up_count == 1)
    _add("exactly_one_third_place", 1, third_place_count, third_place_count == 1)

    report_df = pd.DataFrame(checks)
    return bool(report_df["passed"].all()) if not report_df.empty else False, report_df


def create_full_tournament_summary(
    group_result: dict[str, Any],
    knockout_result: dict[str, Any],
    full_validation_passed: bool,
    random_seed: int,
) -> dict[str, Any]:
    """Create high-level summary payload for Step 14 full single-run simulation."""
    group_matches = group_result.get("simulated_group_matches", pd.DataFrame())
    knockout_matches = knockout_result.get("knockout_simulated_matches", pd.DataFrame())

    return {
        "status": "ok" if full_validation_passed else "validation_failed",
        "run_type": FULL_TOURNAMENT_RUN_TYPE_SINGLE,
        "random_seed": int(random_seed),
        "validation_passed": bool(full_validation_passed),
        "group_validation_passed": bool(group_result.get("group_validation_passed", False)),
        "knockout_validation_passed": bool(knockout_result.get("knockout_validation_passed", False)),
        "total_matches": int(len(group_matches) + len(knockout_matches)),
        "group_stage_matches": int(len(group_matches)),
        "knockout_matches": int(len(knockout_matches)),
        "champion": knockout_result.get("champion"),
        "runner_up": knockout_result.get("runner_up"),
        "third_place": knockout_result.get("third_place"),
        "fourth_place": knockout_result.get("fourth_place"),
        "round_of_32_qualifiers": int(len(group_result.get("round_of_32_qualifiers", pd.DataFrame()))),
        "notes": [
            "This is one sampled tournament path, not a probability forecast. Monte Carlo simulation will be added in Step 15.",
        ],
    }


def run_full_tournament_single(random_seed: int = 42) -> dict[str, Any]:
    """Run one complete sampled tournament from group stage through final."""
    group_result = run_group_stage_for_full_tournament(random_seed=random_seed)
    knockout_seed = int(random_seed) + 1
    knockout_result = run_knockout_stage_for_full_tournament(
        round_of_32_qualifiers=group_result["round_of_32_qualifiers"],
        random_seed=knockout_seed,
    )

    full_match_log = create_full_tournament_match_log(
        group_matches=group_result["simulated_group_matches"],
        knockout_matches=knockout_result["knockout_simulated_matches"],
    )
    stage_results = create_full_tournament_stage_results(group_result, knockout_result)
    path_report = create_full_tournament_path_report(group_result, knockout_result)

    full_validation_passed, full_validation_report = validate_full_tournament(
        group_result=group_result,
        knockout_result=knockout_result,
        full_match_log=full_match_log,
        path_report=path_report,
    )
    summary = create_full_tournament_summary(
        group_result=group_result,
        knockout_result=knockout_result,
        full_validation_passed=full_validation_passed,
        random_seed=random_seed,
    )

    return {
        "group_result": group_result,
        "knockout_result": knockout_result,
        "full_match_log": full_match_log,
        "stage_results": stage_results,
        "path_report": path_report,
        "full_validation_report": full_validation_report,
        "summary": summary,
    }
