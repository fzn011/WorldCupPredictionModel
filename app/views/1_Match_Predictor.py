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
APP_DIR = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

try:
    from app.components.ui import (  # noqa: E402
        inject_page_theme,
        render_data_table,
        render_hero,
        render_info_panel,
        render_metric_card,
        render_section_header,
        render_warning_panel,
    )
except ModuleNotFoundError:  # pragma: no cover
    from components.ui import (  # noqa: E402
        inject_page_theme,
        render_data_table,
        render_hero,
        render_info_panel,
        render_metric_card,
        render_section_header,
        render_warning_panel,
    )

from src.features.future_match_features import get_available_teams  # noqa: E402
from src.official.loaders import get_official_team_list  # noqa: E402
from src.models.explain_prediction import explain_future_match_prediction  # noqa: E402
from src.models.model_features import load_feature_dataset  # noqa: E402
import src.models.predict_match as predict_match_module  # noqa: E402
from src.models.prediction_utils import (  # noqa: E402
    format_explanation_table_for_display,
    get_prediction_confidence,
)
import src.utils.constants as C  # noqa: E402

DEFAULT_FUTURE_MATCH_DATE = getattr(C, "DEFAULT_FUTURE_MATCH_DATE", "2026-06-11")
DEFAULT_FUTURE_TOURNAMENT = getattr(C, "DEFAULT_FUTURE_TOURNAMENT", "FIFA World Cup")
DEFAULT_FUTURE_CITY = getattr(C, "DEFAULT_FUTURE_CITY", "Unknown")
DEFAULT_FUTURE_COUNTRY = getattr(C, "DEFAULT_FUTURE_COUNTRY", "Unknown")
DEFAULT_FUTURE_NEUTRAL = getattr(C, "DEFAULT_FUTURE_NEUTRAL", 1)

_SESSION_FUTURE_RESULT = "match_predictor_future_result"
_SESSION_HISTORICAL_RESULT = "match_predictor_historical_result"

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
    return get_available_teams(official_only=True)


@st.cache_data(show_spinner=False)
def _official_team_lock_enabled() -> bool:
    try:
        return bool(get_official_team_list())
    except FileNotFoundError:
        return False


def _render_future_prediction_results(
    *,
    prediction: dict,
    team_a: str,
    team_b: str,
    match_date_value,
    tournament: str,
    city: str,
    country: str,
    neutral: bool,
) -> None:
    probabilities = prediction["probabilities"]
    render_section_header("Prediction results")
    st.write(f"**Most likely outcome:** {prediction.get('predicted_label')}")
    confidence_label, confidence_score = get_prediction_confidence(probabilities)
    st.write(f"**Confidence:** {confidence_label} ({confidence_score:.0%})")

    p1, p2, p3 = st.columns(3)
    with p1:
        render_metric_card(f"{team_a} win", f"{probabilities['team_a_win']:.1%}", variant="ok")
    with p2:
        render_metric_card("Draw", f"{probabilities['draw']:.1%}", variant="warn")
    with p3:
        render_metric_card(f"{team_b} win", f"{probabilities['team_a_loss']:.1%}", variant="accent")

    notes = prediction.get("notes", [])
    if notes:
        st.markdown("**Notes**")
        for note in notes:
            st.write(f"- {note}")

    preview = prediction.get("feature_preview", {})
    if preview:
        with st.expander("Feature preview (technical)"):
            render_data_table(pd.DataFrame([preview]), use_container_width=True)

    with st.expander("How this prediction was generated"):
        try:
            explanation_result = explain_future_match_prediction(
                team_a=team_a,
                team_b=team_b,
                match_date=str(match_date_value),
                tournament=tournament,
                city=city,
                country=country,
                neutral=int(neutral),
            )

            method = explanation_result.get("explanation_method", "fallback")
            st.write(f"**Explanation method:** {method}")
            if method != "shap":
                st.warning(
                    "SHAP is unavailable or incompatible for this model/runtime. "
                    "Using a model-agnostic local sensitivity fallback."
                )

            st.markdown("**Natural-language explanation**")
            st.write(explanation_result.get("natural_language_explanation", "No explanation available."))

            support_df = format_explanation_table_for_display(
                explanation_result.get("top_supporting_factors", pd.DataFrame())
            )
            oppose_df = format_explanation_table_for_display(
                explanation_result.get("top_opposing_factors", pd.DataFrame())
            )

            st.markdown("**Top supporting factors**")
            if support_df.empty:
                st.info("No clear supporting factors were detected for this prediction.")
            else:
                render_data_table(support_df, use_container_width=True)

            st.markdown("**Top opposing factors**")
            if oppose_df.empty:
                st.info("No clear opposing factors were detected for this prediction.")
            else:
                render_data_table(oppose_df, use_container_width=True)
        except Exception as exc:  # pragma: no cover - UI safety
            st.warning(
                "Prediction explanation is currently unavailable. "
                f"The prediction itself is still valid. Details: {exc}"
            )


def _render_historical_prediction_results(prediction: dict) -> None:
    render_section_header("Prediction results")
    probs = prediction["probabilities"]
    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card("Team A loss", f"{probs['team_a_loss']:.1%}", variant="danger")
    with c2:
        render_metric_card("Draw", f"{probs['draw']:.1%}", variant="warn")
    with c3:
        render_metric_card("Team A win", f"{probs['team_a_win']:.1%}", variant="ok")
    st.write(f"**Predicted label:** {prediction['predicted_label']}")
    if prediction.get("actual_label") is not None:
        st.write(f"**Actual label:** {prediction.get('actual_label')}")


