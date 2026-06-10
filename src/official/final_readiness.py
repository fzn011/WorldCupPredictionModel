"""Final readiness evaluation for official World Cup 2026 data.

This module provides the evaluate_official_final_readiness() function that
checks all data completeness, placeholder values, sample rows, and cross-dataset
consistency to determine if the system is ready for official_final mode.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C
from src.official.loaders import (
    load_official_fixtures,
    load_official_groups,
    load_official_teams,
    load_official_venues,
)
from src.official.validators import (
    validate_group_team_consistency,
    validate_official_data_bundle,
)
from src.utils.team_name_mapping import standardize_team_name

# Local reference to placeholder values for efficiency
_PLACEHOLDER_VALUES = set(str(v).strip() for v in C.OFFICIAL_PLACEHOLDER_VALUES)


def _load_csv_safe(path: Path) -> pd.DataFrame | None:
    """Load a CSV file if it exists, otherwise return None."""
    if path.exists():
        return pd.read_csv(path)
    return None


def _count_placeholders(df: pd.DataFrame, columns: list[str]) -> int:
    """Count rows where any of the specified columns contain placeholder values."""
    if df is None or df.empty:
        return 0
    count = 0
    for col in columns:
        if col not in df.columns:
            continue
        values = df[col].fillna("").astype(str).str.strip()
        count += int(values.isin(_PLACEHOLDER_VALUES).sum())
    return count


def _has_sample_rows(df: pd.DataFrame) -> bool:
    """Check if DataFrame contains sample_to_be_verified rows."""
    if df is None or df.empty:
        return False
    if "source" not in df.columns:
        return False
    return bool((df["source"].fillna("").astype(str) == "sample_to_be_verified").any())


def _check_teams_complete(teams_df: pd.DataFrame | None) -> dict[str, Any]:
    """Check if all 48 teams are verified."""
    result = {
        "id": "teams_complete",
        "passed": False,
        "details": {},
    }
    if teams_df is None or teams_df.empty:
        result["details"] = {"error": "Teams data not found"}
        return result

    team_count = len(teams_df)
    result["details"] = {
        "team_count": team_count,
        "required": C.OFFICIAL_REQUIRED_TEAM_COUNT,
    }

    if team_count == C.OFFICIAL_REQUIRED_TEAM_COUNT:
        result["passed"] = True
    return result


def _check_teams_no_placeholders(teams_df: pd.DataFrame | None) -> dict[str, Any]:
    """Check for placeholder values in teams data."""
    result = {
        "id": "teams_no_placeholders",
        "passed": False,
        "details": {},
    }
    if teams_df is None or teams_df.empty:
        result["details"] = {"error": "Teams data not found"}
        return result

    placeholder_count = _count_placeholders(teams_df, ["team", "team_code", "group", "confederation"])
    result["details"] = {"placeholder_count": placeholder_count}

    if placeholder_count == 0:
        result["passed"] = True
    return result


def _check_groups_complete(groups_df: pd.DataFrame | None) -> dict[str, Any]:
    """Check if all 12 groups have 4 teams each."""
    result = {
        "id": "groups_complete",
        "passed": False,
        "details": {},
    }
    if groups_df is None or groups_df.empty:
        result["details"] = {"error": "Groups data not found"}
        return result

    group_counts = groups_df.groupby("group")["team"].count()
    all_have_four = bool((group_counts == 4).all() and len(group_counts) == 12)

    result["details"] = {
        "group_count": len(group_counts),
        "all_groups_have_4_teams": all_have_four,
        "group_sizes": group_counts.to_dict(),
    }

    if all_have_four:
        result["passed"] = True
    return result


def _check_groups_no_placeholders(groups_df: pd.DataFrame | None) -> dict[str, Any]:
    """Check for placeholder values in groups data."""
    result = {
        "id": "groups_no_placeholders",
        "passed": False,
        "details": {},
    }
    if groups_df is None or groups_df.empty:
        result["details"] = {"error": "Groups data not found"}
        return result

    placeholder_count = _count_placeholders(groups_df, ["team", "team_code", "group"])
    result["details"] = {"placeholder_count": placeholder_count}

    if placeholder_count == 0:
        result["passed"] = True
    return result


def _check_venues_complete(venues_df: pd.DataFrame | None) -> dict[str, Any]:
    """Check if all venues are verified (expect at least 16 venues)."""
    result = {
        "id": "venues_complete",
        "passed": False,
        "details": {},
    }
    if venues_df is None or venues_df.empty:
        result["details"] = {"error": "Venues data not found"}
        return result

    venue_count = len(venues_df)
    # FIFA World Cup 2026 will use 16 venues across 3 host countries
    expected_min_venues = 16

    result["details"] = {
        "venue_count": venue_count,
        "expected_min": expected_min_venues,
    }

    if venue_count >= expected_min_venues:
        result["passed"] = True
    return result


def _check_venues_no_placeholders(venues_df: pd.DataFrame | None) -> dict[str, Any]:
    """Check for placeholder values in venues data."""
    result = {
        "id": "venues_no_placeholders",
        "passed": False,
        "details": {},
    }
    if venues_df is None or venues_df.empty:
        result["details"] = {"error": "Venues data not found"}
        return result

    placeholder_count = _count_placeholders(venues_df, ["venue", "stadium", "city", "country", "timezone"])
    result["details"] = {"placeholder_count": placeholder_count}

    if placeholder_count == 0:
        result["passed"] = True
    return result


def _check_fixtures_complete(fixtures_df: pd.DataFrame | None) -> dict[str, Any]:
    """Check if all 104 fixtures are scheduled."""
    result = {
        "id": "fixtures_complete",
        "passed": False,
        "details": {},
    }
    if fixtures_df is None or fixtures_df.empty:
        result["details"] = {"error": "Fixtures data not found"}
        return result

    fixture_count = len(fixtures_df)
    result["details"] = {
        "fixture_count": fixture_count,
        "required": C.OFFICIAL_TOTAL_MATCHES,
    }

    if fixture_count == C.OFFICIAL_TOTAL_MATCHES:
        result["passed"] = True
    return result


def _check_fixtures_no_placeholders(fixtures_df: pd.DataFrame | None) -> dict[str, Any]:
    """Check for placeholder values in fixtures data."""
    result = {
        "id": "fixtures_no_placeholders",
        "passed": False,
        "details": {},
    }
    if fixtures_df is None or fixtures_df.empty:
        result["details"] = {"error": "Fixtures data not found"}
        return result

    placeholder_count = _count_placeholders(fixtures_df, ["venue", "city", "country", "team_a", "team_b", "timezone"])
    result["details"] = {"placeholder_count": placeholder_count}

    if placeholder_count == 0:
        result["passed"] = True
    return result


def _check_squads_complete(players_df: pd.DataFrame | None) -> dict[str, Any]:
    """Check if all 48 teams have 26 players each."""
    result = {
        "id": "squads_complete",
        "passed": False,
        "details": {},
    }
    if players_df is None or players_df.empty:
        result["details"] = {"error": "Players data not found"}
        return result

    team_counts = players_df.groupby("team").size()
    teams_with_26 = int((team_counts == 26).sum())

    result["details"] = {
        "teams_with_26_players": teams_with_26,
        "total_teams": len(team_counts),
        "required": 48,
    }

    if teams_with_26 == 48:
        result["passed"] = True
    return result


def _check_players_complete(players_df: pd.DataFrame | None) -> dict[str, Any]:
    """Check if all 1248 players are registered."""
    result = {
        "id": "players_complete",
        "passed": False,
        "details": {},
    }
    if players_df is None or players_df.empty:
        result["details"] = {"error": "Players data not found"}
        return result

    player_count = len(players_df)
    result["details"] = {
        "player_count": player_count,
        "required": C.OFFICIAL_REQUIRED_TOTAL_PLAYERS,
    }

    if player_count == C.OFFICIAL_REQUIRED_TOTAL_PLAYERS:
        result["passed"] = True
    return result


def _check_players_no_placeholders(players_df: pd.DataFrame | None) -> dict[str, Any]:
    """Check for placeholder values in players data."""
    result = {
        "id": "players_no_placeholders",
        "passed": False,
        "details": {},
    }
    if players_df is None or players_df.empty:
        result["details"] = {"error": "Players data not found"}
        return result

    placeholder_count = _count_placeholders(players_df, [
        "player_name", "team", "team_code", "position", "position_code",
        "shirt_number", "club", "date_of_birth"
    ])
    result["details"] = {"placeholder_count": placeholder_count}

    if placeholder_count == 0:
        result["passed"] = True
    return result


def _check_award_candidates_ready(award_candidates_df: pd.DataFrame | None) -> dict[str, Any]:
    """Check if award candidates have been generated."""
    result = {
        "id": "award_candidates_ready",
        "passed": False,
        "details": {},
    }
    if award_candidates_df is None or award_candidates_df.empty:
        result["details"] = {"error": "Award candidates data not found"}
        return result

    candidate_count = len(award_candidates_df)
    result["details"] = {"candidate_count": candidate_count}

    # Should have all official players as candidates
    if candidate_count >= C.OFFICIAL_REQUIRED_TOTAL_PLAYERS:
        result["passed"] = True
    return result


def _check_player_priors_merged(award_candidates_df: pd.DataFrame | None) -> dict[str, Any]:
    """Check if player priors have been merged with award candidates."""
    result = {
        "id": "player_priors_merged",
        "passed": False,
        "details": {},
    }
    if award_candidates_df is None or award_candidates_df.empty:
        result["details"] = {"error": "Award candidates data not found"}
        return result

    if "has_player_prior" not in award_candidates_df.columns:
        result["details"] = {"error": "has_player_prior column not found"}
        return result

    with_priors = int(award_candidates_df["has_player_prior"].sum())
    total = len(award_candidates_df)
    result["details"] = {
        "players_with_priors": with_priors,
        "total_players": total,
    }

    # At least some players should have priors (user-provided or estimated)
    if with_priors > 0:
        result["passed"] = True
    return result


def _check_no_sample_rows(
    teams_df: pd.DataFrame | None,
    groups_df: pd.DataFrame | None,
    fixtures_df: pd.DataFrame | None,
    venues_df: pd.DataFrame | None,
    players_df: pd.DataFrame | None,
) -> dict[str, Any]:
    """Check that no datasets contain sample_to_be_verified rows."""
    result = {
        "id": "no_sample_rows",
        "passed": True,
        "details": {"datasets_checked": []},
    }

    datasets = [
        ("teams", teams_df),
        ("groups", groups_df),
        ("fixtures", fixtures_df),
        ("venues", venues_df),
        ("players", players_df),
    ]

    sample_datasets = []
    for name, df in datasets:
        if df is not None and not df.empty:
            result["details"]["datasets_checked"].append(name)
            if _has_sample_rows(df):
                sample_datasets.append(name)

    if sample_datasets:
        result["passed"] = False
        result["details"]["sample_datasets"] = sample_datasets

    return result


def _check_data_consistency(
    teams_df: pd.DataFrame | None,
    groups_df: pd.DataFrame | None,
    fixtures_df: pd.DataFrame | None,
    venues_df: pd.DataFrame | None,
) -> dict[str, Any]:
    """Check cross-dataset consistency."""
    result = {
        "id": "data_consistency",
        "passed": False,
        "details": {},
    }

    if any(df is None or df.empty for df in [teams_df, groups_df, fixtures_df, venues_df]):
        result["details"] = {"error": "One or more datasets are missing"}
        return result

    # Check groups vs teams consistency
    groups_ok, groups_report = validate_group_team_consistency(groups_df, teams_df)

    # Check fixture team consistency
    fixtures_ok, fixtures_report = validate_official_data_bundle(
        teams_df, groups_df, fixtures_df, venues_df, fixtures_df, strict_full_schedule=False
    )

    result["details"] = {
        "groups_teams_consistent": groups_ok,
        "fixtures_consistent": fixtures_ok,
    }

    if groups_ok and fixtures_ok:
        result["passed"] = True
    return result


def evaluate_official_final_readiness(
    official_processed_dir: Path | str | None = None,
) -> dict[str, Any]:
    """Evaluate final readiness for official_final mode.

    Args:
        official_processed_dir: Path to the official processed data directory.
            Defaults to PROJECT_ROOT / OFFICIAL_PROCESSED_DIR.

    Returns:
        Dictionary containing:
        - status: "ready", "warning", or "blocked"
        - checklist: List of check results
        - blockers: List of blocking issues
        - warnings: List of warning issues
        - summary: Summary statistics
        - timestamp: ISO timestamp of evaluation
    """
    if official_processed_dir is None:
        official_processed_dir = C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR
    elif isinstance(official_processed_dir, str):
        official_processed_dir = Path(official_processed_dir)

    # Load all datasets
    teams_df = _load_csv_safe(official_processed_dir / C.OFFICIAL_TEAMS_FILE)
    groups_df = _load_csv_safe(official_processed_dir / C.OFFICIAL_GROUPS_FILE)
    fixtures_df = _load_csv_safe(official_processed_dir / C.OFFICIAL_FIXTURES_FILE)
    venues_df = _load_csv_safe(official_processed_dir / C.OFFICIAL_VENUES_FILE)
    players_df = _load_csv_safe(official_processed_dir / C.OFFICIAL_PLAYERS_FILE)
    award_candidates_df = _load_csv_safe(C.PROJECT_ROOT / C.PROCESSED_DATA_DIR / C.OFFICIAL_AWARD_CANDIDATES_FILE)

    # Run all checks
    checks = [
        _check_teams_complete(teams_df),
        _check_teams_no_placeholders(teams_df),
        _check_groups_complete(groups_df),
        _check_groups_no_placeholders(groups_df),
        _check_venues_complete(venues_df),
        _check_venues_no_placeholders(venues_df),
        _check_fixtures_complete(fixtures_df),
        _check_fixtures_no_placeholders(fixtures_df),
        _check_squads_complete(players_df),
        _check_players_complete(players_df),
        _check_players_no_placeholders(players_df),
        _check_award_candidates_ready(award_candidates_df),
        _check_player_priors_merged(award_candidates_df),
        _check_no_sample_rows(teams_df, groups_df, fixtures_df, venues_df, players_df),
        _check_data_consistency(teams_df, groups_df, fixtures_df, venues_df),
    ]

    # Determine status
    failed_checks = [c for c in checks if not c["passed"]]
    blocked_ids = set(C.OFFICIAL_FINAL_BLOCKERS)

    blockers = []
    warnings = []

    for check in failed_checks:
        check_id = check["id"]
        # Map check IDs to blocker IDs
        if check_id in blocked_ids:
            blockers.append(check)
        else:
            # Some checks map to blockers
            if check_id == "teams_complete":
                blockers.append({"id": "incomplete_teams", "details": check["details"]})
            elif check_id == "groups_complete":
                blockers.append({"id": "incomplete_groups", "details": check["details"]})
            elif check_id == "venues_complete":
                blockers.append({"id": "incomplete_venues", "details": check["details"]})
            elif check_id == "fixtures_complete":
                blockers.append({"id": "incomplete_fixtures", "details": check["details"]})
            elif check_id in ("squads_complete", "players_complete"):
                blockers.append({"id": "incomplete_squads", "details": check["details"]})
            elif "placeholder" in check_id:
                blockers.append({"id": "placeholder_values_detected", "details": check["details"]})
            elif check_id == "no_sample_rows":
                blockers.append({"id": "sample_rows_detected", "details": check["details"]})
            elif check_id == "data_consistency":
                blockers.append({"id": "data_inconsistency", "details": check["details"]})
            else:
                warnings.append(check)

    # Determine overall status
    if blockers:
        status = C.OFFICIAL_READINESS_BLOCKED
    elif warnings:
        status = C.OFFICIAL_READINESS_WARNING
    else:
        status = C.OFFICIAL_READINESS_READY

    # Build summary
    passed_count = sum(1 for c in checks if c["passed"])
    total_count = len(checks)

    summary = {
        "total_checks": total_count,
        "passed_checks": passed_count,
        "failed_checks": total_count - passed_count,
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "teams_count": len(teams_df) if teams_df is not None else 0,
        "players_count": len(players_df) if players_df is not None else 0,
        "teams_with_26_players": 0,  # Would need additional calculation
    }

    if players_df is not None and not players_df.empty:
        team_counts = players_df.groupby("team").size()
        summary["teams_with_26_players"] = int((team_counts == 26).sum())

    result = {
        "status": status,
        "checklist": checks,
        "blockers": blockers,
        "warnings": warnings,
        "summary": summary,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "is_official_final_ready": status == C.OFFICIAL_READINESS_READY,
    }

    return result


def save_final_readiness_report(
    report: dict[str, Any],
    output_dir: Path | str | None = None,
) -> Path:
    """Save the final readiness report to disk.

    Args:
        report: The readiness report from evaluate_official_final_readiness().
        output_dir: Output directory. Defaults to OFFICIAL_PROCESSED_DIR.

    Returns:
        Path to the saved report file.
    """
    if output_dir is None:
        output_dir = C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Save JSON report
    report_path = output_dir / C.OFFICIAL_FINAL_READINESS_REPORT_FILE
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    # Save CSV checklist
    checklist_path = output_dir / C.OFFICIAL_FINAL_READINESS_CHECKLIST_FILE
    checklist_rows = []
    for check in report.get("checklist", []):
        checklist_rows.append({
            "id": check["id"],
            "passed": check["passed"],
            "details": json.dumps(check.get("details", {}), default=str),
        })
    checklist_df = pd.DataFrame(checklist_rows)
    checklist_df.to_csv(checklist_path, index=False)

    return report_path


def is_official_final_mode_allowed(
    official_processed_dir: Path | str | None = None,
) -> tuple[bool, list[str]]:
    """Check if official_final mode is allowed.

    This is a convenience function that returns a simple boolean and list of blockers.

    Args:
        official_processed_dir: Path to the official processed data directory.

    Returns:
        Tuple of (is_allowed, list_of_blocker_descriptions).
    """
    report = evaluate_official_final_readiness(official_processed_dir)
    is_allowed = report["is_official_final_ready"]

    blocker_descriptions = []
    for blocker in report.get("blockers", []):
        blocker_id = blocker.get("id", "unknown")
        details = blocker.get("details", {})
        desc = f"{blocker_id}: {json.dumps(details, default=str)}"
        blocker_descriptions.append(desc)

    return is_allowed, blocker_descriptions