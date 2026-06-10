"""World Cup awards analytics package (Step 18)."""

from src.awards.award_data import (
    calculate_team_progression_score,
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
    add_team_progression_to_players,
    calculate_expected_matches,
    calculate_golden_ball_predictions,
    calculate_golden_boot_predictions,
    calculate_golden_glove_predictions,
    calculate_goal_of_tournament_proxy,
    calculate_player_impact_components,
    calculate_player_of_match_proxy,
    calculate_position_impact_score,
    calculate_team_progression_score as calculate_player_team_progression_score,
    calculate_young_player_predictions,
    ensure_numeric_award_columns,
    filter_young_player_candidates,
    is_young_player_eligible,
    load_player_candidates,
    validate_player_candidates,
)
from src.awards.prepare_awards import prepare_step18_world_cup_awards, prepare_step17_world_cup_awards
from src.awards.team_awards import (
    calculate_fair_play_predictions,
    calculate_most_entertaining_team_predictions,
    prepare_team_award_data,
    validate_team_award_profiles,
)
from src.awards.team_of_tournament import select_team_of_the_tournament, select_team_of_tournament

__all__ = [
    "add_team_progression_to_players",
    "calculate_expected_matches",
    "calculate_fair_play_predictions",
    "calculate_golden_ball_predictions",
    "calculate_golden_boot_predictions",
    "calculate_golden_glove_predictions",
    "calculate_goal_of_tournament_proxy",
    "calculate_most_entertaining_team_predictions",
    "calculate_player_impact_components",
    "calculate_player_of_match_proxy",
    "calculate_position_impact_score",
    "calculate_player_team_progression_score",
    "calculate_team_progression_score",
    "calculate_young_player_predictions",
    "create_combined_awards_table",
    "create_world_cup_awards_markdown_report",
    "create_world_cup_awards_summary",
    "ensure_numeric_award_columns",
    "filter_young_player_candidates",
    "is_young_player_eligible",
    "load_official_award_candidates",
    "load_official_teams_for_awards",
    "load_player_candidates",
    "load_team_award_profiles",
    "load_team_stage_probabilities",
    "merge_players_with_team_progression",
    "prepare_step17_world_cup_awards",
    "prepare_step18_world_cup_awards",
    "prepare_team_award_data",
    "require_official_final_ready",
    "save_world_cup_awards_report",
    "select_team_of_the_tournament",
    "select_team_of_tournament",
    "validate_award_outputs",
    "validate_player_candidates",
    "validate_team_award_profiles",
]
