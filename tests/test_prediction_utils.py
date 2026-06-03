"""Tests for Step 9 prediction utility helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.models.prediction_utils import (
    append_prediction_history,
    extract_prediction_explanation_features,
    flatten_prediction_result,
    format_probability,
    get_prediction_confidence,
    load_prediction_history,
    save_latest_prediction_report,
)



def _prediction_result() -> dict:
    return {
        "team_a": "Argentina",
        "team_b": "France",
        "match_date": "2026-06-11",
        "tournament": "FIFA World Cup",
        "city": "Unknown",
        "country": "Unknown",
        "neutral": 1,
        "model_type": "ranking_enhanced",
        "predicted_class": 0,
        "predicted_label": "team_a_loss",
        "probabilities": {
            "team_a_loss": 0.5,
            "draw": 0.25,
            "team_a_win": 0.25,
        },
        "confidence": {
            "max_probability": 0.5,
            "confidence_label": "Medium",
        },
        "notes": ["snapshot ranking in use"],
    }



def test_get_prediction_confidence_thresholds() -> None:
    high = get_prediction_confidence({"a": 0.60, "b": 0.2})
    med = get_prediction_confidence({"a": 0.45, "b": 0.2})
    low = get_prediction_confidence({"a": 0.44, "b": 0.3})

    assert high["confidence_label"] == "High"
    assert med["confidence_label"] == "Medium"
    assert low["confidence_label"] == "Low"



def test_format_probability() -> None:
    assert format_probability(0.5) == "50.00%"



def test_flatten_prediction_result_keys() -> None:
    out = flatten_prediction_result(_prediction_result())
    expected = {
        "prediction_timestamp",
        "team_a",
        "team_b",
        "match_date",
        "tournament",
        "city",
        "country",
        "neutral",
        "model_type",
        "predicted_class",
        "predicted_label",
        "team_a_loss_probability",
        "draw_probability",
        "team_a_win_probability",
        "confidence_label",
        "max_probability",
        "notes",
    }
    assert expected.issubset(set(out.keys()))



def test_append_prediction_history_writes_csv(tmp_path: Path) -> None:
    out_path = tmp_path / "history.csv"
    written = append_prediction_history(_prediction_result(), output_path=str(out_path))
    assert Path(written).is_file()
    df = pd.read_csv(written)
    assert len(df) == 1



def test_save_latest_prediction_report_writes_csv(tmp_path: Path) -> None:
    out_path = tmp_path / "latest.csv"
    written = save_latest_prediction_report(_prediction_result(), output_path=str(out_path))
    assert Path(written).is_file()
    df = pd.read_csv(written)
    assert len(df) == 1



def test_load_prediction_history_returns_dataframe(tmp_path: Path) -> None:
    missing = load_prediction_history(path=str(tmp_path / "does_not_exist.csv"))
    assert isinstance(missing, pd.DataFrame)
    assert missing.empty



def test_extract_prediction_explanation_features_columns() -> None:
    row = pd.DataFrame(
        {
            "team_a_last_5_win_rate": [1.0],
            "team_b_last_5_win_rate": [0.8],
            "diff_last_5_win_rate": [0.2],
        }
    )
    out = extract_prediction_explanation_features(row)
    assert {"feature", "value"}.issubset(out.columns)
    assert "team_a_last_5_win_rate" in set(out["feature"])
