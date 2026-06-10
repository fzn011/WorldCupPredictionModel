"""Compatibility wrapper for Golden Ball inside the broader awards predictor."""

from __future__ import annotations

from typing import Any

from src.awards.prepare_awards import prepare_step17_world_cup_awards


def prepare_step17_golden_ball_predictions() -> dict[str, Any]:
    """Compatibility call that now delegates to the broader awards predictor."""
    return prepare_step17_world_cup_awards()


if __name__ == "__main__":
    print(prepare_step17_golden_ball_predictions())
