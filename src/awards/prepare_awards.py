"""Step 18 World Cup awards preparation orchestrator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C
from src.awards.award_data import (
    get_award_candidate_source,
    load_official_award_candidates,
    load_official_teams_for_awards,
    load_team_award_profiles,
    load_team_stage_probabilities,
    merge_players_with_team_progression,
    require_official_final_ready,
)
from src.awards.award_reports import (
    create_combined_awards_table,
    create_world_cup_awards_markdown_report,
    create_world_cup_awards_summary,
    save_world_cup_awards_report,
)
from src.awards.award_validation import validate_award_outputs
from src.awards.player_awards import (
    calculate_golden_ball_predictions,
    calculate_golden_boot_predictions,
    calculate_golden_glove_predictions,
    calculate_goal_of_tournament_proxy,
    calculate_player_of_match_proxy,
    calculate_young_player_predictions,
    validate_player_candidates,
)
from src.awards.team_awards import (
    calculate_fair_play_predictions,
    calculate_most_entertaining_team_predictions,
    prepare_team_award_data,
    validate_team_award_profiles,
)
from src.awards.team_of_tournament import select_team_of_the_tournament

PROJECT_ROOT = C.PROJECT_ROOT
PROCESSED_DATA_DIR = PROJECT_ROOT / C.AWARDS_OUTPUT_DIR


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


def prepare_step18_world_cup_awards(*, use_enriched_candidates: bool | None = None) -> dict[str, Any]:
    """Generate Step 18 World Cup awards analytics outputs (official_final required)."""
    readiness = require_official_final_ready()

    players_df = load_official_award_candidates(use_enriched_candidates=use_enriched_candidates)
    candidate_source = get_award_candidate_source(use_enriched_candidates=use_enriched_candidates)
    players_valid, player_validation_df = validate_player_candidates(players_df)

    team_profiles_df = load_team_award_profiles()
    team_valid, team_validation_df = validate_team_award_profiles(team_profiles_df)

    official_teams_df = load_official_teams_for_awards()
    team_stage_df = load_team_stage_probabilities()

    players_enriched_df = merge_players_with_team_progression(players_df, team_stage_df)
    team_enriched_df = prepare_team_award_data(team_profiles_df, team_stage_df, players_enriched_df)

    golden_ball_df = calculate_golden_ball_predictions(players_enriched_df)
    golden_boot_df = calculate_golden_boot_predictions(players_enriched_df)
    golden_glove_df = calculate_golden_glove_predictions(players_enriched_df)
    young_player_df = calculate_young_player_predictions(players_enriched_df)
    potm_proxy_df = calculate_player_of_match_proxy(golden_ball_df)
    got_proxy_df = calculate_goal_of_tournament_proxy(golden_boot_df)
    fair_play_df = calculate_fair_play_predictions(team_enriched_df)
    entertaining_df = calculate_most_entertaining_team_predictions(team_enriched_df, players_enriched_df)
    team_of_tournament_df = select_team_of_the_tournament(golden_ball_df)

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

    outputs_valid, outputs_validation_df = validate_award_outputs(
        outputs,
        official_candidates=players_df,
        official_teams=official_teams_df,
    )
    validation_report_df = pd.concat([player_validation_df, team_validation_df, outputs_validation_df], ignore_index=True)
    validation_passed = bool(players_valid and team_valid and outputs_valid)

    summary = create_world_cup_awards_summary(outputs, validation_passed=validation_passed)
    summary["official_final_enabled"] = readiness.get("official_final_enabled", True)
    summary["candidate_source"] = candidate_source
    report_text = create_world_cup_awards_markdown_report(outputs, summary, readiness)
    report_path = save_world_cup_awards_report(report_text)

    combined_predictions_path = _save_csv(combined_awards_df, C.WORLD_CUP_AWARDS_PREDICTIONS_FILE)
    _save_csv(golden_ball_df, C.GOLDEN_BALL_PREDICTIONS_FILE)
    _save_csv(golden_boot_df, C.GOLDEN_BOOT_PREDICTIONS_FILE)
    _save_csv(golden_glove_df, C.GOLDEN_GLOVE_PREDICTIONS_FILE)
    _save_csv(young_player_df, C.YOUNG_PLAYER_PREDICTIONS_FILE)
    _save_csv(fair_play_df, C.FAIR_PLAY_PREDICTIONS_FILE)
    _save_csv(entertaining_df, C.MOST_ENTERTAINING_TEAM_PREDICTIONS_FILE)
    _save_csv(team_of_tournament_df, C.TEAM_OF_THE_TOURNAMENT_FILE)
    _save_csv(potm_proxy_df, C.PLAYER_OF_THE_MATCH_PROXY_FILE)
    _save_csv(got_proxy_df, C.GOAL_OF_THE_TOURNAMENT_PROXY_FILE)
    validation_report_path = _save_csv(validation_report_df, C.WORLD_CUP_AWARDS_VALIDATION_REPORT_FILE)
    _save_json(summary, C.WORLD_CUP_AWARDS_SUMMARY_FILE)

    summary.update(
        {
            "combined_predictions_path": combined_predictions_path,
            "report_path": report_path,
            "validation_report_path": validation_report_path,
        }
    )
    return summary


def prepare_step17_world_cup_awards(*, use_enriched_candidates: bool | None = None) -> dict[str, Any]:
    """Backward-compatible alias for Step 18 orchestrator."""
    return prepare_step18_world_cup_awards(use_enriched_candidates=use_enriched_candidates)


if __name__ == "__main__":
    print(json.dumps(prepare_step18_world_cup_awards(), indent=2))
