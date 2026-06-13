"""Step 16 Monte Carlo reporting utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C

PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")
PROJECT_ROOT = getattr(C, "PROJECT_ROOT", Path(__file__).resolve().parents[2])
REPORTS_DIR = PROJECT_ROOT / "reports"

MONTE_CARLO_SIMULATION_RESULTS_FILE = getattr(C, "MONTE_CARLO_SIMULATION_RESULTS_FILE", "monte_carlo_simulation_results.csv")
MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE = getattr(C, "MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE", "monte_carlo_team_stage_probabilities.csv")
MONTE_CARLO_CHAMPION_PROBABILITIES_FILE = getattr(C, "MONTE_CARLO_CHAMPION_PROBABILITIES_FILE", "monte_carlo_champion_probabilities.csv")
MONTE_CARLO_FINALISTS_FILE = getattr(C, "MONTE_CARLO_FINALISTS_FILE", "monte_carlo_finalists.csv")
MONTE_CARLO_SEMIFINALISTS_FILE = getattr(C, "MONTE_CARLO_SEMIFINALISTS_FILE", "monte_carlo_semifinalists.csv")
MONTE_CARLO_SUMMARY_FILE = getattr(C, "MONTE_CARLO_SUMMARY_FILE", "monte_carlo_summary.json")
MONTE_CARLO_VALIDATION_REPORT_FILE = getattr(C, "MONTE_CARLO_VALIDATION_REPORT_FILE", "monte_carlo_validation_report.csv")
MONTE_CARLO_REPORT_MD_FILE = getattr(C, "MONTE_CARLO_REPORT_MD_FILE", "monte_carlo_report.md")
MONTE_CARLO_SUMMARY_CARDS_FILE = getattr(C, "MONTE_CARLO_SUMMARY_CARDS_FILE", "monte_carlo_summary_cards.csv")
MONTE_CARLO_DASHBOARD_EXPORT_FILE = getattr(C, "MONTE_CARLO_DASHBOARD_EXPORT_FILE", "monte_carlo_dashboard_export.csv")
MONTE_CARLO_TOP_N_TEAMS = int(getattr(C, "MONTE_CARLO_TOP_N_TEAMS", 20))
STAGE_PROBABILITY_DISPLAY_COLUMNS = list(
    getattr(
        C,
        "STAGE_PROBABILITY_DISPLAY_COLUMNS",
        [
            "team",
            "round_of_32_probability",
            "round_of_16_probability",
            "quarter_final_probability",
            "semi_final_probability",
            "final_probability",
            "champion_probability",
        ],
    )
)


def _processed_path(file_name: str) -> Path:
    return PROCESSED_DATA_DIR / file_name


def _reports_path(file_name: str) -> Path:
    return REPORTS_DIR / file_name


def _format_markdown_value(value: Any) -> str:
    """Convert a scalar value into a markdown-safe string."""
    if pd.isna(value):
        text = ""
    elif isinstance(value, float):
        text = f"{value:.6g}"
    else:
        text = str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def _dataframe_to_markdown(df: pd.DataFrame) -> str:
    """Render a dataframe as a GitHub-flavored markdown table without optional dependencies."""
    if df.empty:
        return ""

    headers = [str(column) for column in df.columns]
    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"
    data_rows = [
        "| " + " | ".join(_format_markdown_value(value) for value in row) + " |"
        for row in df.itertuples(index=False, name=None)
    ]
    return "\n".join([header_row, separator_row, *data_rows])


def _read_csv_required(file_name: str) -> pd.DataFrame:
    path = _processed_path(file_name)
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing Monte Carlo output: {path}. Run python scripts/run_monte_carlo.py --simulations 10 --seed 42"
        )
    return pd.read_csv(path)


def _read_json_required(file_name: str) -> dict[str, Any]:
    path = _processed_path(file_name)
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing Monte Carlo output: {path}. Run python scripts/run_monte_carlo.py --simulations 10 --seed 42"
        )
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_monte_carlo_outputs() -> dict[str, Any]:
    """Load all required Monte Carlo outputs from processed storage."""
    return {
        "simulation_results": _read_csv_required(MONTE_CARLO_SIMULATION_RESULTS_FILE),
        "team_stage_probabilities": _read_csv_required(MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE),
        "champion_probabilities": _read_csv_required(MONTE_CARLO_CHAMPION_PROBABILITIES_FILE),
        "finalists": _read_csv_required(MONTE_CARLO_FINALISTS_FILE),
        "semifinalists": _read_csv_required(MONTE_CARLO_SEMIFINALISTS_FILE),
        "summary": _read_json_required(MONTE_CARLO_SUMMARY_FILE),
        "validation_report": _read_csv_required(MONTE_CARLO_VALIDATION_REPORT_FILE),
    }


def create_summary_cards(outputs: dict[str, Any]) -> pd.DataFrame:
    """Create compact summary-card data for dashboard/report use."""
    summary = outputs.get("summary", {}) or {}
    stage_df = outputs.get("team_stage_probabilities", pd.DataFrame())
    cache_info = summary.get("cache_info", {}) if isinstance(summary, dict) else {}

    rows = [
        {"card": "Total simulations", "value": summary.get("num_simulations", 0)},
        {"card": "Successful simulations", "value": summary.get("successful_simulations", 0)},
        {"card": "Failed simulations", "value": summary.get("failed_simulations", 0)},
        {"card": "Validation status", "value": "passed" if summary.get("validation_passed") else "failed"},
        {"card": "Top champion", "value": summary.get("top_champion", "—")},
        {
            "card": "Top champion probability",
            "value": f"{float(summary.get('top_champion_probability', 0.0)):.2%}",
        },
        {"card": "Top finalist", "value": summary.get("top_finalist", "—")},
        {"card": "Number of teams simulated", "value": int(len(stage_df))},
        {"card": "Cache hits", "value": cache_info.get("cache_hits", 0)},
        {"card": "Cache misses", "value": cache_info.get("cache_misses", 0)},
    ]
    cards = pd.DataFrame(rows)
    cards["value"] = cards["value"].map(lambda value: "" if pd.isna(value) else str(value))
    return cards


def create_champion_probability_table(outputs: dict[str, Any], top_n: int = MONTE_CARLO_TOP_N_TEAMS) -> pd.DataFrame:
    """Create top-N champion probability display table."""
    df = outputs.get("champion_probabilities", pd.DataFrame()).copy()
    if df.empty:
        return pd.DataFrame(columns=["team", "champion_count", "champion_probability", "champion_probability_percent"])
    df = df.sort_values(["champion_probability", "champion_count", "team"], ascending=[False, False, True]).head(int(top_n)).reset_index(drop=True)
    df["champion_probability_percent"] = (df["champion_probability"] * 100).round(2)
    return df


def create_stage_probability_table(outputs: dict[str, Any], top_n: int = MONTE_CARLO_TOP_N_TEAMS) -> pd.DataFrame:
    """Create top-N stage progression display table."""
    df = outputs.get("team_stage_probabilities", pd.DataFrame()).copy()
    if df.empty:
        return pd.DataFrame(columns=STAGE_PROBABILITY_DISPLAY_COLUMNS)

    keep_cols = [col for col in STAGE_PROBABILITY_DISPLAY_COLUMNS if col in df.columns]
    df = df[keep_cols].copy()
    df = df.sort_values(["champion_probability", "final_probability", "team"], ascending=[False, False, True]).head(int(top_n)).reset_index(drop=True)
    for col in [c for c in keep_cols if c.endswith("_probability")]:
        df[f"{col}_percent"] = (df[col] * 100).round(2)
    return df


def create_monte_carlo_insight_text(outputs: dict[str, Any]) -> list[str]:
    """Generate concise narrative insights from Monte Carlo outputs."""
    summary = outputs.get("summary", {}) or {}
    finalists = outputs.get("finalists", pd.DataFrame())
    semifinalists = outputs.get("semifinalists", pd.DataFrame())

    most_frequent_finalist = finalists.iloc[0]["team"] if isinstance(finalists, pd.DataFrame) and not finalists.empty else "—"
    highest_semifinal_team = semifinalists.iloc[0]["team"] if isinstance(semifinalists, pd.DataFrame) and not semifinalists.empty else "—"
    highest_semifinal_prob = float(semifinalists.iloc[0]["semifinal_probability"]) if isinstance(semifinalists, pd.DataFrame) and not semifinalists.empty else 0.0

    return [
        f"Top champion estimate: {summary.get('top_champion', '—')} at {float(summary.get('top_champion_probability', 0.0)):.2%}.",
        f"Most frequent finalist: {most_frequent_finalist}.",
        f"Highest semi-final probability: {highest_semifinal_team} at {highest_semifinal_prob:.2%}.",
        f"Successful simulations: {summary.get('successful_simulations', 0)} of {summary.get('num_simulations', 0)}.",
        "These outputs are simulation estimates, not certainties.",
    ]


def generate_monte_carlo_markdown_report(outputs: dict[str, Any]) -> str:
    """Generate a Markdown report summarizing Monte Carlo outputs."""
    summary = outputs.get("summary", {}) or {}
    validation = outputs.get("validation_report", pd.DataFrame())
    champion_table = create_champion_probability_table(outputs)
    stage_table = create_stage_probability_table(outputs)
    finalists = outputs.get("finalists", pd.DataFrame())
    semifinalists = outputs.get("semifinalists", pd.DataFrame())
    insights = create_monte_carlo_insight_text(outputs)

    lines: list[str] = [
        "# Monte Carlo Tournament Report",
        "",
        "## Simulation summary",
        f"- Total simulations: {summary.get('num_simulations', 0)}",
        f"- Successful simulations: {summary.get('successful_simulations', 0)}",
        f"- Failed simulations: {summary.get('failed_simulations', 0)}",
        f"- Validation status: {'passed' if summary.get('validation_passed') else 'failed'}",
        f"- Top champion: {summary.get('top_champion', '—')} ({float(summary.get('top_champion_probability', 0.0)):.2%})",
        f"- Top finalist: {summary.get('top_finalist', '—')}",
        "",
        "## Insights",
    ]
    lines.extend([f"- {item}" for item in insights])

    lines.extend([
        "",
        "## Top champion probabilities",
        _dataframe_to_markdown(champion_table) if not champion_table.empty else "No champion probabilities available.",
        "",
        "## Stage progression overview",
        _dataframe_to_markdown(stage_table) if not stage_table.empty else "No stage progression table available.",
        "",
        "## Finalists and semi-finalists",
        "### Finalists",
        _dataframe_to_markdown(finalists.head(MONTE_CARLO_TOP_N_TEAMS)) if isinstance(finalists, pd.DataFrame) and not finalists.empty else "No finalists table available.",
        "",
        "### Semi-finalists",
        _dataframe_to_markdown(semifinalists.head(MONTE_CARLO_TOP_N_TEAMS)) if isinstance(semifinalists, pd.DataFrame) and not semifinalists.empty else "No semifinalists table available.",
        "",
        "## Validation summary",
        _dataframe_to_markdown(validation) if isinstance(validation, pd.DataFrame) and not validation.empty else "No validation report available.",
        "",
        "## Notes and limitations",
        "- Probabilities depend on sample size.",
        "- Outputs depend on current fixture and group assumptions.",
        "- Outputs depend on underlying model quality.",
        "- Ranking and Elo features currently use snapshot-style assumptions rather than strict date-aware historical joins.",
        "- This project is educational sports analytics, not betting advice.",
    ])
    return "\n".join(lines)


def save_monte_carlo_report(outputs: dict[str, Any], output_path: str | None = None) -> str:
    """Save generated Markdown report to reports directory."""
    path = Path(output_path) if output_path else _reports_path(MONTE_CARLO_REPORT_MD_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(generate_monte_carlo_markdown_report(outputs), encoding="utf-8")
    return str(path)


def save_summary_cards(cards_df: pd.DataFrame, output_path: str | None = None) -> str:
    """Save summary card table to CSV."""
    path = Path(output_path) if output_path else _reports_path(MONTE_CARLO_SUMMARY_CARDS_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    cards_df.to_csv(path, index=False)
    return str(path)


def save_dashboard_export(outputs: dict[str, Any], output_path: str | None = None) -> str:
    """Save a combined CSV export for dashboard review."""
    path = Path(output_path) if output_path else _reports_path(MONTE_CARLO_DASHBOARD_EXPORT_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)

    frames: list[pd.DataFrame] = []
    sections = {
        "champion_probabilities": create_champion_probability_table(outputs),
        "stage_probabilities": create_stage_probability_table(outputs),
        "finalists": outputs.get("finalists", pd.DataFrame()),
        "semifinalists": outputs.get("semifinalists", pd.DataFrame()),
    }
    for section_name, df in sections.items():
        if isinstance(df, pd.DataFrame) and not df.empty:
            export_df = df.copy()
            export_df.insert(0, "section", section_name)
            frames.append(export_df)

    combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=["section"])
    combined.to_csv(path, index=False)
    return str(path)
