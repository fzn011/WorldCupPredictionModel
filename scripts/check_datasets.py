"""Dataset Availability Report.

Lists every registered data source and indicates whether a real file is
present under ``data/raw/`` or whether the sample fallback will be used.

Usage::

    python scripts/check_datasets.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `src` importable when running this script directly.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.data_sources import DATA_SOURCES  # noqa: E402


def main() -> int:
    """Print a clean dataset availability report."""
    print("## Dataset Availability Report")
    for key, cfg in DATA_SOURCES.items():
        if cfg.expected_path.is_file():
            status = f"FOUND real file -> {cfg.expected_path}"
        else:
            status = (
                f"MISSING real file, using sample fallback -> {cfg.sample_path}"
            )
        print(f"- {cfg.name}: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
