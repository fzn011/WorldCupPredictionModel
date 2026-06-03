"""Streamlit page: Match Predictor."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Ensure project root is on sys.path so `src` imports work when Streamlit
# runs this file directly.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.models.model_features import load_feature_dataset  # noqa: E402
from src.models.predict_match import (  # noqa: E402
    predict_existing_match_by_id,
    predict_match_result,
)


@st.cache_data(show_spinner=False)
def _load_features() -> pd.DataFrame:
    return load_feature_dataset()


st.title("Match Predictor")
st.caption(
    "Predict existing engineered matches using the best available trained model (improved preferred, baseline fallback)."
)

feature_df = _load_features()
available_teams = sorted(pd.unique(feature_df[["team_a", "team_b"]].values.ravel("K")))

mode = st.radio(
    "Prediction mode",
    ["Existing Match Prediction Demo", "Future Match Placeholder"],
    horizontal=True,
)

if mode == "Existing Match Prediction Demo":
    if feature_df.empty or "match_id" not in feature_df.columns:
        st.warning("No feature dataset is available yet. Run `python main.py` first.")
    else:
        demo_df = feature_df.copy()
        if "date" in demo_df.columns:
            demo_df["date"] = pd.to_datetime(demo_df["date"], errors="coerce")
            demo_df = demo_df.sort_values("date")

        options: dict[str, str] = {}
        for _, row in demo_df.head(1000).iterrows():
            date_text = row["date"].date().isoformat() if pd.notna(row.get("date")) else "unknown-date"
            label = f"{date_text} | {row['team_a']} vs {row['team_b']} | {row.get('result_label', 'unknown')}"
            options[label] = str(row["match_id"])

        selected_label = st.selectbox("Choose a match", list(options.keys()))

        if st.button("Predict this match"):
            try:
                prediction = predict_existing_match_by_id(options[selected_label])
                st.subheader("Prediction")
                st.write(f"**Model type used:** {prediction.get('model_type', 'baseline')}")
                st.write(f"**Team A loss probability:** {prediction['probabilities']['team_a_loss']:.3f}")
                st.write(f"**Draw probability:** {prediction['probabilities']['draw']:.3f}")
                st.write(f"**Team A win probability:** {prediction['probabilities']['team_a_win']:.3f}")
                st.write(f"**Predicted label:** {prediction['predicted_label']}")
                st.write(f"**Actual label:** {prediction.get('actual_label')}")
            except Exception as exc:  # pragma: no cover - UI safety
                st.error(str(exc))

else:
    col1, col2 = st.columns(2)
    with col1:
        team_a = st.selectbox("Team A", available_teams, index=0 if available_teams else None)
    with col2:
        team_b = st.selectbox("Team B", available_teams, index=1 if len(available_teams) > 1 else 0)

    if st.button("Preview future match"):
        if team_a == team_b:
            st.warning("Please pick two different teams.")
        else:
            placeholder = predict_match_result(team_a, team_b)
            st.info(placeholder["message"])
