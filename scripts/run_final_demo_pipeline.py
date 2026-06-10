#!/usr/bin/env python
"""One-command demo pipeline for portfolio presentation (Step 19)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.official.final_readiness import evaluate_official_final_readiness  # noqa: E402
from src.official.promotion import load_official_final_mode  # noqa: E402
from src.portfolio.packaging import prepare_step19_portfolio_pack  # noqa: E402
from src.reports.final_project_report import (  # noqa: E402
    create_final_project_summary,
    create_final_validation_report,
    save_final_project_summary,
)


def _run(cmd: list[str]) -> int:
    print("$", " ".join(cmd))
    return subprocess.call(cmd, cwd=str(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run final demo pipeline")
    parser.add_argument("--simulations", type=int, default=10, help="Monte Carlo simulation count")
    parser.add_argument("--seed", type=int, default=42, help="Monte Carlo random seed")
    parser.add_argument(
        "--use-manual-priors",
        action="store_true",
        help="Generate awards with optional manual star-player prior overrides",
    )
    parser.add_argument(
        "--manual-prior-file",
        default=None,
        help="Manual prior CSV path for awards generation",
    )
    args = parser.parse_args()

    mode = load_official_final_mode()
    readiness = evaluate_official_final_readiness()
    print("=== Official Final Status ===")
    print(f"official_final_enabled: {mode.get('official_final_enabled')}")
    print(f"final_ready: {readiness.get('is_official_final_ready')}")

    steps = [
        [sys.executable, "scripts/evaluate_official_final_readiness.py"],
        [
            sys.executable,
            "scripts/run_monte_carlo.py",
            "--simulations",
            str(args.simulations),
            "--seed",
            str(args.seed),
        ],
        [sys.executable, "scripts/enrich_player_priors.py"],
        [sys.executable, "scripts/enrich_player_priors.py", "--update-award-candidates"],
    ]
    awards_cmd = [sys.executable, "scripts/generate_world_cup_awards.py", "--use-enriched"]
    if args.use_manual_priors:
        awards_cmd.append("--use-manual-priors")
        if args.manual_prior_file:
            awards_cmd.extend(["--manual-prior-file", args.manual_prior_file])
    steps.append(awards_cmd)
    for cmd in steps:
        script = cmd[1] if len(cmd) > 1 else ""
        if script.endswith("evaluate_official_final_readiness.py"):
            path = ROOT / script
            if not path.is_file():
                print(f"Skipping missing script: {script}")
                continue
        rc = _run(cmd)
        if rc != 0 and "evaluate_official_final_readiness" not in script:
            print(f"Warning: command failed with exit {rc}: {script}")

    # Optional monte carlo report if script exists
    mc_report = ROOT / "scripts/prepare_monte_carlo_report.py"
    if mc_report.is_file():
        _run([sys.executable, str(mc_report)])

    summary = create_final_project_summary()
    summary_path = save_final_project_summary(summary)
    validation_df = create_final_validation_report()
    portfolio = prepare_step19_portfolio_pack()

    print("\n=== Final Demo Pipeline Summary ===")
    print(f"top_champion: {summary.get('top_champion')}")
    print(f"top_golden_ball_player: {summary.get('top_golden_ball_player')}")
    print(f"top_golden_boot_player: {summary.get('top_golden_boot_player')}")
    print(f"candidate_source: {summary.get('candidate_source')}")
    print(f"use_manual_priors: {summary.get('use_manual_priors')}")
    print(f"manual_priors_applied: {summary.get('manual_priors_applied')}")
    print(f"summary_path: {summary_path}")
    print(f"portfolio_readme: {portfolio.get('portfolio_readme')}")
    print(f"demo_script: {portfolio.get('demo_script')}")
    print(f"validation_passed: {bool(validation_df['passed'].all()) if not validation_df.empty else False}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
