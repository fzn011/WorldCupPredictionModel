#!/usr/bin/env python
"""Apply staged official data through the safe import workflow (Step 17E)."""

from __future__ import annotations

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import src.utils.constants as C
from src.official.apply_imports import apply_official_import_file, append_import_audit
from src.official.final_readiness import evaluate_official_final_readiness
from src.official.import_diff import preview_official_import, save_import_diff_report
from src.official.prepare_squads import prepare_step17b_official_squads_and_priors
from src.official.staging_validation import STAGED_FILES

ALLOWED = set(C.OFFICIAL_SOURCE_APPLY_ORDER) | {"all"}


def _staged_path(target: str) -> Path:
    return C.PROJECT_ROOT / C.OFFICIAL_SOURCE_STAGING_DIR / STAGED_FILES[target]


def _apply_one(target: str, preview: bool) -> dict:
    path = _staged_path(target)
    if not path.is_file():
        return {"target": target, "success": False, "error": f"Staged file missing: {path}"}

    if preview:
        diff_df = preview_official_import(str(path), target)
        diff_path = save_import_diff_report(diff_df)
        return {"target": target, "success": True, "preview": True, "diff_report": str(diff_path)}

    result = apply_official_import_file(str(path), template_type=target, create_backup=True, re_prepare=True)
    if result.get("success"):
        append_import_audit(
            target,
            str(path),
            result.get("rows", 0),
            True,
            "applied_from_staging",
            result.get("backup_path", ""),
        )
    return {"target": target, **result}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Apply staged official data")
    parser.add_argument("--target", "-t", required=True, choices=sorted(ALLOWED))
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preview", action="store_true")
    group.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    targets = list(C.OFFICIAL_SOURCE_APPLY_ORDER) if args.target == "all" else [args.target]

    print("=" * 60)
    print("Step 17E: Apply Staged Official Data")
    print("=" * 60)

    results = []
    for target in targets:
        res = _apply_one(target, preview=args.preview)
        results.append(res)
        print(f"\n{target}: success={res.get('success')}")
        if res.get("error"):
            print(f"  {res['error']}")
        if res.get("diff_report"):
            print(f"  diff: {res['diff_report']}")

    if args.apply and any(t in {"players", "player_priors"} for t in targets):
        print("\nRe-running squad merge (Step 17B)...")
        prepare_step17b_official_squads_and_priors()

    if args.apply:
        readiness = evaluate_official_final_readiness()
        print(f"\nofficial_final ready: {readiness.get('is_official_final_ready')}")
        print(f"Readiness status:     {readiness.get('status')}")

    print("=" * 60)


if __name__ == "__main__":
    main()
