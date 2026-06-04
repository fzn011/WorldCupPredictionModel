from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from src.models.explain_prediction import explain_future_match_prediction
from src.models.predict_match import predict_future_match
from src.models.prediction_utils import format_explanation_table_for_display
import src.utils.constants as C

DEFAULT_FUTURE_MATCH_DATE = getattr(C, "DEFAULT_FUTURE_MATCH_DATE", "2026-06-11")
DEFAULT_FUTURE_TOURNAMENT = getattr(C, "DEFAULT_FUTURE_TOURNAMENT", "FIFA World Cup")
DEFAULT_FUTURE_CITY = getattr(C, "DEFAULT_FUTURE_CITY", "Unknown")
DEFAULT_FUTURE_COUNTRY = getattr(C, "DEFAULT_FUTURE_COUNTRY", "Unknown")
DEFAULT_FUTURE_NEUTRAL = getattr(C, "DEFAULT_FUTURE_NEUTRAL", 1)

app = FastAPI(title="FIFA World Cup 2026 AI Predictor API")


class FutureMatchRequest(BaseModel):
    team_a: str
    team_b: str
    match_date: str = DEFAULT_FUTURE_MATCH_DATE
    tournament: str = DEFAULT_FUTURE_TOURNAMENT
    city: str = DEFAULT_FUTURE_CITY
    country: str = DEFAULT_FUTURE_COUNTRY
    neutral: int = DEFAULT_FUTURE_NEUTRAL


@app.get("/")
def root() -> dict:
    return {"project": "FIFA World Cup 2026 AI Predictor", "status": "ok"}


@app.post("/predict/future-match")
def predict_future_match_endpoint(payload: FutureMatchRequest) -> dict:
    result = predict_future_match(
        team_a=payload.team_a,
        team_b=payload.team_b,
        match_date=payload.match_date,
        tournament=payload.tournament,
        city=payload.city,
        country=payload.country,
        neutral=payload.neutral,
    )
    result.pop("feature_row", None)
    return result


@app.post("/explain/future-match")
def explain_future_match_endpoint(payload: FutureMatchRequest) -> dict:
    result = explain_future_match_prediction(
        team_a=payload.team_a,
        team_b=payload.team_b,
        match_date=payload.match_date,
        tournament=payload.tournament,
        city=payload.city,
        country=payload.country,
        neutral=payload.neutral,
    )

    explanation_table = format_explanation_table_for_display(result.get("explanation_table"))
    support_table = format_explanation_table_for_display(result.get("top_supporting_factors"))
    oppose_table = format_explanation_table_for_display(result.get("top_opposing_factors"))

    payload_out = {
        "team_a": result.get("team_a"),
        "team_b": result.get("team_b"),
        "match_date": result.get("match_date"),
        "prediction": result.get("prediction", {}),
        "explanation_method": result.get("explanation_method"),
        "natural_language_explanation": result.get("natural_language_explanation"),
        "top_supporting_factors": support_table.to_dict(orient="records"),
        "top_opposing_factors": oppose_table.to_dict(orient="records"),
        "explanation_table": explanation_table.to_dict(orient="records"),
        "report_path": result.get("report_path"),
    }

    prediction_payload = payload_out.get("prediction", {})
    if isinstance(prediction_payload, dict):
        prediction_payload.pop("feature_row", None)

    return payload_out
