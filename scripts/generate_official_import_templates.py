#!/usr/bin/env python
"""Generate manual import templates for official World Cup 2026 data.

This script generates CSV templates that can be used to manually import
verified official data from FIFA sources. Templates are pre-populated
with existing data if available.

Usage:
    python scripts/generate_official_import_templates.py [--empty]

Options:
    --empty    Generate empty templates instead of pre-populating with existing data
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.official.import_templates import generate_all_import_templates, create_import_manifest
from src.utils.constants import OFFICIAL_PROCESSED_DIR, PROJECT_ROOT


def main():
    """Generate all official import templates."""
    import argparse
    parser = argparse.ArgumentParser(description="Generate official import templates")
    parser.add_argument("--empty", action="store_true", help="Generate empty templates")
    args = parser.parse_args()

    print("=" * 60)
    print("FIFA World Cup 2026 - Official Import Template Generator")
    print("=" * 60)

    output_dir = PROJECT_ROOT / OFFICIAL_PROCESSED_DIR
    print(f"\nOutput directory: {output_dir}")
    print(f"Pre-populate with existing data: {not args.empty}")

    try:
        # Generate all templates
        print("\nGenerating import templates...")
        templates = generate_all_import_templates(
            output_dir=output_dir,
            include_existing_data=not args.empty,
        )

        # Create manifest
        manifest_path = create_import_manifest(templates, output_dir)

        print("\n✓ Templates generated successfully!")
        print("\nGenerated files:")
        for name, path in templates.items():
            exists = "✓" if path.exists() else "✗"
            print(f"  {exists} {path.name}")

        print(f"\nManifest: {manifest_path}")

        # Print summary
        print("\n" + "=" * 60)
        print("Template Summary:")
        print("=" * 60)
        print("  teams:     48 rows (one per qualified team)")
        print("  groups:    48 rows (12 groups × 4 teams)")
        print("  fixtures:  104 rows (all tournament matches)")
        print("  venues:    16 rows (all tournament venues)")
        print("  players:   1248 rows (48 teams × 26 players)")
        print("  squads:    48 rows (squad summaries per team)")

        print("\n" + "=" * 60)
        print("Instructions:")
        print("=" * 60)
        print("1. Open the generated CSV templates in a spreadsheet editor")
        print("2. Fill in the data from official FIFA sources")
        print("3. Save the completed files (keep the same column structure)")
        print("4. Run: python scripts/apply_official_import.py")
        print("5. Run: python scripts/evaluate_official_final_readiness.py")

        print("\n" + "=" * 60)
        print("Done!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()