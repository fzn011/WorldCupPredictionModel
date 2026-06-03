"""Step 2 dataset preparation pipeline.

Loads every registered dataset (real or sample fallback), validates it,
converts historical match results to the canonical schema, and saves a
processed sample copy to ``data/processed/canonical_matches_sample.csv``.

Does **not** train any model.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.data.clean_data import (
    build_team_registry,
    clean_historical_results,
    clean_shootouts,
    convert_historical_results_to_canonical,
)
from src.data.load_data import (
    dataset_uses_real_file,
    load_elo_ratings,
    load_fifa_rankings,
    load_historical_results,
    load_shootouts,
    load_wc2026_groups,
    load_wc2026_schedule,
    load_wc2026_teams,
    real_file_exists,
)
from src.data.validate_data import (
    validate_canonical_matches,
    validate_elo_ratings,
    validate_fifa_rankings,
    validate_historical_results,
    validate_team_registry,
    validate_wc2026_groups,
    validate_wc2026_schedule,
    validate_wc2026_teams,
)
from src.utils.constants import (
    CANONICAL_MATCHES_FILE,
    CANONICAL_MATCHES_SAMPLE_FILE,
    CLEANING_SUMMARY_FILE,
    DATA_QUALITY_REPORT_FILE,
    PROCESSED_DATA_DIR,
    SHOOTOUT_OUTCOMES_FILE,
    TEAM_REGISTRY_FILE,
)

CANONICAL_SAMPLE_FILENAME = "canonical_matches_sample.csv"


def prepare_step2_datasets() -> dict:
    """Load + validate every dataset and emit a canonical match CSV.

    Returns:
        Summary dictionary with row counts, the output canonical path,
        and a status message.
    """
    summary: dict = {"rows": {}, "real_data_used": {}, "messages": []}

    # 1. Historical results --------------------------------------------------
    results_df = load_historical_results()
    validate_historical_results(results_df)
    summary["rows"]["historical_results"] = len(results_df)
    summary["real_data_used"]["historical_results"] = real_file_exists(
        "historical_results"
    )

    canonical_df = convert_historical_results_to_canonical(results_df)
    summary["rows"]["canonical_matches"] = len(canonical_df)

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    canonical_path: Path = PROCESSED_DATA_DIR / CANONICAL_SAMPLE_FILENAME

    if not real_file_exists("historical_results"):
        canonical_df.to_csv(canonical_path, index=False)
        summary["messages"].append(
            f"Sample-based canonical matches written to {canonical_path}."
        )
    else:
        # Still write it so downstream steps have something to read.
        canonical_df.to_csv(canonical_path, index=False)
        summary["messages"].append(
            f"Real-data canonical matches written to {canonical_path}."
        )
    summary["canonical_matches_path"] = str(canonical_path)

    # 2. FIFA rankings -------------------------------------------------------
    fifa_df = load_fifa_rankings()
    validate_fifa_rankings(fifa_df)
    summary["rows"]["fifa_rankings"] = len(fifa_df)
    summary["real_data_used"]["fifa_rankings"] = real_file_exists("fifa_rankings")

    # 3. Elo ratings ---------------------------------------------------------
    elo_df = load_elo_ratings()
    validate_elo_ratings(elo_df)
    summary["rows"]["elo_ratings"] = len(elo_df)
    summary["real_data_used"]["elo_ratings"] = real_file_exists("elo_ratings")

    # 4. WC2026 teams --------------------------------------------------------
    teams_df = load_wc2026_teams()
    validate_wc2026_teams(teams_df)
    summary["rows"]["wc2026_teams"] = len(teams_df)
    summary["real_data_used"]["wc2026_teams"] = real_file_exists("wc2026_teams")

    # 5. WC2026 groups -------------------------------------------------------
    groups_df = load_wc2026_groups()
    validate_wc2026_groups(groups_df)
    summary["rows"]["wc2026_groups"] = len(groups_df)
    summary["real_data_used"]["wc2026_groups"] = real_file_exists("wc2026_groups")

    # 6. WC2026 schedule -----------------------------------------------------
    schedule_df = load_wc2026_schedule()
    validate_wc2026_schedule(schedule_df)
    summary["rows"]["wc2026_schedule"] = len(schedule_df)
    summary["real_data_used"]["wc2026_schedule"] = real_file_exists(
        "wc2026_schedule"
    )

    summary["status"] = "ok"
    return summary


def _build_data_quality_report(canonical_df) -> "list[dict]":
    """Compute per-column missing-value statistics for the canonical data."""
    total = len(canonical_df)
    report: list[dict] = []
    for col in canonical_df.columns:
        missing = int(canonical_df[col].isna().sum())
        pct = round((missing / total) * 100, 2) if total else 0.0
        report.append(
            {
                "column": col,
                "missing_count": missing,
                "missing_pct": pct,
                "dtype": str(canonical_df[col].dtype),
            }
        )
    return report


def prepare_step3_clean_datasets() -> dict:
    """Step 3 pipeline: clean raw data and build the canonical dataset.

    Loads historical results and shootouts, deep-cleans both, converts to the
    full canonical schema (merging shootouts), builds a team registry, and
    writes processed outputs. Uses real Kaggle data when present, otherwise
    falls back to the bundled sample data.

    Returns:
        Summary dictionary with row counts, output paths, and status.
    """
    import pandas as pd  # local import to keep module import light

    summary: dict = {"messages": [], "paths": {}, "real_data_used": {}}

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load + validate raw historical results -----------------------------
    raw_results = load_historical_results()
    validate_historical_results(raw_results)
    summary["raw_rows"] = len(raw_results)
    uses_real = dataset_uses_real_file("historical_results")
    summary["real_data_used"]["historical_results"] = uses_real

    cleaned_results = clean_historical_results(raw_results)
    summary["cleaned_rows"] = len(cleaned_results)

    # 2. Load + clean shootouts ---------------------------------------------
    raw_shootouts = load_shootouts()
    summary["shootouts_loaded"] = len(raw_shootouts)
    cleaned_shootouts = clean_shootouts(raw_shootouts)

    # 3. Build canonical matches (with shootout merge) ----------------------
    data_source = "kaggle_real" if uses_real else "sample_fallback"
    canonical_df = convert_historical_results_to_canonical(
        cleaned_results,
        shootouts_df=cleaned_shootouts,
        data_source=data_source,
    )
    validate_canonical_matches(canonical_df)
    summary["canonical_rows"] = len(canonical_df)
    summary["shootouts_merged"] = int(canonical_df["has_shootout"].sum())

    # 4. Team registry ------------------------------------------------------
    registry_df = build_team_registry(canonical_df)
    validate_team_registry(registry_df)
    summary["unique_teams"] = len(registry_df)

    # 5. Save outputs -------------------------------------------------------
    canonical_name = (
        CANONICAL_MATCHES_FILE if uses_real else CANONICAL_MATCHES_SAMPLE_FILE
    )
    canonical_path = PROCESSED_DATA_DIR / canonical_name
    registry_path = PROCESSED_DATA_DIR / TEAM_REGISTRY_FILE
    shootouts_path = PROCESSED_DATA_DIR / SHOOTOUT_OUTCOMES_FILE
    quality_path = PROCESSED_DATA_DIR / DATA_QUALITY_REPORT_FILE
    cleaning_path = PROCESSED_DATA_DIR / CLEANING_SUMMARY_FILE

    canonical_df.to_csv(canonical_path, index=False)
    registry_df.to_csv(registry_path, index=False)
    cleaned_shootouts.to_csv(shootouts_path, index=False)

    quality_report = _build_data_quality_report(canonical_df)
    pd.DataFrame(quality_report).to_csv(quality_path, index=False)

    cleaning_summary = {
        "raw_rows": summary["raw_rows"],
        "cleaned_rows": summary["cleaned_rows"],
        "canonical_rows": summary["canonical_rows"],
        "unique_teams": summary["unique_teams"],
        "shootouts_loaded": summary["shootouts_loaded"],
        "shootouts_merged": summary["shootouts_merged"],
        "real_data_used": uses_real,
        "data_source": data_source,
    }
    cleaning_path.write_text(json.dumps(cleaning_summary, indent=2))

    summary["paths"] = {
        "canonical_matches": str(canonical_path),
        "team_registry": str(registry_path),
        "shootout_outcomes": str(shootouts_path),
        "data_quality_report": str(quality_path),
        "cleaning_summary": str(cleaning_path),
    }
    summary["messages"].append(
        f"Canonical matches ({data_source}) written to {canonical_path}."
    )
    summary["status"] = "ok"
    return summary


if __name__ == "__main__":
    print(prepare_step3_clean_datasets())
