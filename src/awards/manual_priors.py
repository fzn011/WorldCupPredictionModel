"""Step 20 manual star-player prior override workflow (official candidates only)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C
from src.awards.award_data import merge_players_with_team_progression, normalize_official_award_candidates
from src.awards.player_awards import (
    calculate_golden_ball_predictions,
    calculate_golden_boot_predictions,
    calculate_golden_glove_predictions,
    calculate_young_player_predictions,
    is_young_player_eligible,
)
from src.utils.team_name_mapping import standardize_team_name

PROJECT_ROOT = C.PROJECT_ROOT
PROCESSED_DATA_DIR = PROJECT_ROOT / C.PROCESSED_DATA_DIR


def _player_label(row: pd.Series) -> str:
    return str(row.get("player_name") or row.get("player") or "")


def _normalize_team(value: Any) -> str:
    return standardize_team_name(str(value).strip())


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    return text in {"1", "true", "yes", "y", "t"}


def _clip_boost(column: str, value: Any) -> tuple[float, bool]:
    """Return clipped boost and whether the raw value was out of range."""
    low, high = C.MANUAL_BOOST_CLIP_RANGES.get(column, (0.0, 1.0))
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0.0, True
    if pd.isna(numeric):
        return 0.0, False
    clipped = float(max(low, min(high, numeric)))
    return clipped, clipped != numeric


def _star_tier_key(value: Any) -> str:
    text = str(value or "none").strip().lower()
    if text in C.MANUAL_STAR_TIER_BONUSES:
        return text
    return "none"


def load_manual_prior_file(path: str | Path) -> pd.DataFrame:
    """Load a manual prior CSV from disk."""
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Manual prior file not found: {file_path}")
    return pd.read_csv(file_path)


def validate_manual_prior_columns(manual_df: pd.DataFrame) -> tuple[bool, list[str]]:
    """Validate required manual prior columns are present."""
    missing = [col for col in C.MANUAL_PRIOR_REQUIRED_COLUMNS if col not in manual_df.columns]
    return len(missing) == 0, missing


def _build_candidate_index(candidates_df: pd.DataFrame) -> tuple[dict[str, int], dict[tuple[str, str], int]]:
    by_id: dict[str, int] = {}
    by_name_team: dict[tuple[str, str], int] = {}
    for idx, row in candidates_df.iterrows():
        player_id = str(row.get("player_id", "")).strip()
        if player_id:
            by_id[player_id] = int(idx)
        name = _player_label(row).strip().lower()
        team = _normalize_team(row.get("team", "")).lower()
        if name and team:
            by_name_team[(name, team)] = int(idx)
    return by_id, by_name_team


def match_manual_rows_to_candidates(
    manual_df: pd.DataFrame,
    candidates_df: pd.DataFrame,
) -> pd.DataFrame:
    """Annotate manual rows with match status against official candidates."""
    by_id, by_name_team = _build_candidate_index(candidates_df)
    rows: list[dict[str, Any]] = []
    for _, row in manual_df.iterrows():
        player_id = str(row.get("player_id", "")).strip()
        name = str(row.get("player_name", row.get("player", ""))).strip().lower()
        team = _normalize_team(row.get("team", "")).lower()
        matched_idx: int | None = None
        match_method = "unmatched"
        if player_id and player_id in by_id:
            matched_idx = by_id[player_id]
            match_method = "player_id"
        elif name and team and (name, team) in by_name_team:
            matched_idx = by_name_team[(name, team)]
            match_method = "player_name_team"
        record = row.to_dict()
        record["match_status"] = "matched" if matched_idx is not None else "unmatched"
        record["match_method"] = match_method
        record["matched_candidate_index"] = matched_idx
        rows.append(record)
    return pd.DataFrame(rows)


def _apply_single_manual_override(
    candidate_row: pd.Series,
    manual_row: pd.Series,
) -> tuple[pd.Series, dict[str, Any], bool]:
    """Apply one manual override row to a candidate; return updated row, change log, invalid flag."""
    out = candidate_row.copy()
    change_log: dict[str, Any] = {
        "player_id": out.get("player_id"),
        "player_name": _player_label(out),
        "team": out.get("team"),
        "manual_prior_source": str(manual_row.get("manual_prior_source", "user_manual")).strip() or "user_manual",
    }
    invalid = False

    tier = _star_tier_key(manual_row.get("manual_star_tier"))
    tier_bonus = C.MANUAL_STAR_TIER_BONUSES[tier]
    out["base_player_rating"] = float(out.get("base_player_rating", 0)) + tier_bonus["base_player_rating"]
    out["star_role_score"] = float(out.get("star_role_score", 0)) + tier_bonus["star_role_score"]
    out["flair_score"] = float(out.get("flair_score", 0)) + tier_bonus["flair_score"]
    change_log["manual_star_tier"] = tier

    boost_map = {
        "manual_goal_prior_boost": "goals_prior",
        "manual_assist_prior_boost": "assists_prior",
        "manual_golden_boot_boost": "goals_prior",
        "manual_golden_glove_boost": "goalkeeper_actions_prior",
    }
    applied_boosts: dict[str, float] = {}
    for manual_col, target_col in boost_map.items():
        boost, was_invalid = _clip_boost(manual_col, manual_row.get(manual_col, 0))
        invalid = invalid or was_invalid
        if boost:
            out[target_col] = float(out.get(target_col, 0)) + boost
            applied_boosts[manual_col] = boost

    gb_boost, gb_invalid = _clip_boost("manual_golden_ball_boost", manual_row.get("manual_golden_ball_boost", 0))
    invalid = invalid or gb_invalid
    if gb_boost:
        out["star_role_score"] = float(out.get("star_role_score", 0)) + gb_boost * 20.0
        out["flair_score"] = float(out.get("flair_score", 0)) + gb_boost * 10.0
        out["base_player_rating"] = float(out.get("base_player_rating", 0)) + gb_boost * 15.0
        applied_boosts["manual_golden_ball_boost"] = gb_boost

    yp_boost, yp_invalid = _clip_boost("manual_young_player_boost", manual_row.get("manual_young_player_boost", 0))
    invalid = invalid or yp_invalid
    if yp_boost and is_young_player_eligible(out):
        out["star_role_score"] = float(out.get("star_role_score", 0)) + yp_boost * 15.0
        out["flair_score"] = float(out.get("flair_score", 0)) + yp_boost * 8.0
        applied_boosts["manual_young_player_boost"] = yp_boost

    minutes_boost, minutes_invalid = _clip_boost(
        "manual_minutes_confidence", manual_row.get("manual_minutes_confidence", 0)
    )
    invalid = invalid or minutes_invalid
    if minutes_boost:
        out["expected_minutes_share"] = float(
            max(0.0, min(1.0, float(out.get("expected_minutes_share", 0)) + minutes_boost))
        )
        applied_boosts["manual_minutes_confidence"] = minutes_boost

    pos_group = str(out.get("position_group", out.get("position", ""))).lower()
    pos_code = str(out.get("position_code", "")).upper()
    if pos_group != "goalkeeper" and pos_code != "GK" and applied_boosts.get("manual_golden_glove_boost"):
        # Glove boost ignored for non-goalkeepers (logged only).
        change_log["ignored_golden_glove_boost"] = True

    out["has_player_prior"] = True
    out["prior_source"] = "manual_override"
    out["manual_prior_applied"] = True
    out["manual_prior_notes"] = str(manual_row.get("manual_notes", "")).strip()
    change_log["applied_boosts"] = applied_boosts
    return out, change_log, invalid


def apply_manual_priors_to_candidates(
    candidates_df: pd.DataFrame,
    manual_df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Apply manual overrides to existing official candidates only."""
    valid, missing = validate_manual_prior_columns(manual_df)
    if not valid:
        raise ValueError(f"Manual prior file missing required columns: {missing}")

    out = candidates_df.copy()
    for col in C.PRIOR_NUMERIC_COLUMNS:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce").astype(float)
    if "manual_prior_applied" not in out.columns:
        out["manual_prior_applied"] = False

    matched_df = match_manual_rows_to_candidates(manual_df, out)
    overrides_applied = 0
    unmatched_ignored = 0
    invalid_boost_rows = 0
    change_logs: list[dict[str, Any]] = []

    for _, manual_row in matched_df.iterrows():
        if not _parse_bool(manual_row.get("apply_manual_override", False)):
            continue
        if manual_row.get("match_status") != "matched":
            unmatched_ignored += 1
            continue
        idx = int(manual_row["matched_candidate_index"])
        updated, change_log, had_invalid = _apply_single_manual_override(out.loc[idx], manual_row)
        for col, value in updated.items():
            out.at[idx, col] = value
        overrides_applied += 1
        if had_invalid:
            invalid_boost_rows += 1
        change_logs.append(change_log)

    summary: dict[str, Any] = {
        "status": "ok",
        "candidate_count": int(len(out)),
        "manual_rows_loaded": int(len(manual_df)),
        "overrides_applied": overrides_applied,
        "unmatched_manual_rows_ignored": unmatched_ignored,
        "invalid_boost_rows_clipped": invalid_boost_rows,
        "change_logs": change_logs,
        "disclaimer": C.MANUAL_PRIOR_DISCLAIMER,
    }
    return out, summary