def render_page() -> None:
    render_hero(
        "Match Predictor",
        "Choose two World Cup teams and estimate the match outcome.",
        eyebrow="Match analytics",
    )

    with st.spinner("Loading match data..."):
        available_teams = _load_available_teams()
        feature_df = _load_features()
        official_team_lock = _official_team_lock_enabled()

    mode = st.radio(
        "Prediction mode",
        ["Future Match Prediction", "Historical match demo"],
        horizontal=True,
        help="Historical demo uses past matches for illustration only.",
    )

    if mode == "Future Match Prediction":
        if predict_future_match is None:
            st.error(
                "Predictor import is out of sync in the current Streamlit process. "
                "Please restart Streamlit to reload `src.models.predict_match`."
            )
            st.stop()

        if not available_teams:
            st.warning("No teams available yet. Run `python main.py` first.")
            st.stop()

        if official_team_lock:
            st.caption("Teams are limited to the official World Cup 2026 squad list.")

        with st.form("future_match_predict_form", clear_on_submit=False):
            form_col, preview_col = st.columns([3, 2], gap="large")

            with form_col:
                with st.container(border=True):
                    render_section_header("Match setup")
                    st.caption("Select two teams and match details, then run the prediction.")
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
                        city = st.text_input("City", value="", placeholder="e.g. New York")
                    with col6:
                        country = st.text_input("Country", value="", placeholder="e.g. United States")

                    neutral = st.checkbox("Neutral venue", value=bool(DEFAULT_FUTURE_NEUTRAL))

            venue = ", ".join(p for p in (city, country) if p) or "Venue TBD"
            neutral_label = "Neutral venue" if neutral else "Home/away context applied"

            with preview_col:
                with st.container(border=True):
                    render_section_header("Match preview")
                    st.markdown(
                        f"""
    <div class="wc-action-card" style="min-height:180px;">
      <div class="wc-action-title" style="font-size:1.25rem;">{team_a} vs {team_b}</div>
      <div class="wc-action-hint" style="margin-top:0.75rem;font-size:0.88rem;">
        {match_date_value}<br>{venue}<br>{tournament}<br>{neutral_label}
      </div>
    </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.caption("Results appear below after you predict.")

            predict_clicked = st.form_submit_button(
                "Predict match outcome",
                type="primary",
                use_container_width=True,
            )

        if predict_clicked:
            if team_a == team_b:
                st.session_state[_SESSION_FUTURE_RESULT] = {
                    "level": "error",
                    "message": "Team A and Team B must be different teams.",
                }
            else:
                with st.spinner("Running match prediction…"):
                    try:
                        prediction = predict_future_match(
                            team_a=team_a,
                            team_b=team_b,
                            match_date=str(match_date_value),
                            tournament=tournament,
                            city=city,
                            country=country,
                            neutral=int(neutral),
                            official_only=official_team_lock,
                        )
                        st.session_state[_SESSION_FUTURE_RESULT] = {
                            "level": "ok",
                            "prediction": prediction,
                            "team_a": team_a,
                            "team_b": team_b,
                            "match_date_value": str(match_date_value),
                            "tournament": tournament,
                            "city": city,
                            "country": country,
                            "neutral": neutral,
                        }
                    except FileNotFoundError:
                        st.session_state[_SESSION_FUTURE_RESULT] = {
                            "level": "error",
                            "message": "Model artifacts are missing. Run `python scripts/train_ranking_enhanced_model.py` first.",
                        }
                    except Exception as exc:  # pragma: no cover - UI safety
                        st.session_state[_SESSION_FUTURE_RESULT] = {
                            "level": "error",
                            "message": str(exc),
                        }

        future_result = st.session_state.get(_SESSION_FUTURE_RESULT)
        if future_result:
            if future_result.get("level") == "error":
                st.error(future_result.get("message", "Prediction failed."))
            elif future_result.get("level") == "ok":
                _render_future_prediction_results(
                    prediction=future_result["prediction"],
                    team_a=future_result["team_a"],
                    team_b=future_result["team_b"],
                    match_date_value=future_result["match_date_value"],
                    tournament=future_result["tournament"],
                    city=future_result["city"],
                    country=future_result["country"],
                    neutral=bool(future_result["neutral"]),
                )

    else:
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

            selected_label = st.selectbox("Choose a match", list(options.keys()), key="match_predictor_historical_select")

            with st.form("historical_match_predict_form", clear_on_submit=False):
                historical_clicked = st.form_submit_button("Predict this existing match", type="primary")

            if historical_clicked:
                with st.spinner("Running historical match prediction…"):
                    try:
                        prediction = predict_existing_match_by_id(options[selected_label])
                        st.session_state[_SESSION_HISTORICAL_RESULT] = {
                            "level": "ok",
                            "prediction": prediction,
                            "label": selected_label,
                        }
                    except Exception as exc:  # pragma: no cover - UI safety
                        st.session_state[_SESSION_HISTORICAL_RESULT] = {
                            "level": "error",
                            "message": str(exc),
                        }

            historical_result = st.session_state.get(_SESSION_HISTORICAL_RESULT)
            if historical_result:
                if historical_result.get("level") == "error":
                    st.error(historical_result.get("message", "Prediction failed."))
                elif historical_result.get("level") == "ok":
                    st.caption(f"Match: {historical_result.get('label', '—')}")
                    _render_historical_prediction_results(historical_result["prediction"])
