#!/usr/bin/env python
"""Enrich official player award priors (Step 19)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.awards.prior_enrichment import (  # noqa: E402
    create_enriched_player_priors,
    merge_enriched_priors_into_award_candidates,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich official player award priors")
    parser.add_argument(
        "--update-award-candidates",
        action="store_true",
        help="Also update official_award_candidates.csv (creates backup first)",
    )
    args = parser.parse_args()

    try:
        summary = create_enriched_player_priors()
        merge_summary = merge_enriched_priors_into_award_candidates(
            update_official=args.update_award_candidates
        )
    except (RuntimeError, FileNotFoundError, ValueError) as exc:
        print(str(exc))
        return 1

    print("=== Step 19 Player Prior Enrichment ===")
    for key in [
        "status",
        "candidate_count",
        "share_with_user_prior",
        "flatness_score_before",
        "flatness_score",
        "non_default_share",
        "output_path",
        "quality_report_path",
        "enrichment_report_path",
    ]:
        print(f"{key}: {summary.get(key)}")
    print(f"enriched_candidates_path: {merge_summary.get('enriched_candidates_path')}")
    print(f"official_award_candidates_updated: {merge_summary.get('official_award_candidates_updated')}")
    if merge_summary.get("backup_path"):
        print(f"backup_path: {merge_summary.get('backup_path')}")
    if summary.get("warnings"):
        print("warnings:", "; ".join(summary["warnings"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
