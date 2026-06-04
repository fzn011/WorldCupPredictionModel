"""Tests for Step 10 local prediction explainability."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.models.explain_prediction import (
    align_feature_row_for_explanation,
    create_natural_language_explanation,
    explain_future_match_prediction,
    get_model_probability_change_explanation,
    is_shap_available,
    save_explanation_report,
)


class _DummyModel:
    classes_ = [0, 1, 2]

    def predict_proba(self, X):
        x = X.fillna(0.0)
        boost = float(x.iloc[0, 0]) if x.shape[1] else 0.0
        return [[max(0.0, 0.4 - boost * 0.05), 0.2, min(1.0, 0.4 + boost * 0.05)]]



def _feature_row() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "team_a": ["Argentina"],
            "team_b": ["France"],
            "date": pd.to_datetime(["2026-06-11"]),
            "team_a_last_5_win_rate": [0.7],
            "team_b_last_5_win_rate": [0.6],
            "diff_last_5_win_rate": [0.1],
            "team_a_fifa_rank": [3],
            "team_b_fifa_rank": [1],
            "diff_fifa_rank": [-2],
        }
    )



def test_is_shap_available_returns_bool() -> None:
    assert isinstance(is_shap_available(), bool)



def test_align_feature_row_for_explanation_aligns_columns() -> None:
    row = _feature_row()
    columns = ["diff_last_5_win_rate", "missing_feature", "team_a_fifa_rank"]
    aligned = align_feature_row_for_explanation(row, columns)
    assert aligned.columns.tolist() == columns
    assert aligned.shape[0] == 1



def test_get_model_probability_change_explanation_returns_dataframe() -> None:
    row = _feature_row()
    columns = ["team_a_last_5_win_rate", "team_b_last_5_win_rate", "diff_last_5_win_rate"]
    model = _DummyModel()

    explanation = get_model_probability_change_explanation(
        model=model,
        X_row=row,
        feature_columns=columns,
        target_class_index=2,
        top_n=5,
    )
    assert isinstance(explanation, pd.DataFrame)
    assert not explanation.empty
    assert {"feature", "contribution", "direction"}.issubset(set(explanation.columns))



def test_create_natural_language_explanation_returns_string() -> None:
    df = pd.DataFrame(
        [
            {"readable_feature": "FIFA ranking advantage", "direction": "supports", "contribution": 0.1},
            {"readable_feature": "Elo rating advantage", "direction": "opposes", "contribution": -0.05},
        ]
    )
    text = create_natural_language_explanation(
        df,
        {
            "predicted_label": "team_a_loss",
            "probabilities": {"team_a_loss": 0.52, "draw": 0.23, "team_a_win": 0.25},
        },
    )
    assert isinstance(text, str)
    assert "analytics estimate" in text



def test_explain_future_match_prediction_monkeypatched(monkeypatch: pytest.MonkeyPatch) -> None:
    prediction_payload = {
        "team_a": "Argentina",
        "team_b": "France",
        "match_date": "2026-06-11",
        "model_type": "ranking_enhanced",
        "predicted_label": "team_a_win",
        "probabilities": {"team_a_loss": 0.2, "draw": 0.2, "team_a_win": 0.6},
        "feature_row": _feature_row(),
    }

    monkeypatch.setattr("src.models.explain_prediction.predict_future_match", lambda **_: prediction_payload)
    monkeypatch.setattr(
        "src.models.explain_prediction.load_best_model_and_features_for_explanation",
        lambda: (_DummyModel(), "ranking_enhanced", ["team_a_last_5_win_rate", "team_b_last_5_win_rate"]),
    )
    monkeypatch.setattr("src.models.explain_prediction.is_shap_available", lambda: False)

    result = explain_future_match_prediction(
        team_a="Argentina",
        team_b="France",
        match_date="2026-06-11",
        tournament="FIFA World Cup",
        city="Unknown",
        country="Unknown",
        neutral=1,
    )

    expected_keys = {
        "team_a",
        "team_b",
        "match_date",
        "prediction",
        "explanation_method",
        "top_supporting_factors",
        "top_opposing_factors",
        "natural_language_explanation",
        "report_path",
    }
    assert expected_keys.issubset(set(result.keys()))



def test_save_explanation_report_writes_csv(tmp_path: Path) -> None:
    explanation = {
        "team_a": "Argentina",
        "team_b": "France",
        "match_date": "2026-06-11",
        "prediction": {"predicted_label": "team_a_win", "model_type": "ranking_enhanced"},
        "explanation_method": "fallback",
        "explanation_table": pd.DataFrame(
            [{"feature": "diff_fifa_rank", "readable_feature": "FIFA ranking advantage", "contribution": 0.1}]
        ),
        "top_supporting_factors": pd.DataFrame([{"readable_feature": "FIFA ranking advantage"}]),
        "top_opposing_factors": pd.DataFrame(),
    }

    output_path = tmp_path / "prediction_explanation_report.csv"
    path = save_explanation_report(explanation, output_path=str(output_path))
    assert path.is_file()
    assert output_path.exists()