def _rank_snapshot(players_df: pd.DataFrame, team_stage_df: pd.DataFrame | None = None) -> dict[str, pd.DataFrame]:
    """Compute compact top-15 ranking snapshots for major awards."""
    enriched = merge_players_with_team_progression(players_df, team_stage_df) if team_stage_df is not None else players_df
    snapshots = {
        "golden_ball": calculate_golden_ball_predictions(enriched).head(15),
        "golden_boot": calculate_golden_boot_predictions(enriched).head(15),
        "golden_glove": calculate_golden_glove_predictions(enriched).head(15),
        "young_player": calculate_young_player_predictions(enriched).head(15),
    }
    return snapshots


def _snapshot_rank_map(snapshot_df: pd.DataFrame, rank_col: str) -> dict[str, int]:
    name_col = "player_name" if "player_name" in snapshot_df.columns else "player"
    mapping: dict[str, int] = {}
    for _, row in snapshot_df.iterrows():
        key = f"{row.get(name_col)}|{row.get('team')}"
        mapping[str(key)] = int(row.get(rank_col, 9999))
    return mapping


def build_manual_prior_validation_report(
    before_players: pd.DataFrame,
    after_players: pd.DataFrame,
    summary: dict[str, Any],
    team_stage_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Build before/after ranking movement report for manual prior application."""
    before = _rank_snapshot(before_players, team_stage_df)
    after = _rank_snapshot(after_players, team_stage_df)
    award_specs = [
        ("golden_ball", "golden_ball_rank"),
        ("golden_boot", "golden_boot_rank"),
        ("golden_glove", "golden_glove_rank"),
        ("young_player", "young_player_rank"),
    ]
    rows: list[dict[str, Any]] = []
    changed_players = {log.get("player_id") for log in summary.get("change_logs", [])}

    summary_rows = [
        {"section": "summary", "metric": "candidate_count", "value": summary.get("candidate_count"), "detail": ""},
        {"section": "summary", "metric": "overrides_applied", "value": summary.get("overrides_applied"), "detail": ""},
        {
            "section": "summary",
            "metric": "unmatched_manual_rows_ignored",
            "value": summary.get("unmatched_manual_rows_ignored"),
            "detail": "",
        },
        {
            "section": "summary",
            "metric": "invalid_boost_rows_clipped",
            "value": summary.get("invalid_boost_rows_clipped"),
            "detail": "",
        },
    ]
    rows.extend(summary_rows)

    for award, rank_col in award_specs:
        before_map = _snapshot_rank_map(before[award], rank_col)
        after_map = _snapshot_rank_map(after[award], rank_col)
        keys = set(before_map) | set(after_map)
        for key in keys:
            player_name, team = key.split("|", 1)
            before_rank = before_map.get(key)
            after_rank = after_map.get(key)
            if before_rank is None and after_rank is None:
                continue
            movement = None
            if before_rank is not None and after_rank is not None:
                movement = before_rank - after_rank
            player_id = ""
            for log in summary.get("change_logs", []):
                if str(log.get("player_name")) == player_name and str(log.get("team")) == team:
                    player_id = str(log.get("player_id", ""))
                    break
            if player_id not in changed_players and movement in (None, 0):
                continue
            rows.append(
                {
                    "section": "rank_movement",
                    "award": award,
                    "player_id": player_id,
                    "player_name": player_name,
                    "team": team,
                    "rank_before": before_rank,
                    "rank_after": after_rank,
                    "rank_movement": movement,
                    "manual_override_applied": player_id in changed_players,
                }
            )

    for log in summary.get("change_logs", []):
        boosts = log.get("applied_boosts", {})
        for boost_name, boost_value in boosts.items():
            rows.append(
                {
                    "section": "applied_boost",
                    "player_id": log.get("player_id"),
                    "player_name": log.get("player_name"),
                    "team": log.get("team"),
                    "boost_column": boost_name,
                    "boost_value": boost_value,
                    "manual_prior_source": log.get("manual_prior_source"),
                }
            )

    return pd.DataFrame(rows)


def save_manual_prior_artifacts(
    summary: dict[str, Any],
    report_df: pd.DataFrame,
    *,
    output_dir: Path | None = None,
) -> dict[str, str]:
    """Persist manual prior summary JSON and validation CSV."""
    out_dir = output_dir or PROCESSED_DATA_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = out_dir / C.MANUAL_PRIOR_SUMMARY_FILE
    report_path = out_dir / C.MANUAL_PRIOR_VALIDATION_REPORT_FILE
    serializable = {k: v for k, v in summary.items() if k != "change_logs"}
    serializable["top_changed_players"] = [
        {
            "player_id": log.get("player_id"),
            "player_name": log.get("player_name"),
            "team": log.get("team"),
            "applied_boosts": log.get("applied_boosts", {}),
        }
        for log in summary.get("change_logs", [])
    ]
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)
    report_df.to_csv(report_path, index=False)
    return {"summary_path": str(summary_path), "validation_report_path": str(report_path)}


def apply_manual_prior_workflow(
    candidates_df: pd.DataFrame,
    manual_prior_file: str | Path,
    *,
    team_stage_df: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Full manual prior workflow with before/after validation artifacts."""
    manual_df = load_manual_prior_file(manual_prior_file)
    normalized = normalize_official_award_candidates(candidates_df)
    before_players = normalized.copy()
    after_players, summary = apply_manual_priors_to_candidates(normalized, manual_df)
    report_df = build_manual_prior_validation_report(before_players, after_players, summary, team_stage_df)
    paths = save_manual_prior_artifacts(summary, report_df)
    summary.update(paths)
    summary["manual_prior_file"] = str(manual_prior_file)
    return after_players, summary


def export_manual_prior_template(candidates_df: pd.DataFrame) -> pd.DataFrame:
    """Build an editable manual prior template from official/enriched candidates."""
    out = candidates_df.copy()
    out = normalize_official_award_candidates(out)

    def _eligible_awards(row: pd.Series) -> str:
        awards = ["golden_ball", "golden_boot"]
        pos = str(row.get("position_group", row.get("position", ""))).lower()
        code = str(row.get("position_code", "")).upper()
        if pos == "goalkeeper" or code == "GK":
            awards = ["golden_glove"]
        elif is_young_player_eligible(row):
            awards.extend(["young_player"])
        return ",".join(awards)

    template = pd.DataFrame(
        {
            "player_id": out.get("player_id", ""),
            "player_name": out.get("player_name", out.get("player", "")),
            "team": out.get("team", ""),
            "position_code": out.get("position_code", ""),
            "position": out.get("position_group", out.get("position", "")),
            "age_at_tournament_start": out.get("age_at_tournament_start", out.get("age", "")),
            "date_of_birth": out.get("date_of_birth", ""),
            "eligible_awards": out.apply(_eligible_awards, axis=1),
        }
    )
    for col in C.PRIOR_NUMERIC_COLUMNS:
        template[col] = pd.to_numeric(out.get(col, 0), errors="coerce").fillna(0)
    template["manual_star_tier"] = "none"
    for col in C.MANUAL_PRIOR_EDITABLE_COLUMNS:
        if col in {"manual_star_tier", "apply_manual_override", "manual_notes", "manual_prior_source"}:
            continue
        template[col] = 0.0
    template["manual_notes"] = ""
    template["manual_prior_source"] = "user_manual"
    template["apply_manual_override"] = False
    return template[C.MANUAL_PRIOR_TEMPLATE_COLUMNS]


def resolve_manual_prior_file(path: str | Path | None) -> Path:
    """Resolve manual prior file path with demo preset fallback."""
    if path is not None:
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = PROJECT_ROOT / candidate
        return candidate
    demo = PROJECT_ROOT / C.PLAYER_AWARD_MANUAL_PRIORS_DEMO_FILE
    if demo.is_file():
        return demo
    template = PROCESSED_DATA_DIR / C.MANUAL_PRIOR_TEMPLATE_FILE
    return template
