"""Tests for official-team filtering in prediction helpers."""

from __future__ import annotations

import pandas as pd
import pytest

from src.features.future_match_features import get_available_teams
from src.models.predict_match import predict_future_match
from src.official.loaders import is_official_team


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
            "team_a_has_fifa_ranking": [1],
            "team_b_has_fifa_ranking": [1],
            "team_a_has_elo": [1],
            "team_b_has_elo": [1],
        }
    )



def test_is_official_team_works(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.official.loaders.get_official_team_list", lambda: ["Argentina", "France"])
    assert is_official_team("Argentina") is True
    assert is_official_team("Brazil") is False



def test_predict_future_match_with_official_only_rejects_non_official_team(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.models.predict_match.is_official_team", lambda team_name: team_name == "Argentina")
    with pytest.raises(ValueError, match="not in the official World Cup 2026 team list"):
        predict_future_match("Argentina", "Brazil", official_only=True)



def test_get_available_teams_official_only_returns_official_teams(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.features.future_match_features.get_official_team_list", lambda: ["Argentina", "France"])
    teams = get_available_teams(official_only=True)
    assert teams == ["Argentina", "France"]
