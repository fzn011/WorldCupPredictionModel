#!/usr/bin/env python
"""Promote or demote official_final mode (Step 17D)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.official.promotion import (
    can_promote_to_official_final,
    demote_from_official_final,
    load_official_final_mode,
    promote_to_official_final,
)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Promote/demote official_final mode")
    parser.add_argument("--confirm", action="store_true", help="Confirm promotion to official_final")
    parser.add_argument("--demote", action="store_true", help="Demote from official_final")
    parser.add_argument("--reason", default="", help="Reason for demotion")
    args = parser.parse_args()

    print("=" * 60)
    print("FIFA World Cup 2026 - Official Final Promotion (Step 17D)")
    print("=" * 60)

    current = load_official_final_mode()
    print(f"\nCurrent official_final_enabled: {current.get('official_final_enabled', False)}")

    if args.demote:
        result = demote_from_official_final(reason=args.reason)
        print(f"\nResult: {result.get('status')}")
        print(f"official_final_enabled: {result.get('official_final_enabled')}")
        if result.get("reason"):
            print(f"Reason: {result.get('reason')}")
        return

    final_ready, summary = can_promote_to_official_final()
    print(f"\nFinal ready: {final_ready}")
    print(f"Readiness status: {summary.get('status')}")
    print(f"Blockers: {summary.get('blocker_count', 0)}")
    print(f"Warnings: {summary.get('warning_count', 0)}")

    if summary.get("blockers"):
        print("\nBlocking issues:")
        for blocker in summary["blockers"]:
            print(f"  - {blocker}")

    if args.confirm:
        result = promote_to_official_final(confirmed=True)
    else:
        result = promote_to_official_final(confirmed=False)
        print("\nPromotion requires --confirm after reviewing readiness above.")

    print(f"\nPromotion result status: {result.get('status')}")
    print(f"official_final_enabled:  {result.get('official_final_enabled', False)}")
    if result.get("message"):
        print(f"Message: {result.get('message')}")

    print("\n" + "=" * 60)

    if args.confirm and result.get("status") == "blocked":
        sys.exit(1)
    if args.confirm and result.get("status") != "promoted":
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\n✗ Error: {exc}")
        sys.exit(1)
