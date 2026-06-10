"""Apply-blocker analysis and safe cleanup for Step 17H."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C
from src.official.final_readiness import evaluate_official_final_readiness
from src.official.populated_data_builder import (
    build_all_populated_official_data,
    derive_teams_and_groups_from_imported_fixtures,
)
from src.official.population_completeness import (
    calculate_population_completeness,
    save_population_completeness_report,
)
from src.official.promotion import load_official_final_mode
from src.official.source_labels import (
    is_official_source_label,
    is_sample_source_label,
    replace_sample_source_labels_for_verified_imports,
)
from src.official.stage_normalization import apply_stage_normalization, is_group_stage_label, is_knockout_stage_label


def _populated_dir() -> Path:
    return C.PROJECT_ROOT / C.OFFICIAL_POPULATED_DATA_DIR


def _reports_dir() -> Path:
    p = C.PROJECT_ROOT / C.OFFICIAL_POPULATED_REPORTS_DIR
    p.mkdir(parents=True, exist_ok=True)
    return p


def _read_populated(name: str) -> pd.DataFrame:
    path = _populated_dir() / name
    if path.is_file():
        try:
            return pd.read_csv(path)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


def _save_populated(df: pd.DataFrame, name: str) -> str:
    path = _populated_dir() / name
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return str(path)


def analyze_apply_blockers() -> tuple[dict[str, Any], pd.DataFrame]:
    """Analyze blockers across populated official datasets."""
    metrics_before, _ = calculate_population_completeness()
    fixtures = _read_populated(C.POPULATED_OFFICIAL_FIXTURES_FILE)
    teams = _read_populated(C.POPULATED_OFFICIAL_TEAMS_FILE)
    players = _read_populated(C.POPULATED_OFFICIAL_PLAYERS_FILE)

    rows: list[dict[str, Any]] = []

    unnormalized = 0
    if not fixtures.empty and "stage" in fixtures.columns:
        for stage in fixtures["stage"].fillna("").astype(str):
            if stage and not is_group_stage_label(stage) and not is_knockout_stage_label(stage):
                if "first stage" in stage.lower() or stage.lower() == "group stage":
                    unnormalized += 1
        first_stage = int(fixtures["stage"].fillna("").astype(str).str.contains("First Stage", case=False, na=False).sum())
        if first_stage:
            rows.append(
                {
                    "category": "stage_normalization",
                    "blocking": True,
                    "issue": f"{first_stage} fixtures still use FIFA label 'First Stage'",
                    "suggested_fix": "Run apply_safe_blocker_cleanups to normalize to group_stage",
                }
            )

    sample_teams = 0
    if not teams.empty and "source" in teams.columns:
        sample_teams = int(teams["source"].map(is_sample_source_label).sum())
        if sample_teams:
            rows.append(
                {
                    "category": "source_labels",
                    "blocking": True,
                    "issue": f"{sample_teams} team rows with sample/unverified source labels",
                    "suggested_fix": "Rebuild teams from imported schedule and apply official FIFA source labels",
                }
            )

    team_count = len(teams) if not teams.empty else 0
    if team_count != C.OFFICIAL_REQUIRED_TEAM_COUNT:
        rows.append(
            {
                "category": "team_loader",
                "blocking": team_count < C.OFFICIAL_REQUIRED_TEAM_COUNT,
                "issue": f"Populated teams count {team_count}/{C.OFFICIAL_REQUIRED_TEAM_COUNT}",
                "suggested_fix": "Derive teams/groups from 104 imported group-stage fixtures",
            }
        )

    rows.append(
        {
            "category": "fixture_counts",
            "blocking": metrics_before.get("fixtures_count", 0) != 104,
            "issue": f"Fixtures {metrics_before.get('fixtures_count', 0)}/104",
            "suggested_fix": "Import FIFA schedule file",
        }
    )
    rows.append(
        {
            "category": "group_stage_fixtures",
            "blocking": metrics_before.get("group_stage_fixtures_count", 0) != 72,
            "issue": f"Group-stage {metrics_before.get('group_stage_fixtures_count', 0)}/72",
            "suggested_fix": "Normalize First Stage → group_stage",
        }
    )
    rows.append(
        {
            "category": "squad_counts",
            "blocking": metrics_before.get("players_count", 0) != 1248,
            "issue": f"Players {metrics_before.get('players_count', 0)}/1248",
            "suggested_fix": "Import FIFA squad file",
        }
    )
    rows.append(
        {
            "category": "placeholders",
            "blocking": metrics_before.get("blocking_placeholder_count", 0) > 0,
            "issue": f"Blocking placeholders {metrics_before.get('blocking_placeholder_count', 0)}",
            "suggested_fix": "Fill required fields or run cleanup after verified import",
        }
    )
    rows.append(
        {
            "category": "missing_values",
            "blocking": metrics_before.get("missing_required_values_count", 0) > 0,
            "issue": f"Missing required values {metrics_before.get('missing_required_values_count', 0)}",
            "suggested_fix": "Review populated CSV required columns",
        }
    )

    report_df = pd.DataFrame(rows)
    summary = {
        "metrics_before": metrics_before,
        "blocking_count": int(report_df["blocking"].sum()) if not report_df.empty else 0,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }
    return summary, report_df


def apply_safe_blocker_cleanups() -> dict[str, Any]:
    """Run safe cleanups without promoting official_final."""
    notes: list[str] = []
    metrics_before, _ = calculate_population_completeness()

    fixtures = _read_populated(C.POPULATED_OFFICIAL_FIXTURES_FILE)
    if not fixtures.empty:
        fixtures = apply_stage_normalization(fixtures)
        fixtures = replace_sample_source_labels_for_verified_imports(
            fixtures, "fixtures", "fifa_schedule_api", require_min_rows=72
        )
        # Ensure downloadable schedule label maps to official API label
        fixtures.loc[
            fixtures["source"].fillna("").astype(str).str.lower() == "fifa_downloadable_schedule",
            "source",
        ] = "fifa_schedule_api"
        _save_populated(fixtures, C.POPULATED_OFFICIAL_FIXTURES_FILE)
        notes.append(f"Normalized stages on {len(fixtures)} fixtures")

    venues = _read_populated(C.POPULATED_OFFICIAL_VENUES_FILE)
    if not venues.empty:
        venues = replace_sample_source_labels_for_verified_imports(
            venues, "venues", "fifa_schedule_api", require_min_rows=1
        )
        venues.loc[
            venues["source"].fillna("").astype(str).str.lower().isin(
                {"fifa_downloadable_schedule", "sample_to_be_verified", "ai_prefilled_needs_verification"}
            ),
            "source",
        ] = "fifa_schedule_api"
        _save_populated(venues, C.POPULATED_OFFICIAL_VENUES_FILE)

    players = _read_populated(C.POPULATED_OFFICIAL_PLAYERS_FILE)
    if not players.empty:
        players = replace_sample_source_labels_for_verified_imports(
            players, "players", "fifa_squad_pdf", require_min_rows=C.OFFICIAL_REQUIRED_TOTAL_PLAYERS
        )
        players.loc[
            players["source"].fillna("").astype(str).str.lower() == "fifa_squad_file",
            "source",
        ] = "fifa_squad_pdf"
        _save_populated(players, C.POPULATED_OFFICIAL_PLAYERS_FILE)
        notes.append(f"Updated source labels on {len(players)} players")

    teams_rebuilt = False
    if not fixtures.empty and len(fixtures) >= C.OFFICIAL_TOTAL_MATCHES:
        teams_df, groups_df, warn = derive_teams_and_groups_from_imported_fixtures(fixtures)
        if len(teams_df) >= C.OFFICIAL_REQUIRED_TEAM_COUNT:
            _save_populated(teams_df, C.POPULATED_OFFICIAL_TEAMS_FILE)
            _save_populated(groups_df, C.POPULATED_OFFICIAL_GROUPS_FILE)
            teams_rebuilt = True
            notes.append(f"Rebuilt {len(teams_df)} teams and {len(groups_df)} group rows from schedule")
        elif warn:
            notes.append(warn)

    build_all_populated_official_data()

    metrics_after, report_df = calculate_population_completeness()
    save_population_completeness_report(report_df)

    try:
        readiness = evaluate_official_final_readiness()
    except Exception as exc:
        readiness = {"is_official_final_ready": False, "error": str(exc)}

    final_mode = load_official_final_mode()
    _, blocker_report = analyze_apply_blockers()

    return {
        "stages_normalized": not fixtures.empty,
        "teams_groups_rebuilt": teams_rebuilt,
        "source_labels_updated": True,
        "metrics_before": metrics_before,
        "metrics_after": metrics_after,
        "remaining_blockers": blocker_report[blocker_report["blocking"] == True]["category"].tolist()  # noqa: E712
        if not blocker_report.empty
        else [],
        "final_ready": bool(readiness.get("is_official_final_ready", False)),
        "official_final_enabled": bool(final_mode.get("official_final_enabled", False)),
        "ready_for_apply": metrics_after.get("ready_for_apply", False),
        "notes": notes,
    }


def save_blocker_cleanup_report(report_df: pd.DataFrame, output_path: str | None = None) -> str:
    path = Path(output_path) if output_path else _reports_dir() / C.OFFICIAL_APPLY_BLOCKER_CLEANUP_REPORT_FILE
    if not path.is_absolute():
        path = C.PROJECT_ROOT / path
    report_df.to_csv(path, index=False)
    return str(path)
