"""Smoke tests for Step 8 CLI script entrypoints."""

from __future__ import annotations

import pandas as pd

from scripts.inspect_future_feature_row import main as inspect_main
from scripts.predict_future_match import main as predict_main



def _feature_row() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "team_a": ["Argentina"],
            "team_b": ["France"],
            "date": pd.to_datetime(["2026-06-11"]),
            "tournament": ["FIFA World Cup"],
            "team_a_matches_played_before": [100],
            "team_b_matches_played_before": [100],
            "team_a_last_5_win_rate": [0.7],
            "team_b_last_5_win_rate": [0.6],
            "diff_last_5_win_rate": [0.1],
            "team_a_goals_scored_avg_before": [1.9],
            "team_b_goals_scored_avg_before": [1.8],
            "diff_goal_diff_avg_before": [0.2],
            "team_a_fifa_rank": [3],
            "team_b_fifa_rank": [1],
            "diff_fifa_rank": [-2],
            "team_a_elo": [2113],
            "team_b_elo": [2081],
            "diff_elo": [32],
            "diff_strength_score": [0.05],
        }
    )



def test_inspect_future_feature_row_main_smoke(monkeypatch) -> None:
    monkeypatch.setattr(
        "scripts.inspect_future_feature_row.generate_future_match_feature_row",
        lambda **_: _feature_row(),
    )

    code = inspect_main(["--team-a", "Argentina", "--team-b", "France", "--date", "2026-06-11"])
    assert code == 0



def test_predict_future_match_main_smoke(monkeypatch, tmp_path) -> None:
    prediction = {
        "team_a": "Argentina",
        "team_b": "France",
        "match_date": "2026-06-11",
        "model_type": "ranking_enhanced",
        "predicted_class": 2,
        "predicted_label": "team_a_win",
        "probabilities": {"team_a_loss": 0.31, "draw": 0.25, "team_a_win": 0.44},
        "feature_row": _feature_row(),
        "notes": [],
    }

    monkeypatch.setattr("scripts.predict_future_match.predict_future_match", lambda **_: prediction)
    monkeypatch.setattr(
        "scripts.predict_future_match._append_prediction_log",
        lambda _df: tmp_path / "future_prediction_log.csv",
    )

    code = predict_main(["--team-a", "Argentina", "--team-b", "France", "--date", "2026-06-11"])
    assert code == 0
