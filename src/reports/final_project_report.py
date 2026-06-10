"""Final project status and validation reporting (Step 19)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C
from src.official.final_readiness import evaluate_official_final_readiness
from src.official.promotion import load_official_final_mode

PROJECT_ROOT = C.PROJECT_ROOT
PROCESSED_DATA_DIR = PROJECT_ROOT / C.PROCESSED_DATA_DIR
REPORTS_DIR = PROJECT_ROOT / "reports"
PORTFOLIO_DIR = PROJECT_ROOT / C.PORTFOLIO_DIR


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _fixtures_count_from_readiness(readiness: dict[str, Any]) -> int | None:
    summary = readiness.get("summary", {})
    if summary.get("fixtures_count"):
        return int(summary["fixtures_count"])
    fixtures_path = PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR / C.OFFICIAL_FIXTURES_FILE
    if fixtures_path.is_file():
        return len(pd.read_csv(fixtures_path))
    for check in readiness.get("checklist", []):
        if check.get("id") == "fixtures_complete":
            details = check.get("details", {})
            if "fixture_count" in details:
                return int(details["fixture_count"])
    return None


def collect_final_project_status() -> dict[str, Any]:
    """Collect end-to-end project status for portfolio/demo."""
    mode = load_official_final_mode()
    readiness = evaluate_official_final_readiness()
    mc_summary = _read_json(PROCESSED_DATA_DIR / C.MONTE_CARLO_SUMMARY_FILE)
    awards_summary = _read_json(PROCESSED_DATA_DIR / C.WORLD_CUP_AWARDS_SUMMARY_FILE)
    prior_quality_path = PROCESSED_DATA_DIR / C.PLAYER_PRIOR_QUALITY_REPORT_FILE
    rs = readiness.get("summary", {})

    return {
        "official_final_enabled": bool(mode.get("official_final_enabled", False)),
        "final_ready": bool(readiness.get("is_official_final_ready", False)),
        "fixtures_count": _fixtures_count_from_readiness(readiness),
        "players_count": rs.get("players_count"),
        "monte_carlo_available": (PROCESSED_DATA_DIR / C.MONTE_CARLO_SUMMARY_FILE).is_file(),
        "awards_available": (PROCESSED_DATA_DIR / C.WORLD_CUP_AWARDS_SUMMARY_FILE).is_file(),
        "enriched_candidates_available": (
            PROCESSED_DATA_DIR / C.ENRICHED_OFFICIAL_AWARD_CANDIDATES_FILE
        ).is_file(),
        "prior_quality_available": prior_quality_path.is_file(),
        "monte_carlo_summary": mc_summary,
        "awards_summary": awards_summary,
        "test_command": "python -m pytest -q",
        "key_outputs": {
            "monte_carlo_summary": str(PROCESSED_DATA_DIR / C.MONTE_CARLO_SUMMARY_FILE),
            "awards_summary": str(PROCESSED_DATA_DIR / C.WORLD_CUP_AWARDS_SUMMARY_FILE),
            "awards_report": str(REPORTS_DIR / C.WORLD_CUP_AWARDS_REPORT_FILE),
            "final_summary": str(PROCESSED_DATA_DIR / C.FINAL_PROJECT_SUMMARY_FILE),
            "portfolio_readme": str(PORTFOLIO_DIR / "PORTFOLIO_README.md"),
        },
        "readiness_status": readiness.get("status"),
    }


def create_final_project_summary() -> dict[str, Any]:
    """Compact summary for demo/portfolio."""
    status = collect_final_project_status()
    mc = status.get("monte_carlo_summary", {})
    awards = status.get("awards_summary", {})
    top_champion = ""
    if isinstance(mc.get("top_champions"), list) and mc["top_champions"]:
        top_champion = mc["top_champions"][0].get("team", "")
    elif mc.get("top_champion_team"):
        top_champion = mc["top_champion_team"]

    return {
        "project_name": C.PROJECT_NAME,
        "status": "ok" if status.get("official_final_enabled") else "blocked",
        "official_final_enabled": status.get("official_final_enabled"),
        "fixtures_count": status.get("fixtures_count"),
        "players_count": status.get("players_count"),
        "monte_carlo_available": status.get("monte_carlo_available"),
        "awards_available": status.get("awards_available"),
        "top_champion": top_champion,
        "top_golden_ball_player": awards.get("top_golden_ball_player"),
        "top_golden_boot_player": awards.get("top_golden_boot_player"),
        "candidate_source": awards.get("candidate_source"),
        "notes": (
            "Probabilistic analytics estimates only — not official FIFA predictions. "
            "Player priors are heuristic unless manually edited."
        ),
    }


def save_final_project_summary(summary: dict[str, Any], output_path: str | None = None) -> str:
    path = Path(output_path) if output_path else PROCESSED_DATA_DIR / C.FINAL_PROJECT_SUMMARY_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return str(path)


def create_final_validation_report() -> pd.DataFrame:
    """Validate portfolio-ready project artifacts."""
    rows: list[dict[str, Any]] = []
    mode = load_official_final_mode()
    readiness = evaluate_official_final_readiness()
    summary = readiness.get("summary", {})

    def row(check: str, expected: Any, actual: Any, passed: bool) -> dict[str, Any]:
        return {"check": check, "expected": expected, "actual": actual, "passed": passed}

    rows.append(row("official_final_enabled", True, mode.get("official_final_enabled"), bool(mode.get("official_final_enabled"))))
    rows.append(row("official_fixtures", 104, _fixtures_count_from_readiness(readiness), _fixtures_count_from_readiness(readiness) == 104))
    rows.append(row("official_players", 1248, summary.get("players_count"), summary.get("players_count") == 1248))
    rows.append(row("monte_carlo_outputs", "present", (PROCESSED_DATA_DIR / C.MONTE_CARLO_SUMMARY_FILE).is_file(), (PROCESSED_DATA_DIR / C.MONTE_CARLO_SUMMARY_FILE).is_file()))
    rows.append(row("awards_outputs", "present", (PROCESSED_DATA_DIR / C.WORLD_CUP_AWARDS_SUMMARY_FILE).is_file(), (PROCESSED_DATA_DIR / C.WORLD_CUP_AWARDS_SUMMARY_FILE).is_file()))
    rows.append(row("streamlit_app", "present", (PROJECT_ROOT / "app" / "streamlit_app.py").is_file(), (PROJECT_ROOT / "app" / "streamlit_app.py").is_file()))
    rows.append(row("awards_page", "present", (PROJECT_ROOT / "app" / "pages" / "17_World_Cup_Awards.py").is_file(), (PROJECT_ROOT / "app" / "pages" / "17_World_Cup_Awards.py").is_file()))
    rows.append(row("readme", "present", (PROJECT_ROOT / "README.md").is_file(), (PROJECT_ROOT / "README.md").is_file()))
    rows.append(row("enrich_script", "present", (PROJECT_ROOT / "scripts" / "enrich_player_priors.py").is_file(), (PROJECT_ROOT / "scripts" / "enrich_player_priors.py").is_file()))
    rows.append(row("demo_pipeline_script", "present", (PROJECT_ROOT / "scripts" / "run_final_demo_pipeline.py").is_file(), (PROJECT_ROOT / "scripts" / "run_final_demo_pipeline.py").is_file()))
    rows.append(row("portfolio_readme", "present", (PORTFOLIO_DIR / "PORTFOLIO_README.md").is_file(), (PORTFOLIO_DIR / "PORTFOLIO_README.md").is_file()))

    df = pd.DataFrame(rows)
    out_path = PROCESSED_DATA_DIR / C.FINAL_PROJECT_VALIDATION_REPORT_FILE
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    return df
