"""Placeholder player impact scoring."""

from __future__ import annotations


def calculate_player_impact_score(player_stats: dict) -> float:
    """Compute a simple player-impact score.

    Current formula::

        score = goals * 5 + assists * 3

    Args:
        player_stats: Dictionary that may contain ``goals`` and ``assists``.

    Returns:
        A non-negative impact score.
    """
    goals = player_stats.get("goals", 0) or 0
    assists = player_stats.get("assists", 0) or 0
    # TODO (Step 8): position-specific scoring (GK saves, DEF tackles,
    # MID key passes, FWD xG/xA), minutes-played normalization, and
    # tournament-stage weighting.
    return float(goals) * 5.0 + float(assists) * 3.0
