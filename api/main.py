"""Optional FastAPI endpoint for future match predictions."""

from __future__ import annotations

from pydantic import BaseModel
from fastapi import FastAPI

from src.models.predict_match import predict_future_match
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
    return {
        "project": "FIFA World Cup 2026 AI Predictor",
        "status": "ok",
    }


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
    # API response should stay JSON-serializable.
    result.pop("feature_row", None)
    return result
