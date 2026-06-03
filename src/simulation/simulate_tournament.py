"""Placeholder full-tournament Monte Carlo simulator."""

from __future__ import annotations


def simulate_tournament(num_simulations: int = 10000) -> dict:
    """Return dummy champion probabilities.

    Args:
        num_simulations: Number of Monte Carlo runs the real simulator
            will eventually use.

    Returns:
        Dictionary mapping team name to champion probability.
    """
    print(f"[simulate_tournament] Requested {num_simulations} simulations.")
    # TODO (Step 7): run real Monte Carlo simulation using group draws,
    # knockout bracket structure, and trained match-result model.
    return {
        "France": 0.18,
        "Argentina": 0.15,
        "Brazil": 0.13,
        "England": 0.10,
        "Spain": 0.09,
        "Germany": 0.07,
        "Portugal": 0.06,
        "Netherlands": 0.05,
    }
