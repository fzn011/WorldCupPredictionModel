"""Prepare official-style World Cup 2026 data bundle."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.official.prepare_official_data import prepare_step17a_official_worldcup_data  # noqa: E402
from src.official.loaders import official_path  # noqa: E402
import src.utils.constants as C  # noqa: E402

DATA_MODE_OFFICIAL = getattr(C, "DATA_MODE_OFFICIAL", "official")
DATA_MODE_SAMPLE = getattr(C, "DATA_MODE_SAMPLE", "sample")
OFFICIAL_DATA_VALIDATION_REPORT_FILE = getattr(C, "OFFICIAL_DATA_VALIDATION_REPORT_FILE", "official_data_validation_report.csv")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare official-style World Cup 2026 data.")
    parser.add_argument("--mode", choices=[DATA_MODE_OFFICIAL, DATA_MODE_SAMPLE], default=DATA_MODE_OFFICIAL)
    parser.add_argument("--strict-full-schedule", action="store_true")
    return parser



def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    summary = prepare_step17a_official_worldcup_data(
        data_mode=args.mode,
        strict_full_schedule=bool(args.strict_full_schedule),
    )

    print("=== Step 17A Official World Cup Data Summary ===")
    for key in [
        "status",
        "validation_passed",
        "teams_count",
        "groups_count",
        "fixtures_count",
        "venues_count",
        "errors_count",
        "warnings_count",
        "official_teams_path",
        "official_groups_path",
        "official_fixtures_path",
        "official_venues_path",
        "official_summary_path",
        "validation_report_path",
    ]:
        print(f"{key}: {summary.get(key)}")

    validation_path = official_path(OFFICIAL_DATA_VALIDATION_REPORT_FILE)
    if validation_path.is_file():
        validation_df = pd.read_csv(validation_path)
        failed = validation_df[validation_df["passed"] == False].head(20)
        if not failed.empty:
            print("\nFirst 20 failed validation rows:")
            print(failed.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
