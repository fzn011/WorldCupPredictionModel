"""Tests for Monte Carlo readiness checks."""

from __future__ import annotations

from pathlib import Path

from src.simulation.monte_carlo_readiness import evaluate_monte_carlo_readiness, require_monte_carlo_ready
import src.utils.constants as C


def test_evaluate_monte_carlo_readiness_passes_with_project_artifacts() -> None:
    status = evaluate_monte_carlo_readiness(project_root=C.PROJECT_ROOT)
    assert "ready" in status
    assert "blockers" in status
    if status["ready"]:
        require_monte_carlo_ready(project_root=C.PROJECT_ROOT)
    else:
        assert status["blockers"]


def test_require_monte_carlo_ready_raises_when_models_missing(tmp_path: Path) -> None:
    empty_root = tmp_path / "empty_project"
    empty_root.mkdir()
    (empty_root / "data" / "processed").mkdir(parents=True)
    status = evaluate_monte_carlo_readiness(project_root=empty_root)
    assert status["ready"] is False
    assert status["blockers"]
