"""Tests for optional Step 9 FastAPI endpoint."""

from __future__ import annotations

import importlib

import pytest

fastapi = pytest.importorskip("fastapi")
try:
    from fastapi.testclient import TestClient
except Exception as exc:  # pragma: no cover - environment dependent
    pytest.skip(f"FastAPI test client unavailable: {exc}", allow_module_level=True)

api_main = importlib.import_module("api.main")



def test_api_root() -> None:
    client = TestClient(api_main.app)
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"



def test_api_predict_future_match(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "api.main.predict_future_match",
        lambda **_: {
            "team_a": "Argentina",
            "team_b": "France",
            "model_type": "ranking_enhanced",
            "predicted_label": "team_a_loss",
            "probabilities": {"team_a_loss": 0.5, "draw": 0.25, "team_a_win": 0.25},
        },
    )

    client = TestClient(api_main.app)
    response = client.post(
        "/predict/future-match",
        json={
            "team_a": "Argentina",
            "team_b": "France",
            "match_date": "2026-06-11",
            "tournament": "FIFA World Cup",
            "neutral": 1,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["model_type"] == "ranking_enhanced"
    assert "probabilities" in payload
