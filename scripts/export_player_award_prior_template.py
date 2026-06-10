#!/usr/bin/env python
"""Export editable manual player award prior template from official candidates (Step 20)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import src.utils.constants as C  # noqa: E402
from src.awards.award_data import load_official_award_candidates  # noqa: E402
from src.awards.manual_priors import export_manual_prior_template  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export manual player award prior template")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--use-enriched", action="store_true", help="Use enriched official candidates")
    group.add_argument("--no-enriched", action="store_true", help="Use base official_award_candidates.csv")
    parser.add_argument(
        "--output",
        default=str(C.PROJECT_ROOT / C.PROCESSED_DATA_DIR / C.MANUAL_PRIOR_TEMPLATE_FILE),
        help="Output CSV path",
    )
    args = parser.parse_args(argv)

    use_enriched: bool | None = None
    if args.use_enriched:
        use_enriched = True
    elif args.no_enriched:
        use_enriched = False

    try:
        candidates = load_official_award_candidates(use_enriched_candidates=use_enriched)
    except (RuntimeError, FileNotFoundError) as exc:
        print(str(exc))
        return 1

    template = export_manual_prior_template(candidates)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    template.to_csv(output_path, index=False)

    print("=== Step 20 Manual Prior Template Export ===")
    print(f"status: ok")
    print(f"candidate_count: {len(template)}")
    print(f"output_path: {output_path}")
    print("Set apply_manual_override=True and edit boost columns for star players.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
