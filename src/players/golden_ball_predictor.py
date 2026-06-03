"""Placeholder Golden Ball predictor."""

from __future__ import annotations


def predict_golden_ball_candidates() -> list:
    """Return a dummy list of Golden Ball candidates.

    Returns:
        List of dictionaries with ``player``, ``country``, ``probability``.
    """
    # TODO (Step 8): rank players using real impact-score model conditioned
    # on team championship probability from the tournament simulator.
    return [
        {"player": "Kylian Mbappe",   "country": "France",  "probability": 0.15},
        {"player": "Jude Bellingham", "country": "England", "probability": 0.11},
        {"player": "Vinicius Junior", "country": "Brazil",  "probability": 0.09},
        {"player": "Lamine Yamal",    "country": "Spain",   "probability": 0.07},
        {"player": "Erling Haaland",  "country": "Norway",  "probability": 0.05},
    ]
