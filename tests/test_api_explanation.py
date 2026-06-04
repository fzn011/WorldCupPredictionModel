"""Tests for Step 10 explanation API endpoint."""

from __future__ import annotations

import pytest



def test_explain_future_match_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    _ = pytest.importorskip("fastapi")
    _ = pytest.importorskip("httpx")
    testclient = pytest.importorskip("fastapi.testclient")

    from api.main import app

    sample_result = {
        "team_a": "Argentina",
        "team_b": "France",
        "match_date": "2026-06-11",
        "prediction": {
            "predicted_label": "team_a_loss",
            "model_type": "ranking_enhanced",
            "probabilities": {"team_a_loss": 0.49, "draw": 0.29, "team_a_win": 0.22},
        },
        "explanation_method": "fallback",
        "natural_language_explanation": "The model appears to favor team_a_loss.",
        "top_supporting_factors": [],
        "top_opposing_factors": [],
        "explanation_table": [],
        "report_path": "reports/prediction_explanation_report.csv",
    }

    monkeypatch.setattr("api.main.explain_future_match_prediction", lambda **_: sample_result)

    client = testclient.TestClient(app)
    response = client.post(
        "/explain/future-match",
        json={
            "team_a": "Argentina",
            "team_b": "France",
            "match_date": "2026-06-11",
            "tournament": "FIFA World Cup",
            "city": "Unknown",
            "country": "Unknown",
            "neutral": 1,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["prediction"]["predicted_label"] == "team_a_loss"
    assert payload["explanation_method"] == "fallback"
    assert "natural_language_explanation" in payload
