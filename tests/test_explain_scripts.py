"""Smoke tests for Step 10 explainability scripts."""

from __future__ import annotations

import pandas as pd

from scripts.explain_future_match import main as explain_main
from scripts.inspect_global_explanation import main as inspect_global_main



def test_explain_future_match_script_smoke(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        "scripts.explain_future_match.explain_future_match_prediction",
        lambda **_: {
            "team_a": "Argentina",
            "team_b": "France",
            "match_date": "2026-06-11",
            "prediction": {
                "predicted_label": "team_a_loss",
                "probabilities": {"team_a_loss": 0.5, "draw": 0.3, "team_a_win": 0.2},
            },
            "explanation_method": "fallback",
            "natural_language_explanation": "The model appears to favor team_a_loss.",
            "top_supporting_factors": pd.DataFrame([{"readable_feature": "FIFA ranking advantage", "contribution": 0.1}]),
            "top_opposing_factors": pd.DataFrame([{"readable_feature": "Elo rating advantage", "contribution": -0.05}]),
            "report_path": str(tmp_path / "prediction_explanation_report.csv"),
        },
    )

    code = explain_main(["--team-a", "Argentina", "--team-b", "France", "--date", "2026-06-11"])
    assert code == 0



def test_inspect_global_explanation_script_smoke(monkeypatch, tmp_path) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    source_path = reports_dir / "ranking_feature_importance.csv"
    pd.DataFrame(
        {
            "feature": ["diff_fifa_rank", "diff_elo"],
            "importance": [0.7, 0.3],
        }
    ).to_csv(source_path, index=False)

    monkeypatch.chdir(tmp_path)
    code = inspect_global_main([])
    assert code == 0
    assert (reports_dir / "global_model_explanation.csv").is_file()
