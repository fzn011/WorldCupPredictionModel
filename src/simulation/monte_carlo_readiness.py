"""Pre-flight checks before running Monte Carlo tournament simulations."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import src.utils.constants as C

BASELINE_MODEL_DIR = getattr(C, "BASELINE_MODEL_DIR", Path("models") / "baseline")
BEST_BASELINE_MODEL_FILE = getattr(C, "BEST_BASELINE_MODEL_FILE", "best_baseline_model.joblib")
IMPROVED_MODEL_DIR = getattr(C, "IMPROVED_MODEL_DIR", Path("models") / "improved")
BEST_IMPROVED_MODEL_FILE = getattr(C, "BEST_IMPROVED_MODEL_FILE", "best_improved_model.joblib")
RANKING_ENHANCED_MODEL_DIR = getattr(C, "RANKING_ENHANCED_MODEL_DIR", Path("models") / "ranking_enhanced")
BEST_RANKING_ENHANCED_MODEL_FILE = getattr(
    C, "BEST_RANKING_ENHANCED_MODEL_FILE", "best_ranking_enhanced_model.joblib"
)
PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")
TOURNAMENT_FIXTURES_FILE = getattr(C, "TOURNAMENT_FIXTURES_FILE", "tournament_fixtures.csv")
TOURNAMENT_GROUPS_FILE = getattr(C, "TOURNAMENT_GROUPS_FILE", "tournament_groups.csv")
PROJECT_ROOT = getattr(C, "PROJECT_ROOT", Path(__file__).resolve().parents[2])
SAMPLE_DATA_DIR = getattr(C, "SAMPLE_DATA_DIR", Path("data") / "sample")


def _model_paths(root: Path) -> list[Path]:
    return [
        root / RANKING_ENHANCED_MODEL_DIR / BEST_RANKING_ENHANCED_MODEL_FILE,
        root / IMPROVED_MODEL_DIR / BEST_IMPROVED_MODEL_FILE,
        root / BASELINE_MODEL_DIR / BEST_BASELINE_MODEL_FILE,
    ]


def evaluate_monte_carlo_readiness(project_root: Path | str | None = None) -> dict[str, Any]:
    """Return readiness status and human-readable blockers for Monte Carlo runs."""
    root = Path(project_root) if project_root is not None else Path(PROJECT_ROOT)
    blockers: list[str] = []
    warnings: list[str] = []

    model_paths = _model_paths(root)
    available_models = [str(path.relative_to(root)) for path in model_paths if path.is_file()]
    if not available_models:
        blockers.append(
            "No trained match model found under `models/`. Run `python main.py` (or the training scripts) first."
        )
    else:
        warnings.append(f"Using available model artifact(s): {', '.join(available_models)}")

    fixture_candidates = [
        root / PROCESSED_DATA_DIR / TOURNAMENT_FIXTURES_FILE,
        root / SAMPLE_DATA_DIR / "sample_tournament_schedule.csv",
        root / PROCESSED_DATA_DIR / TOURNAMENT_GROUPS_FILE,
    ]
    if not any(path.is_file() for path in fixture_candidates):
        blockers.append(
            "Tournament fixtures/groups are missing. Run `python scripts/prepare_tournament_setup.py` or `python main.py`."
        )
    else:
        try:
            from src.tournament.fixtures import load_tournament_fixtures

            fixtures_df = load_tournament_fixtures()
            if fixtures_df.empty:
                blockers.append("Tournament fixtures loaded but contain zero rows.")
            elif len(fixtures_df.loc[fixtures_df["stage"] == "group_stage"]) == 0:
                blockers.append("Tournament fixtures have no group-stage matches.")
        except Exception as exc:
            blockers.append(f"Could not load tournament fixtures: {exc}")

    return {
        "ready": not blockers,
        "blockers": blockers,
        "warnings": warnings,
        "available_models": available_models,
    }


def require_monte_carlo_ready(project_root: Path | str | None = None) -> dict[str, Any]:
    """Raise ValueError when Monte Carlo prerequisites are not satisfied."""
    status = evaluate_monte_carlo_readiness(project_root=project_root)
    if not status["ready"]:
        message = "; ".join(status["blockers"])
        raise ValueError(message)
    return status


MonteCarloProgressCallback = Callable[[int, int, dict[str, Any]], None]
