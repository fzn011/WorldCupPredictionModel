"""Step 17 World Cup awards preparation orchestrator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.awards.award_reports import (
    create_combined_awards_table,
    create_world_cup_awards_markdown_report,
    create_world_cup_awards_summary,
    save_awards_report,
)
from src.awards.player_awards import (
    add_team_progression_to_players,
    calculate_golden_ball_predictions,
    calculate_golden_boot_predictions,
    calculate_golden_glove_predictions,
    calculate_goal_of_tournament_proxy,
    calculate_player_of_match_proxy,
    calculate_young_player_predictions,
    load_player_candidates,
    load_team_stage_probabilities,
    validate_player_candidates,
)
from src.awards.team_awards import (
    add_team_stage_to_award_profiles,
    calculate_fair_play_predictions,
    calculate_most_entertaining_team_predictions,
    load_team_award_profiles,
    validate_team_award_profiles,
)
from src.awards.team_of_tournament import select_team_of_tournament
import src.utils.constants as C

PROJECT_ROOT = getattr(C, "PROJECT_ROOT", Path(__file__).resolve().parents[2])
PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", PROJECT_ROOT / "data" / "processed")

WORLD_CUP_AWARDS_PREDICTIONS_FILE = getattr(C, "WORLD_CUP_AWARDS_PREDICTIONS_FILE", "world_cup_awards_predictions.csv")
GOLDEN_BALL_PREDICTIONS_FILE = getattr(C, "GOLDEN_BALL_PREDICTIONS_FILE", "golden_ball_predictions.csv")
GOLDEN_BOOT_PREDICTIONS_FILE = getattr(C, "GOLDEN_BOOT_PREDICTIONS_FILE", "golden_boot_predictions.csv")
GOLDEN_GLOVE_PREDICTIONS_FILE = getattr(C, "GOLDEN_GLOVE_PREDICTIONS_FILE", "golden_glove_predictions.csv")
YOUNG_PLAYER_PREDICTIONS_FILE = getattr(C, "YOUNG_PLAYER_PREDICTIONS_FILE", "young_player_predictions.csv")
FAIR_PLAY_PREDICTIONS_FILE = getattr(C, "FAIR_PLAY_PREDICTIONS_FILE", "fair_play_predictions.csv")
MOST_ENTERTAINING_TEAM_PREDICTIONS_FILE = getattr(C, "MOST_ENTERTAINING_TEAM_PREDICTIONS_FILE", "most_entertaining_team_predictions.csv")
TEAM_OF_THE_TOURNAMENT_FILE = getattr(C, "TEAM_OF_THE_TOURNAMENT_FILE", "team_of_the_tournament.csv")
PLAYER_OF_THE_MATCH_PROXY_FILE = getattr(C, "PLAYER_OF_THE_MATCH_PROXY_FILE", "player_of_the_match_proxy.csv")
GOAL_OF_THE_TOURNAMENT_PROXY_FILE = getattr(C, "GOAL_OF_THE_TOURNAMENT_PROXY_FILE", "goal_of_the_tournament_proxy.csv")
WORLD_CUP_AWARDS_SUMMARY_FILE = getattr(C, "WORLD_CUP_AWARDS_SUMMARY_FILE", "world_cup_awards_summary.json")
WORLD_CUP_AWARDS_VALIDATION_REPORT_FILE = getattr(C, "WORLD_CUP_AWARDS_VALIDATION_REPORT_FILE", "world_cup_awards_validation_report.csv")


def _save_csv(df: pd.DataFrame, file_name: str) -> str:
    path = PROCESSED_DATA_DIR / file_name
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return str(path)



def _save_json(payload: dict[str, Any], file_name: str) -> str:
    path = PROCESSED_DATA_DIR / file_name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return str(path)



def _validate_outputs(outputs: dict[str, pd.DataFrame]) -> tuple[bool, pd.DataFrame]:
    checks: list[dict[str, Any]] = []

    golden_ball = outputs.get("golden_ball", pd.DataFrame())
    golden_boot = outputs.get("golden_boot", pd.DataFrame())
    golden_glove = outputs.get("golden_glove", pd.DataFrame())
    young_player = outputs.get("young_player", pd.DataFrame())
    team_of_tournament = outputs.get("team_of_tournament", pd.DataFrame())
    fair_play = outputs.get("fair_play", pd.DataFrame())
    entertaining = outputs.get("most_entertaining", pd.DataFrame())

    gb_sum = float(golden_ball.get("golden_ball_probability", pd.Series(dtype=float)).sum()) if not golden_ball.empty else 0.0
    boot_sum = float(golden_boot.get("golden_boot_probability", pd.Series(dtype=float)).sum()) if not golden_boot.empty else 0.0
    glove_only_gk = bool((golden_glove.get("position", pd.Series(dtype=str)).astype(str).str.lower() == "goalkeeper").all()) if not golden_glove.empty else True
    young_ok = True
    if not young_player.empty:
        dob = pd.to_datetime(young_player.get("date_of_birth"), errors="coerce")
        age = pd.to_numeric(young_player.get("age"), errors="coerce").fillna(999)
        young_ok = bool((dob.ge(pd.Timestamp(str(getattr(C, "YOUNG_PLAYER_CUTOFF_DATE_2026", "2005-01-01"))) ) | age.le(21)).all())

    position_counts = team_of_tournament.get("position", pd.Series(dtype=str)).astype(str).str.lower().value_counts() if not team_of_tournament.empty else pd.Series(dtype=int)
    formation_ok = (
        len(team_of_tournament) == 11
        and int(position_counts.get("goalkeeper", 0)) == 1
        and int(position_counts.get("defender", 0)) == 4
        and int(position_counts.get("midfielder", 0)) == 3
        and int(position_counts.get("forward", 0)) == 3
    )

    checks.extend(
        [
            {"check": "golden_ball_probabilities_sum", "expected": "~1.0", "actual": gb_sum, "passed": abs(gb_sum - 1.0) < 1e-6},
            {"check": "golden_boot_probabilities_sum", "expected": "~1.0", "actual": boot_sum, "passed": abs(boot_sum - 1.0) < 1e-6},
            {"check": "golden_glove_goalkeepers_only", "expected": "all goalkeepers", "actual": glove_only_gk, "passed": glove_only_gk},
            {"check": "young_player_eligibility", "expected": "all eligible", "actual": young_ok, "passed": young_ok},
            {"check": "team_of_tournament_size", "expected": 11, "actual": int(len(team_of_tournament)), "passed": len(team_of_tournament) == 11},
            {"check": "team_of_tournament_formation", "expected": "1 GK / 4 DEF / 3 MID / 3 FWD", "actual": position_counts.to_dict(), "passed": formation_ok},
            {"check": "fair_play_output_exists", "expected": ">=1 row", "actual": int(len(fair_play)), "passed": not fair_play.empty},
            {"check": "most_entertaining_output_exists", "expected": ">=1 row", "actual": int(len(entertaining)), "passed": not entertaining.empty},
        ]
    )
    report_df = pd.DataFrame(checks)
    return bool(report_df["passed"].all()), report_df



def prepare_step17_world_cup_awards() -> dict[str, Any]:
    """Generate the broader Step 17 World Cup awards analytics outputs."""
    players_df = load_player_candidates()
    players_valid, player_validation_df = validate_player_candidates(players_df)

    team_profiles_df = load_team_award_profiles()
    team_valid, team_validation_df = validate_team_award_profiles(team_profiles_df)

    team_stage_df = load_team_stage_probabilities()

    players_enriched_df = add_team_progression_to_players(players_df, team_stage_df)
    if "discipline_risk" in players_enriched_df.columns:
        discipline_df = (
            players_enriched_df.assign(discipline_risk=pd.to_numeric(players_enriched_df["discipline_risk"], errors="coerce").fillna(0.0))
            .groupby("team", as_index=False)
            .agg(discipline_risk=("discipline_risk", "mean"))
        )
    else:
        discipline_df = pd.DataFrame(columns=["team", "discipline_risk"])

    team_enriched_df = add_team_stage_to_award_profiles(team_profiles_df, team_stage_df)
    if not discipline_df.empty:
        team_enriched_df = team_enriched_df.merge(discipline_df, on="team", how="left")

    golden_ball_df = calculate_golden_ball_predictions(players_enriched_df)
    golden_boot_df = calculate_golden_boot_predictions(players_enriched_df)
    golden_glove_df = calculate_golden_glove_predictions(players_enriched_df)
    young_player_df = calculate_young_player_predictions(players_enriched_df)
    potm_proxy_df = calculate_player_of_match_proxy(golden_ball_df)
    got_proxy_df = calculate_goal_of_tournament_proxy(golden_boot_df)
    fair_play_df = calculate_fair_play_predictions(team_enriched_df)
    entertaining_df = calculate_most_entertaining_team_predictions(team_enriched_df, players_enriched_df)
    team_of_tournament_df = select_team_of_tournament(golden_ball_df)

    outputs = {
        "golden_ball": golden_ball_df,
        "golden_boot": golden_boot_df,
        "golden_glove": golden_glove_df,
        "young_player": young_player_df,
        "fair_play": fair_play_df,
        "most_entertaining": entertaining_df,
        "team_of_tournament": team_of_tournament_df,
        "player_of_match_proxy": potm_proxy_df,
        "goal_of_tournament_proxy": got_proxy_df,
    }
    combined_awards_df = create_combined_awards_table(outputs)
    outputs["combined_awards"] = combined_awards_df

    outputs_valid, outputs_validation_df = _validate_outputs(outputs)

    validation_report_df = pd.concat([player_validation_df, team_validation_df, outputs_validation_df], ignore_index=True)
    validation_passed = bool(players_valid and team_valid and outputs_valid)

    summary = create_world_cup_awards_summary(outputs, validation_passed=validation_passed)
    report_text = create_world_cup_awards_markdown_report(outputs, summary)
    report_path = save_awards_report(report_text)

    combined_predictions_path = _save_csv(combined_awards_df, WORLD_CUP_AWARDS_PREDICTIONS_FILE)
    _save_csv(golden_ball_df, GOLDEN_BALL_PREDICTIONS_FILE)
    _save_csv(golden_boot_df, GOLDEN_BOOT_PREDICTIONS_FILE)
    _save_csv(golden_glove_df, GOLDEN_GLOVE_PREDICTIONS_FILE)
    _save_csv(young_player_df, YOUNG_PLAYER_PREDICTIONS_FILE)
    _save_csv(fair_play_df, FAIR_PLAY_PREDICTIONS_FILE)
    _save_csv(entertaining_df, MOST_ENTERTAINING_TEAM_PREDICTIONS_FILE)
    _save_csv(team_of_tournament_df, TEAM_OF_THE_TOURNAMENT_FILE)
    _save_csv(potm_proxy_df, PLAYER_OF_THE_MATCH_PROXY_FILE)
    _save_csv(got_proxy_df, GOAL_OF_THE_TOURNAMENT_PROXY_FILE)
    validation_report_path = _save_csv(validation_report_df, WORLD_CUP_AWARDS_VALIDATION_REPORT_FILE)
    _save_json(summary, WORLD_CUP_AWARDS_SUMMARY_FILE)

    summary.update(
        {
            "combined_predictions_path": combined_predictions_path,
            "report_path": report_path,
            "validation_report_path": validation_report_path,
        }
    )
    return summary


if __name__ == "__main__":
    print(prepare_step17_world_cup_awards())
