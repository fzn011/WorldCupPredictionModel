"""FIFA/external stage name normalization for official fixtures (Step 17H)."""

from __future__ import annotations

import re

import pandas as pd

FIFA_STAGE_TO_INTERNAL_STAGE: dict[str, str] = {
    "First Stage": "group_stage",
    "Group Stage": "group_stage",
    "group stage": "group_stage",
    "group_stage": "group_stage",
    "Round of 32": "round_of_32",
    "Round of 16": "round_of_16",
    "Quarter-final": "quarter_final",
    "Quarter-finals": "quarter_final",
    "Quarter Final": "quarter_final",
    "Semi-final": "semi_final",
    "Semi-finals": "semi_final",
    "Semi Final": "semi_final",
    "Third-place match": "third_place",
    "Play-off for third place": "third_place",
    "Final": "final",
    "Knockout": "knockout",
}

KNOCKOUT_STAGES = {
    "round_of_32",
    "round_of_16",
    "quarter_final",
    "semi_final",
    "third_place",
    "final",
    "knockout",
}


def normalize_stage_name(stage: str) -> str:
    """Map FIFA/external stage labels to internal stage constants."""
    if not stage or not str(stage).strip():
        return ""
    raw = str(stage).strip()
    if raw in FIFA_STAGE_TO_INTERNAL_STAGE:
        return FIFA_STAGE_TO_INTERNAL_STAGE[raw]
    lower = raw.lower()
    for key, val in FIFA_STAGE_TO_INTERNAL_STAGE.items():
        if key.lower() == lower:
            return val
    slug = re.sub(r"[^a-z0-9]+", "_", lower).strip("_")
    return slug or lower


def is_group_stage_label(stage: str) -> bool:
    """True when stage normalizes to group_stage."""
    return normalize_stage_name(stage) == "group_stage"


def is_knockout_stage_label(stage: str) -> bool:
    """True for knockout bracket stages."""
    return normalize_stage_name(stage) in KNOCKOUT_STAGES


def apply_stage_normalization(fixtures_df: pd.DataFrame) -> pd.DataFrame:
    """Add original_stage and normalize stage column on fixtures."""
    if fixtures_df.empty or "stage" not in fixtures_df.columns:
        return fixtures_df
    out = fixtures_df.copy()
    out["original_stage"] = out["stage"].fillna("").astype(str)
    out["normalized_stage"] = out["original_stage"].map(normalize_stage_name)
    out["stage"] = out["normalized_stage"]
    return out
