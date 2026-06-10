"""Step 19 player prior enrichment for official award candidates."""

from __future__ import annotations

import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C
from src.awards.award_data import (
    normalize_official_award_candidates,
    require_official_final_ready,
)
from src.official.loaders import load_official_players
from src.utils.team_name_mapping import standardize_team_name

PROJECT_ROOT = C.PROJECT_ROOT
PROCESSED_DATA_DIR = PROJECT_ROOT / C.PROCESSED_DATA_DIR

_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_FLAT_SIGNATURE = {
    "base_player_rating": 50.0,
    "expected_minutes_share": 0.5,
    "goals_prior": 0.0,
    "assists_prior": 0.0,
    "chance_creation_prior": 0.0,
    "defensive_actions_prior": 0.0,
    "goalkeeper_actions_prior": 0.0,
    "discipline_risk": 0.5,
    "star_role_score": 0.0,
    "flair_score": 0.0,
}


def load_current_award_candidates() -> pd.DataFrame:
    """Load official award candidates (official_final required)."""
    require_official_final_ready()
    path = PROCESSED_DATA_DIR / C.OFFICIAL_AWARD_CANDIDATES_FILE
    if not path.is_file():
        raise FileNotFoundError(
            f"Official award candidates not found: {path}. Run official squads merge first."
        )
    df = pd.read_csv(path)
    missing = [c for c in C.OFFICIAL_AWARD_CANDIDATES_REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Official award candidates missing required columns: {missing}")
    return normalize_official_award_candidates(df)


def infer_position_group(row: pd.Series) -> str:
    """Map position_code/position to goalkeeper/defender/midfielder/forward."""
    code = str(row.get("position_code", "")).strip().upper()
    pos = str(row.get("position", "")).strip().upper()
    if code in C.AWARD_POSITION_GROUPS:
        return C.AWARD_POSITION_GROUPS[code]
    if pos in C.AWARD_POSITION_GROUPS:
        return C.AWARD_POSITION_GROUPS[pos]
    pos_lower = str(row.get("position", "")).strip().lower()
    if pos_lower in C.PLAYER_POSITIONS:
        return pos_lower
    if pos_lower in {"gk", "goalkeeper"}:
        return "goalkeeper"
    if pos_lower in {"df", "defender"}:
        return "defender"
    if pos_lower in {"mf", "midfielder"}:
        return "midfielder"
    if pos_lower in {"fw", "forward"}:
        return "forward"
    return "midfielder"


def _is_flat_prior_row(row: pd.Series) -> bool:
    """Detect generic placeholder priors (even when has_player_prior=True)."""
    for col, expected in _FLAT_SIGNATURE.items():
        val = pd.to_numeric(row.get(col), errors="coerce")
        if pd.isna(val) or abs(float(val) - expected) > 1e-9:
            return False
    return True


def _should_preserve_user_prior(row: pd.Series) -> bool:
    return bool(row.get("has_player_prior", False)) and not _is_flat_prior_row(row)


def fix_squad_metadata_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Repair common squad import column swaps (DOB/club/height)."""
    out = df.copy()
    if "club_country" not in out.columns:
        out["club_country"] = ""

    for idx, row in out.iterrows():
        dob = str(row.get("date_of_birth", "")).strip()
        club = str(row.get("club", "")).strip()
        height = row.get("height_cm")

        if dob and not _DATE_PATTERN.match(dob) and (not club or club.lower() in {"nan", ""}):
            out.at[idx, "club"] = dob
            out.at[idx, "date_of_birth"] = ""
            club = dob

        if club and "(" in club and ")" in club and not str(out.at[idx, "club_country"]).strip():
            match = re.search(r"\(([A-Z]{3})\)\s*$", club)
            if match:
                out.at[idx, "club_country"] = match.group(1)

        if pd.isna(height) or str(height).strip() == "":
            continue
        try:
            h = float(height)
            if h < 100 or h > 230:
                if _DATE_PATTERN.match(str(height)):
                    out.at[idx, "date_of_birth"] = str(height)
                    out.at[idx, "height_cm"] = pd.NA
        except (TypeError, ValueError):
            pass

    return out


def create_position_based_default_priors(candidates_df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing or flat priors using position defaults; preserve real user priors."""
    out = candidates_df.copy()
    for col in C.PRIOR_NUMERIC_COLUMNS:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce").astype(float)
    out["position_group"] = out.apply(infer_position_group, axis=1)
    out["prior_enrichment_source"] = ""
    out["prior_enrichment_notes"] = ""

    for idx, row in out.iterrows():
        group = str(row["position_group"])
        defaults = C.DEFAULT_PRIOR_BY_POSITION.get(group, C.DEFAULT_PRIOR_BY_POSITION["midfielder"])
        preserve = _should_preserve_user_prior(row)
        filled_cols: list[str] = []

        if not preserve:
            for col, default_val in defaults.items():
                out.at[idx, col] = float(default_val)
                filled_cols.append(col)

        if preserve:
            out.at[idx, "prior_enrichment_source"] = "user_prior"
            out.at[idx, "prior_enrichment_notes"] = "Preserved non-flat user priors"
        elif filled_cols and len(filled_cols) < len(defaults):
            out.at[idx, "prior_enrichment_source"] = "mixed_user_and_position_default"
            out.at[idx, "prior_enrichment_notes"] = f"Filled: {', '.join(filled_cols)}"
        else:
            out.at[idx, "prior_enrichment_source"] = "position_default"
            out.at[idx, "prior_enrichment_notes"] = f"Position defaults applied ({group})"

        if not preserve:
            out.at[idx, "has_player_prior"] = True
            out.at[idx, "prior_source"] = "step19_position_enrichment"

    return out


def apply_team_progression_prior_adjustment(
    priors_df: pd.DataFrame,
    team_stage_df: pd.DataFrame,
) -> pd.DataFrame:
    """Apply small uplift from Monte Carlo team progression (conservative)."""
    out = priors_df.copy()
    stages = team_stage_df.copy()
    stages["team"] = stages["team"].map(standardize_team_name)
    out["team"] = out["team"].map(standardize_team_name)
    merged = out.merge(
        stages[["team", "final_probability", "champion_probability"]],
        on="team",
        how="left",
    )
    for col in ("final_probability", "champion_probability"):
        merged[col] = pd.to_numeric(merged[col], errors="coerce").fillna(0.0)

    multiplier = 1.0 + merged["champion_probability"] * 0.10 + merged["final_probability"] * 0.05
    merged["expected_minutes_share"] = (
        pd.to_numeric(merged["expected_minutes_share"], errors="coerce").fillna(0.5) * multiplier
    ).clip(0.0, 1.0)
    merged["star_role_score"] = pd.to_numeric(merged["star_role_score"], errors="coerce").fillna(0.0) * multiplier
    merged["base_player_rating"] = (
        pd.to_numeric(merged["base_player_rating"], errors="coerce").fillna(50.0) + (multiplier - 1.0) * 5.0
    ).clip(40.0, 95.0)

    notes = merged.get("prior_enrichment_notes", pd.Series("", index=merged.index)).astype(str)
    merged["prior_enrichment_notes"] = notes + "; team_progression_adjustment"
    return merged.drop(columns=["final_probability", "champion_probability"], errors="ignore")


def apply_squad_role_heuristics(priors_df: pd.DataFrame) -> pd.DataFrame:
    """Light shirt-number and position heuristics (conservative)."""
    out = priors_df.copy()
    out["heuristic_flags"] = ""

    for idx, row in out.iterrows():
        flags: list[str] = []
        group = infer_position_group(row)
        shirt = pd.to_numeric(row.get("shirt_number"), errors="coerce")

        if group == "goalkeeper" and pd.notna(shirt) and shirt <= 2:
            out.at[idx, "expected_minutes_share"] = min(
                1.0,
                float(pd.to_numeric(out.at[idx, "expected_minutes_share"], errors="coerce") or 0.35) + 0.08,
            )
            flags.append("gk_starter_shirt")

        if group == "forward":
            boost = 0.0
            if pd.notna(shirt) and shirt in {9, 10, 11}:
                boost = 0.25
                flags.append("forward_attacking_shirt")
            out.at[idx, "goals_prior"] = float(pd.to_numeric(out.at[idx, "goals_prior"], errors="coerce") or 0) + boost
            out.at[idx, "star_role_score"] = float(pd.to_numeric(out.at[idx, "star_role_score"], errors="coerce") or 0) + boost

        if group == "defender":
            out.at[idx, "defensive_actions_prior"] = float(
                pd.to_numeric(out.at[idx, "defensive_actions_prior"], errors="coerce") or 0
            ) + 0.5
            flags.append("defender_actions_boost")

        if group == "midfielder" and pd.notna(shirt) and shirt in {8, 10}:
            out.at[idx, "chance_creation_prior"] = float(
                pd.to_numeric(out.at[idx, "chance_creation_prior"], errors="coerce") or 0
            ) + 0.5
            flags.append("midfield_creator_shirt")

        out.at[idx, "heuristic_flags"] = ",".join(flags) if flags else ""

    return out


def measure_prior_quality(priors_df: pd.DataFrame) -> tuple[dict[str, Any], pd.DataFrame]:
    """Compute prior quality metrics and warning rows."""
    n = len(priors_df)
    source_counts = priors_df.get("prior_enrichment_source", pd.Series(dtype=str)).value_counts().to_dict()
    share_user = float(source_counts.get("user_prior", 0) / n) if n else 0.0
    share_default = float(source_counts.get("position_default", 0) / n) if n else 0.0
    share_mixed = float(source_counts.get("mixed_user_and_position_default", 0) / n) if n else 0.0

    flat_count = int(priors_df.apply(_is_flat_prior_row, axis=1).sum()) if n else 0
    flatness_score = float(flat_count / n) if n else 1.0

    distinct_rating = int(priors_df["base_player_rating"].nunique()) if "base_player_rating" in priors_df else 0
    distinct_goals = int(priors_df["goals_prior"].nunique()) if "goals_prior" in priors_df else 0
    distinct_star = int(priors_df["star_role_score"].nunique()) if "star_role_score" in priors_df else 0

    non_default_share = 1.0 - flatness_score
    warnings: list[str] = []
    if flatness_score >= C.PLAYER_PRIOR_FLATNESS_WARNING_THRESHOLD:
        warnings.append("High flatness score: priors still look mostly uniform")
    if non_default_share < C.PLAYER_PRIOR_MIN_NON_DEFAULT_SHARE:
        warnings.append("Low non-default prior share after enrichment")

    summary = {
        "candidate_count": n,
        "share_with_user_prior": round(share_user, 4),
        "share_position_default": round(share_default, 4),
        "share_mixed": round(share_mixed, 4),
        "distinct_base_player_rating": distinct_rating,
        "distinct_goals_prior": distinct_goals,
        "distinct_star_role_score": distinct_star,
        "flatness_score": round(flatness_score, 4),
        "non_default_share": round(non_default_share, 4),
        "warnings": warnings,
    }

    rows = [
        {"metric": k, "value": v}
        for k, v in summary.items()
        if k != "warnings"
    ]
    for w in warnings:
        rows.append({"metric": "warning", "value": w})
    report_df = pd.DataFrame(rows)
    return summary, report_df


def _load_team_stages_optional() -> pd.DataFrame:
    path = PROCESSED_DATA_DIR / C.MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE
    if not path.is_file():
        return pd.DataFrame(columns=["team", "final_probability", "champion_probability"])
    df = pd.read_csv(path)
    df["team"] = df["team"].map(standardize_team_name)
    return df


def create_enriched_player_priors() -> dict[str, Any]:
    """Build enriched priors from official candidates and save reports."""
    candidates = load_current_award_candidates()
    before_summary, _ = measure_prior_quality(candidates)

    fixed = fix_squad_metadata_fields(candidates)
    with_defaults = create_position_based_default_priors(fixed)
    stages = _load_team_stages_optional()
    if not stages.empty:
        adjusted = apply_team_progression_prior_adjustment(with_defaults, stages)
    else:
        adjusted = with_defaults.copy()
    enriched = apply_squad_role_heuristics(adjusted)

    quality_summary, quality_df = measure_prior_quality(enriched)

    priors_path = PROCESSED_DATA_DIR / C.ENRICHED_PLAYER_AWARD_PRIORS_FILE
    quality_path = PROCESSED_DATA_DIR / C.PLAYER_PRIOR_QUALITY_REPORT_FILE
    enrichment_path = PROCESSED_DATA_DIR / C.PLAYER_PRIOR_ENRICHMENT_REPORT_FILE

    priors_path.parent.mkdir(parents=True, exist_ok=True)
    enriched.to_csv(priors_path, index=False)
    quality_df.to_csv(quality_path, index=False)

    enrichment_rows = pd.DataFrame(
        [
            {"phase": "before", "metric": k, "value": v}
            for k, v in before_summary.items()
            if k != "warnings"
        ]
        + [
            {"phase": "after", "metric": k, "value": v}
            for k, v in quality_summary.items()
            if k != "warnings"
        ]
    )
    enrichment_rows.to_csv(enrichment_path, index=False)

    return {
        "status": "ok",
        "candidate_count": quality_summary["candidate_count"],
        "share_with_user_prior": quality_summary["share_with_user_prior"],
        "flatness_score_before": before_summary.get("flatness_score"),
        "flatness_score": quality_summary["flatness_score"],
        "non_default_share": quality_summary["non_default_share"],
        "output_path": str(priors_path),
        "quality_report_path": str(quality_path),
        "enrichment_report_path": str(enrichment_path),
        "warnings": quality_summary.get("warnings", []),
    }


def merge_enriched_priors_into_award_candidates(*, update_official: bool = False) -> dict[str, Any]:
    """Merge enriched priors back into award candidates; optional official file update."""
    enriched_path = PROCESSED_DATA_DIR / C.ENRICHED_PLAYER_AWARD_PRIORS_FILE
    if not enriched_path.is_file():
        create_enriched_player_priors()

    enriched = pd.read_csv(enriched_path)
    base = load_current_award_candidates()
    official_players = load_official_players()
    allowed_ids = set(official_players["player_id"].astype(str))

    enriched_ids = set(enriched["player_id"].astype(str))
    base_ids = set(base["player_id"].astype(str))
    if enriched_ids != base_ids:
        raise ValueError(
            f"Enriched player_id set mismatch: enriched={len(enriched_ids)} base={len(base_ids)}"
        )
    if not enriched_ids.issubset(allowed_ids):
        raise ValueError("Enriched priors contain non-official player_id values")

    prior_cols = [c for c in C.PRIOR_NUMERIC_COLUMNS if c in enriched.columns]
    meta_cols = [
        "prior_enrichment_source",
        "prior_enrichment_notes",
        "heuristic_flags",
        "position_group",
    ]
    merge_cols = ["player_id", *prior_cols, *[c for c in meta_cols if c in enriched.columns]]
    merged = base.drop(columns=[c for c in prior_cols + meta_cols if c in base.columns], errors="ignore")
    merged = merged.merge(enriched[merge_cols], on="player_id", how="left")
    merged = fix_squad_metadata_fields(merged)

    enriched_candidates_path = PROCESSED_DATA_DIR / C.ENRICHED_OFFICIAL_AWARD_CANDIDATES_FILE
    merged.to_csv(enriched_candidates_path, index=False)

    official_updated = False
    backup_path = ""
    if update_official:
        official_path = PROCESSED_DATA_DIR / C.OFFICIAL_AWARD_CANDIDATES_FILE
        backup_dir = PROCESSED_DATA_DIR / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_path = str(backup_dir / f"official_award_candidates_backup_{ts}.csv")
        shutil.copy2(official_path, backup_path)
        merged.drop(columns=[c for c in meta_cols if c in merged.columns], errors="ignore").to_csv(
            official_path, index=False
        )
        official_updated = True

    return {
        "status": "ok",
        "candidate_count": len(merged),
        "enriched_candidates_path": str(enriched_candidates_path),
        "official_award_candidates_updated": official_updated,
        "backup_path": backup_path,
        "player_id_set_unchanged": True,
    }
