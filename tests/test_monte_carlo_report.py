"""Tests for Step 16 Monte Carlo reporting utilities."""

from __future__ import annotations

import pandas as pd

from src.reports.monte_carlo_report import (
    create_champion_probability_table,
    create_monte_carlo_insight_text,
    create_stage_probability_table,
    create_summary_cards,
    generate_monte_carlo_markdown_report,
)


def _synthetic_outputs() -> dict:
    return {
        "simulation_results": pd.DataFrame({"simulation_id": [1, 2], "status": ["success", "success"]}),
        "team_stage_probabilities": pd.DataFrame(
            {
                "team": ["France", "Brazil"],
                "round_of_32_probability": [1.0, 1.0],
                "round_of_16_probability": [0.8, 0.7],
                "quarter_final_probability": [0.5, 0.4],
                "semi_final_probability": [0.3, 0.2],
                "final_probability": [0.2, 0.1],
                "champion_probability": [0.2, 0.1],
            }
        ),
        "champion_probabilities": pd.DataFrame(
            {
                "team": ["France", "Brazil"],
                "champion_count": [2, 1],
                "champion_probability": [0.2, 0.1],
            }
        ),
        "finalists": pd.DataFrame({"team": ["France"], "final_appearance_probability": [0.2]}),
        "semifinalists": pd.DataFrame({"team": ["France"], "semifinal_probability": [0.3]}),
        "summary": {
            "num_simulations": 10,
            "successful_simulations": 10,
            "failed_simulations": 0,
            "validation_passed": True,
            "top_champion": "France",
            "top_champion_probability": 0.2,
            "top_finalist": "France",
            "cache_info": {"cache_hits": 5, "cache_misses": 3},
        },
        "validation_report": pd.DataFrame({"check": ["ok"], "passed": [True]}),
    }


def test_create_summary_cards_returns_expected_columns() -> None:
    cards = create_summary_cards(_synthetic_outputs())
    assert list(cards.columns) == ["card", "value"]
    assert not cards.empty
    assert cards["value"].map(type).eq(str).all()


def test_prepare_table_display_stringifies_mixed_object_column() -> None:
    from app.components.ui import _prepare_table_display

    df = pd.DataFrame(
        [
            {"card": "Total simulations", "value": 10},
            {"card": "Validation status", "value": "passed"},
        ]
    )
    out = _prepare_table_display(df, hide_index=True)
    assert out["value"].tolist() == ["10", "passed"]


def test_create_champion_probability_table_returns_sorted_top_n() -> None:
    df = create_champion_probability_table(_synthetic_outputs(), top_n=1)
    assert len(df) == 1
    assert df.iloc[0]["team"] == "France"


def test_create_stage_probability_table_returns_expected_columns() -> None:
    df = create_stage_probability_table(_synthetic_outputs(), top_n=2)
    assert "team" in df.columns
    assert "champion_probability" in df.columns


def test_create_monte_carlo_insight_text_returns_strings() -> None:
    insights = create_monte_carlo_insight_text(_synthetic_outputs())
    assert isinstance(insights, list)
    assert insights
    assert all(isinstance(item, str) for item in insights)


def test_generate_monte_carlo_markdown_report_returns_markdown_string() -> None:
    report = generate_monte_carlo_markdown_report(_synthetic_outputs())
    assert isinstance(report, str)
    assert "# Monte Carlo Tournament Report" in report
