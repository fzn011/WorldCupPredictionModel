"""Streamlit page: Match Predictor."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Ensure project root is on sys.path so `src` imports work when Streamlit
# runs this file directly.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.features.future_match_features import get_available_teams  # noqa: E402
from src.models.model_features import load_feature_dataset  # noqa: E402
from src.models.prediction_utils import (  # noqa: E402
    append_prediction_history,
    extract_prediction_explanation_features,
    format_probability,
    load_prediction_history,
    save_latest_prediction_report,
)
import src.models.predict_match as predict_match_module  # noqa: E402
import src.utils.constants as C  # noqa: E402

DEFAULT_FUTURE_MATCH_DATE = getattr(C, "DEFAULT_FUTURE_MATCH_DATE", "2026-06-11")
DEFAULT_FUTURE_TOURNAMENT = getattr(C, "DEFAULT_FUTURE_TOURNAMENT", "FIFA World Cup")
DEFAULT_FUTURE_CITY = getattr(C, "DEFAULT_FUTURE_CITY", "Unknown")
DEFAULT_FUTURE_COUNTRY = getattr(C, "DEFAULT_FUTURE_COUNTRY", "Unknown")
DEFAULT_FUTURE_NEUTRAL = getattr(C, "DEFAULT_FUTURE_NEUTRAL", 1)
LATEST_PREDICTION_REPORT_FILE = getattr(C, "LATEST_PREDICTION_REPORT_FILE", "latest_prediction_report.csv")

predict_existing_match_by_id = getattr(predict_match_module, "predict_existing_match_by_id", None)
predict_future_match = getattr(predict_match_module, "predict_future_match", None)

if predict_existing_match_by_id is None or predict_future_match is None:
    local_predictor_path = ROOT / "src" / "models" / "predict_match.py"
    if local_predictor_path.is_file():
        spec = importlib.util.spec_from_file_location("local_predict_match", local_predictor_path)
        if spec and spec.loader:
            local_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(local_module)
            if predict_existing_match_by_id is None:
                predict_existing_match_by_id = getattr(local_module, "predict_existing_match_by_id", None)
            if predict_future_match is None:
                predict_future_match = getattr(local_module, "predict_future_match", None)


@st.cache_data(show_spinner=False)
def _load_features() -> pd.DataFrame:
    return load_feature_dataset()


@st.cache_data(show_spinner=False)
def _load_available_teams() -> list[str]:
    return get_available_teams()


def _render_probability_chart(probabilities: dict) -> None:
    chart_df = pd.DataFrame(
        {
            "result": ["team_a_loss", "draw", "team_a_win"],
            "probability": [
                float(probabilities.get("team_a_loss", 0.0)),
                float(probabilities.get("draw", 0.0)),
                float(probabilities.get("team_a_win", 0.0)),
            ],
        }
    )
    st.bar_chart(chart_df.set_index("result"))


st.title("Match Predictor")
st.caption(
    "Predict arbitrary future matches from generated pre-match features (ranking-enhanced preferred, then improved, then baseline)."
)

available_teams = _load_available_teams()
feature_df = _load_features()

future_tab, existing_tab = st.tabs(["Future Match Prediction", "Existing Match Prediction Demo"])

with future_tab:
    if predict_future_match is None:
        st.error(
            "Predictor import is out of sync in the current Streamlit process. "
            "Please restart Streamlit to reload `src.models.predict_match`."
        )
        st.stop()

    if not available_teams:
        st.warning("No teams available yet. Run `python main.py` first.")
        st.stop()

    col1, col2 = st.columns(2)
    with col1:
        team_a = st.selectbox("Team A", available_teams, index=0)
    with col2:
        team_b = st.selectbox("Team B", available_teams, index=1 if len(available_teams) > 1 else 0)

    col3, col4 = st.columns(2)
    with col3:
        match_date_value = st.date_input("Match date", pd.to_datetime(DEFAULT_FUTURE_MATCH_DATE).date())
    with col4:
        tournament = st.text_input("Tournament", value=DEFAULT_FUTURE_TOURNAMENT)

    col5, col6 = st.columns(2)
    with col5:
        city = st.text_input("City", value=DEFAULT_FUTURE_CITY)
    with col6:
        country = st.text_input("Country", value=DEFAULT_FUTURE_COUNTRY)

    neutral = st.checkbox("Neutral venue", value=bool(DEFAULT_FUTURE_NEUTRAL))

    if st.button("Predict future match"):
        if team_a == team_b:
            st.error("Team A and Team B must be different teams.")
            st.stop()

        try:
            prediction = predict_future_match(
                team_a=team_a,
                team_b=team_b,
                match_date=str(match_date_value),
                tournament=tournament,
                city=city,
                country=country,
                neutral=int(neutral),
            )
        except FileNotFoundError:
            st.error("Model artifacts are missing. Run `python scripts/train_ranking_enhanced_model.py` first.")
            st.stop()
        except Exception as exc:  # pragma: no cover - UI safety
            st.error(str(exc))
            st.stop()

        probabilities = prediction["probabilities"]
        confidence = prediction.get("confidence", {})

        history_path = append_prediction_history(prediction)
        latest_report_path = save_latest_prediction_report(prediction)

        st.subheader("Prediction")
        st.write(f"**Predicted label:** {prediction.get('predicted_label')} ")
        st.write(f"**Model type used:** {prediction.get('model_type')} ")
        st.write(
            f"**Confidence:** {confidence.get('confidence_label', 'Unknown')} "
            f"({format_probability(confidence.get('max_probability', 0.0))})"
        )

        m1, m2, m3 = st.columns(3)
        m1.metric("Team A loss", format_probability(probabilities["team_a_loss"]))
        m2.metric("Draw", format_probability(probabilities["draw"]))
        m3.metric("Team A win", format_probability(probabilities["team_a_win"]))

        st.markdown("**Probability chart**")
        _render_probability_chart(probabilities)

        notes = prediction.get("notes", [])
        if notes:
            st.markdown("**Notes**")
            for note in notes:
                st.write(f"- {note}")

        st.markdown("**Feature preview / explanation**")
        explanation_df = extract_prediction_explanation_features(prediction.get("feature_row", pd.DataFrame()))
        st.dataframe(explanation_df, use_container_width=True)

        report_file = Path(latest_report_path)
        if report_file.is_file():
            st.download_button(
                label="Download latest prediction report",
                data=report_file.read_bytes(),
                file_name=LATEST_PREDICTION_REPORT_FILE,
                mime="text/csv",
            )

        history_df = load_prediction_history(history_path)
        if history_df.empty:
            st.info("No prediction history yet.")
        else:
            show_columns = [
                "prediction_timestamp",
                "team_a",
                "team_b",
                "match_date",
                "tournament",
                "model_type",
                "predicted_label",
                "team_a_loss_probability",
                "draw_probability",
                "team_a_win_probability",
            ]
            show_columns = [col for col in show_columns if col in history_df.columns]
            st.markdown("**Prediction history (recent)**")
            st.dataframe(history_df.tail(20)[show_columns].iloc[::-1], use_container_width=True)

with existing_tab:
    if predict_existing_match_by_id is None:
        st.error(
            "Predictor import is out of sync in the current Streamlit process. "
            "Please restart Streamlit to reload `src.models.predict_match`."
        )
        st.stop()

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

        if st.button("Predict this existing match"):
            try:
                prediction = predict_existing_match_by_id(options[selected_label])
                st.subheader("Prediction")
                st.write(f"**Model type used:** {prediction.get('model_type', 'baseline')}")
                st.write(f"**Actual label:** {prediction.get('actual_label')}")
                st.write(f"**Predicted label:** {prediction['predicted_label']}")
                st.write(f"**Team A loss probability:** {prediction['probabilities']['team_a_loss']:.3f}")
                st.write(f"**Draw probability:** {prediction['probabilities']['draw']:.3f}")
                st.write(f"**Team A win probability:** {prediction['probabilities']['team_a_win']:.3f}")
            except Exception as exc:  # pragma: no cover - UI safety
                st.error(str(exc))
