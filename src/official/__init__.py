"""Official World Cup 2026 data-lock package."""

from src.official.apply_imports import (
    apply_official_import_file,
    apply_all_imports,
    apply_teams_import,
    apply_groups_import,
    apply_fixtures_import,
    apply_venues_import,
    apply_players_import,
    create_import_report,
)
from src.official.final_readiness import (
    evaluate_official_final_readiness,
    save_final_readiness_report,
    is_official_final_mode_allowed,
)
from src.official.import_templates import (
    generate_all_import_templates,
    generate_teams_import_template,
    generate_groups_import_template,
    generate_fixtures_import_template,
    generate_venues_import_template,
    generate_players_import_template,
    generate_squads_import_template,
    create_import_manifest,
    validate_import_file,
)
from src.official.loaders import (
    get_official_team_list,
    is_official_team,
    load_official_fixtures,
    load_official_groups,
    load_official_teams,
    load_official_venues,
)
from src.official.prepare_population_pack import prepare_step17d_official_data_population_pack
from src.official.promotion import (
    can_promote_to_official_final,
    demote_from_official_final,
    load_official_final_mode,
    promote_to_official_final,
)
from src.official.population_guide import generate_population_guide_markdown, save_population_guide
from src.official.population_status import (
    initialize_population_status,
    load_population_status,
    save_population_status,
    summarize_population_status,
    update_population_step,
)
from src.official.missing_data import (
    build_official_missing_data_report,
    find_missing_or_placeholder_values,
    save_missing_data_report,
)
from src.official.import_diff import (
    compare_import_to_current,
    infer_key_columns,
    preview_official_import,
    save_import_diff_report,
)
from src.official.master_workbook import generate_population_workbook_pack
from src.official.prepare_official_data import prepare_step17a_official_worldcup_data
from src.official.validators import validate_official_data_bundle

__all__ = [
    # Final readiness
    "evaluate_official_final_readiness",
    "save_final_readiness_report",
    "is_official_final_mode_allowed",
    # Import templates
    "generate_all_import_templates",
    "generate_teams_import_template",
    "generate_groups_import_template",
    "generate_fixtures_import_template",
    "generate_venues_import_template",
    "generate_players_import_template",
    "generate_squads_import_template",
    "create_import_manifest",
    "validate_import_file",
    # Apply imports
    "apply_official_import_file",
    "apply_all_imports",
    "apply_teams_import",
    "apply_groups_import",
    "apply_fixtures_import",
    "apply_venues_import",
    "apply_players_import",
    "create_import_report",
    # Step 17D population pack
    "prepare_step17d_official_data_population_pack",
    "can_promote_to_official_final",
    "demote_from_official_final",
    "load_official_final_mode",
    "promote_to_official_final",
    "generate_population_guide_markdown",
    "save_population_guide",
    "initialize_population_status",
    "load_population_status",
    "save_population_status",
    "summarize_population_status",
    "update_population_step",
    "build_official_missing_data_report",
    "find_missing_or_placeholder_values",
    "save_missing_data_report",
    "compare_import_to_current",
    "infer_key_columns",
    "preview_official_import",
    "save_import_diff_report",
    "generate_population_workbook_pack",
    # Existing
    "get_official_team_list",
    "is_official_team",
    "load_official_fixtures",
    "load_official_groups",
    "load_official_teams",
    "load_official_venues",
    "prepare_step17a_official_worldcup_data",
    "validate_official_data_bundle",
]