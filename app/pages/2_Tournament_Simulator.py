"""Streamlit page: Tournament Simulator (placeholder)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.simulation.simulate_tournament import simulate_tournament  # noqa: E402

st.title("Tournament Simulator")
st.caption("Placeholder champion probabilities — real Monte Carlo arrives later.")

num_simulations = st.number_input(
    "Number of simulations",
    min_value=100,
    max_value=100_000,
    value=10_000,
    step=100,
)

if st.button("Run Simulation"):
    probs = simulate_tournament(num_simulations=int(num_simulations))
    df = (
        pd.DataFrame(
            [{"team": t, "champion_probability": p} for t, p in probs.items()]
        )
        .sort_values("champion_probability", ascending=False)
        .reset_index(drop=True)
    )
    st.subheader("Champion Probabilities")
    st.dataframe(df, use_container_width=True)
