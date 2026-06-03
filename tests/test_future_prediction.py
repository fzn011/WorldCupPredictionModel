"""Tests for Step 8 future prediction APIs."""

from __future__ import annotations

import pandas as pd
import pytest

from src.models.predict_match import (
    get_probability_dict_from_model,
    predict_future_match,
    predict_match_result,
)


class _DummyModel:
    classes_ = [0, 1, 2]

    def predict_proba(self, X):
        return [[0.3, 0.2, 0.5]]



def _future_feature_row() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "match_id": ["future_20260611_argentina-vs-france"],
            "date": pd.to_datetime(["2026-06-11"]),
            "team_a": ["Argentina"],
            "team_b": ["France"],
            "tournament": ["FIFA World Cup"],
            "team_a_last_5_win_rate": [0.7],
            "team_b_last_5_win_rate": [0.6],
            "diff_last_5_win_rate": [0.1],
            "team_a_has_fifa_ranking": [1],
            "team_b_has_fifa_ranking": [1],
            "team_a_has_elo": [1],
            "team_b_has_elo": [1],
            "team_a_fifa_rank": [3],
            "team_b_fifa_rank": [1],
            "team_a_elo": [2113],
            "team_b_elo": [2081],
            "diff_elo": [32],
        }
    )



def test_predict_future_match_with_monkeypatched_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "src.models.predict_match.generate_future_match_feature_row",
        lambda **_: _future_feature_row(),
    )
    monkeypatch.setattr(
        "src.models.predict_match.load_best_available_model",
        lambda **_: (_DummyModel(), "ranking_enhanced"),
    )
    monkeypatch.setattr(
        "src.models.predict_match.load_best_available_feature_columns",
        lambda **_: ["team_a_last_5_win_rate", "team_b_last_5_win_rate", "diff_last_5_win_rate"],
    )

    result = predict_future_match("Argentina", "France", "2026-06-11")
    assert result["model_type"] == "ranking_enhanced"
    assert result["predicted_label"] == "team_a_win"
    assert set(result["probabilities"].keys()) == {"team_a_loss", "draw", "team_a_win"}



def test_predict_match_result_returns_clear_error_when_missing_model(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise(*_args, **_kwargs):
        raise FileNotFoundError("missing model")

    monkeypatch.setattr("src.models.predict_match.predict_future_match", _raise)
    out = predict_match_result("Argentina", "France")
    assert "error" in out
    assert "Future prediction failed" in out["message"]



def test_predict_future_match_same_team_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise(*_args, **_kwargs):
        raise ValueError("team_a and team_b must be different teams.")

    monkeypatch.setattr("src.models.predict_match.generate_future_match_feature_row", _raise)

    with pytest.raises(ValueError):
        predict_future_match("Argentina", "Argentina", "2026-06-11")



def test_predict_future_match_missing_model_raises_clear_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "src.models.predict_match.generate_future_match_feature_row",
        lambda **_: _future_feature_row(),
    )

    def _raise(*_args, **_kwargs):
        raise FileNotFoundError("no model")

    monkeypatch.setattr("src.models.predict_match.load_best_available_model", _raise)

    with pytest.raises(FileNotFoundError, match="train_ranking_enhanced_model"):
        predict_future_match("Argentina", "France", "2026-06-11")



def test_probability_dict_contains_expected_keys() -> None:
    out = get_probability_dict_from_model(
        _DummyModel(),
        pd.DataFrame([[1, 2, 3]], columns=["a", "b", "c"]),
    )
    assert set(out.keys()) == {"team_a_loss", "draw", "team_a_win"}
