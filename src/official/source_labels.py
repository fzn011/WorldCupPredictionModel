"""Official vs sample source label helpers (Step 17H)."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

OFFICIAL_SOURCE_LABELS: set[str] = {
    "fifa_schedule_api",
    "fifa_schedule_page",
    "fifa_scores_fixtures_page",
    "fifa_downloadable_schedule",
    "fifa_squad_pdf",
    "fifa_squad_file",
    "fifa_squad_confirmation_page",
    "fifa_teams_page",
    "fifa_manual_verified",
}

SAMPLE_SOURCE_LABELS: set[str] = {
    "sample_to_be_verified",
    "ai_prefilled_needs_verification",
    "sample",
    "template",
    "manual_template",
}


def is_sample_source_label(value: str) -> bool:
    if not value or not str(value).strip():
        return False
    return str(value).strip().lower() in {s.lower() for s in SAMPLE_SOURCE_LABELS}


def is_official_source_label(value: str) -> bool:
    if not value or not str(value).strip():
        return False
    v = str(value).strip().lower()
    if v in {s.lower() for s in OFFICIAL_SOURCE_LABELS}:
        return True
    return v.startswith("fifa_")


def replace_sample_source_labels_for_verified_imports(
    df: pd.DataFrame,
    dataset_name: str,
    official_source_label: str,
    require_min_rows: int | None = None,
) -> pd.DataFrame:
    """Replace sample labels when dataset is verified imported FIFA data."""
    if df.empty or "source" not in df.columns:
        return df
    if require_min_rows is not None and len(df) < require_min_rows:
        return df
    out = df.copy()
    sources = out["source"].fillna("").astype(str)
    has_fifa_import = sources.str.lower().isin(
        {"fifa_downloadable_schedule", "fifa_schedule_api", "fifa_squad_file", "fifa_squad_pdf"}
    ).any()
    sample_mask = sources.map(is_sample_source_label)
    if not sample_mask.any() and not has_fifa_import:
        return out
    if has_fifa_import or (require_min_rows and len(out) >= require_min_rows):
        replace_mask = sample_mask | sources.str.lower().isin(
            {"fifa_downloadable_schedule", "fifa_schedule_api", "fifa_squad_file", "fifa_squad_pdf"}
        )
        out.loc[replace_mask, "source"] = official_source_label
        if "verification_notes" not in out.columns:
            out["verification_notes"] = ""
        verified_at = datetime.now(timezone.utc).isoformat()
        out.loc[replace_mask, "verification_notes"] = out.loc[replace_mask, "verification_notes"].replace(
            "", f"Verified {dataset_name} import {verified_at}"
        )
    return out
