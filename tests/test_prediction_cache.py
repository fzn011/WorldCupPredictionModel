"""Tests for cached match prediction utility."""

from __future__ import annotations

from src.models import prediction_cache as pc


def test_cached_predictor_reuses_identical_requests(monkeypatch) -> None:
    calls: list[tuple[str, str]] = []

    def _fake_predict_future_match(**kwargs):
        calls.append((kwargs["team_a"], kwargs["team_b"]))
        return {
            "model_type": "fake",
            "predicted_label": "team_a_win",
            "probabilities": {
                "team_a_loss": 0.25,
                "draw": 0.25,
                "team_a_win": 0.50,
            },
        }

    monkeypatch.setattr(pc, "predict_future_match", _fake_predict_future_match)

    predictor = pc.CachedMatchPredictor()
    first = predictor.predict("A", "B", "2026-06-11")
    second = predictor.predict("A", "B", "2026-06-11")

    assert first == second
    assert len(calls) == 1

    info = predictor.cache_info()
    assert info["total_requests"] == 2
    assert info["cache_hits"] == 1
    assert info["cache_misses"] == 1
    assert info["cache_size"] == 1


def test_cached_predictor_direction_sensitive_keys(monkeypatch) -> None:
    def _fake_predict_future_match(**kwargs):
        return {
            "model_type": "fake",
            "predicted_label": "team_a_win",
            "probabilities": {
                "team_a_loss": 0.25,
                "draw": 0.25,
                "team_a_win": 0.50,
            },
            "signature": f"{kwargs['team_a']}->{kwargs['team_b']}",
        }

    monkeypatch.setattr(pc, "predict_future_match", _fake_predict_future_match)

    predictor = pc.CachedMatchPredictor()
    ab = predictor.predict("A", "B", "2026-06-11")
    ba = predictor.predict("B", "A", "2026-06-11")

    assert ab["signature"] == "A->B"
    assert ba["signature"] == "B->A"

    info = predictor.cache_info()
    assert info["cache_size"] == 2


def test_cache_info_has_expected_keys() -> None:
    predictor = pc.CachedMatchPredictor()
    info = predictor.cache_info()
    assert {"total_requests", "cache_hits", "cache_misses", "cache_size"}.issubset(set(info.keys()))
