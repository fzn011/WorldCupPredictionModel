"""Placeholder knockout-stage simulation."""

from __future__ import annotations


def simulate_knockout_match(team_a: str, team_b: str) -> str:
    """Return a dummy winner for a single knockout match.

    Args:
        team_a: Name of team A.
        team_b: Name of team B.

    Returns:
        The dummy winner (currently always ``team_a``).
    """
    # TODO (Step 7): sample winner from match-result probabilities, with
    # extra-time and penalty-shootout logic for draws.
    return team_a
