"""Streamlit page: Golden Ball Predictor (placeholder)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.players.golden_ball_predictor import predict_golden_ball_candidates  # noqa: E402

st.title("Golden Ball Predictor")
st.caption("Placeholder Golden Ball candidates.")

candidates = predict_golden_ball_candidates()
df = (
    pd.DataFrame(candidates)
    .sort_values("probability", ascending=False)
    .reset_index(drop=True)
)
st.dataframe(df, use_container_width=True)
