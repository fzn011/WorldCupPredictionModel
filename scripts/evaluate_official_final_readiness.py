#!/usr/bin/env python
"""Evaluate final readiness for official_final mode.

This script runs all final readiness checks and reports whether the system
is ready for official_final mode. It checks data completeness, placeholder
values, sample rows, and cross-dataset consistency.

Usage:
    python scripts/evaluate_official_final_readiness.py [--save]

Options:
    --save    Save the full report to disk
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.official.final_readiness import evaluate_official_final_readiness, save_final_readiness_report
from src.utils.constants import OFFICIAL_READINESS_READY, OFFICIAL_READINESS_WARNING, OFFICIAL_READINESS_BLOCKED


def main():
    """Evaluate official final readiness."""
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate official final readiness")
    parser.add_argument("--save", action="store_true", help="Save the full report to disk")
    args = parser.parse_args()

    print("=" * 60)
    print("FIFA World Cup 2026 - Official Final Readiness Evaluation")
    print("=" * 60)

    try:
        # Evaluate readiness
        print("\nRunning readiness checks...\n")
        report = evaluate_official_final_readiness()

        status = report["status"]
        summary = report["summary"]

        # Print summary
        print("-" * 60)
        print("SUMMARY")
        print("-" * 60)
        print(f"  Total checks:     {summary['total_checks']}")
        print(f"  Passed:           {summary['passed_checks']}")
        print(f"  Failed:           {summary['failed_checks']}")
        print(f"  Blockers:         {summary['blocker_count']}")
        print(f"  Warnings:         {summary['warning_count']}")
        print(f"  Teams:            {summary['teams_count']}/48")
        print(f"  Players:          {summary['players_count']}/1248")
        print(f"  Teams w/ 26:      {summary['teams_with_26_players']}/48")

        # Print status
        print("\n" + "-" * 60)
        print("STATUS")
        print("-" * 60)

        if status == OFFICIAL_READINESS_READY:
            print("  ✓ READY - System is ready for official_final mode!")
        elif status == OFFICIAL_READINESS_WARNING:
            print("  ⚠ WARNING - System has warnings but may be usable")
        elif status == OFFICIAL_READINESS_BLOCKED:
            print("  ✗ BLOCKED - System is NOT ready for official_final mode")

        # Print checklist
        print("\n" + "-" * 60)
        print("CHECKLIST")
        print("-" * 60)

        for check in report["checklist"]:
            icon = "✓" if check["passed"] else "✗"
            print(f"  {icon} {check['id']}: {check['passed']}")

        # Print blockers
        if report["blockers"]:
            print("\n" + "-" * 60)
            print("BLOCKERS")
            print("-" * 60)
            for blocker in report["blockers"]:
                print(f"  ✗ {blocker.get('id', 'unknown')}")
                details = blocker.get("details", {})
                if isinstance(details, dict):
                    for key, value in details.items():
                        print(f"      {key}: {value}")

        # Print warnings
        if report["warnings"]:
            print("\n" + "-" * 60)
            print("WARNINGS")
            print("-" * 60)
            for warning in report["warnings"]:
                print(f"  ⚠ {warning.get('id', 'unknown')}")

        # Save report if requested
        if args.save:
            print("\n" + "-" * 60)
            report_path = save_final_readiness_report(report)
            print(f"Report saved to: {report_path}")

        # Print final verdict
        print("\n" + "=" * 60)
        if report["is_official_final_ready"]:
            print("VERDICT: Official final mode is ALLOWED")
        else:
            print("VERDICT: Official final mode is BLOCKED")
            print("\nResolve all blockers before enabling official_final mode.")
        print("=" * 60)

        # Return appropriate exit code
        if not report["is_official_final_ready"]:
            sys.exit(1)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()