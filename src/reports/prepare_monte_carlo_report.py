"""Step 16 Monte Carlo report preparation orchestrator."""

from __future__ import annotations

from typing import Any

from src.reports.monte_carlo_report import (
    create_champion_probability_table,
    create_monte_carlo_insight_text,
    create_stage_probability_table,
    create_summary_cards,
    load_monte_carlo_outputs,
    save_dashboard_export,
    save_monte_carlo_report,
    save_summary_cards,
)
from src.reports.monte_carlo_visuals import (
    plot_champion_probabilities,
    plot_stage_probability_heatmap,
)


def prepare_step16_monte_carlo_report() -> dict[str, Any]:
    """Generate Step 16 report/figure artifacts from existing Monte Carlo outputs."""
    outputs = load_monte_carlo_outputs()
    summary_cards_df = create_summary_cards(outputs)
    champion_table = create_champion_probability_table(outputs)
    stage_table = create_stage_probability_table(outputs)
    insights = create_monte_carlo_insight_text(outputs)

    report_path = save_monte_carlo_report(outputs)
    summary_cards_path = save_summary_cards(summary_cards_df)
    dashboard_export_path = save_dashboard_export(outputs)
    champion_chart_path = plot_champion_probabilities(champion_table)
    stage_heatmap_path = plot_stage_probability_heatmap(stage_table)

    summary = outputs.get("summary", {}) or {}
    return {
        "status": "ok",
        "report_path": report_path,
        "summary_cards_path": summary_cards_path,
        "dashboard_export_path": dashboard_export_path,
        "champion_chart_path": champion_chart_path,
        "stage_heatmap_path": stage_heatmap_path,
        "top_champion": summary.get("top_champion"),
        "top_champion_probability": summary.get("top_champion_probability"),
        "validation_status": "passed" if summary.get("validation_passed") else "failed",
        "insights": insights,
    }


if __name__ == "__main__":
    print(prepare_step16_monte_carlo_report())
