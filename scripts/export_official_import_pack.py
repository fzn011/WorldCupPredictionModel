#!/usr/bin/env python
"""Export Step 17E downloadable official import pack."""

from __future__ import annotations

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.official.import_pack import create_import_pack_summary, create_import_pack_zip


def main() -> None:
    zip_path = create_import_pack_zip()
    summary = create_import_pack_summary()

    print("=" * 60)
    print("Step 17E: Export Official Import Pack")
    print("=" * 60)
    print(f"Zip path:         {zip_path}")
    print(f"Files included:   {len(summary.get('files_included', []))}")
    for name in summary.get("files_included", [])[:20]:
        print(f"  - {name}")
    if len(summary.get("files_included", [])) > 20:
        print("  ...")
    print("=" * 60)


if __name__ == "__main__":
    main()
