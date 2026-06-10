"""Reporting utilities for Step 17 World Cup awards analytics."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C

PROJECT_ROOT = getattr(C, "PROJECT_ROOT", Path(__file__).resolve().parents[2])
REPORTS_DIR = PROJECT_ROOT / "reports"
WORLD_CUP_AWARDS_REPORT_FILE = getattr(C, "WORLD_CUP_AWARDS_REPORT_FILE", "world_cup_awards_report.md")
AWARDS_ANALYTICS_DISCLAIMER = str(
    getattr(
        C,
        "AWARDS_ANALYTICS_DISCLAIMER",
        "These awards are explainable analytics estimates based on manually editable player priors, team profiles, and Monte Carlo team progression probabilities. They are not official FIFA predictions.",
    )
)


def _format_markdown_value(value: Any) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, float):
        text = f"{value:.6g}"
    else:
        text = str(value)
    return text.replace("|", "\\|").replace("\n", " ")



def _dataframe_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    headers = [str(column) for column in df.columns]
    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"
    data_rows = [
        "| " + " | ".join(_format_markdown_value(v) for v in row) + " |"
        for row in df.itertuples(index=False, name=None)
    ]
    return "\n".join([header_row, separator_row, *data_rows])



def _top_value(df: pd.DataFrame, column: str) -> str:
    if not isinstance(df, pd.DataFrame) or df.empty or column not in df.columns:
        return "—"
    return str(df.iloc[0][column])



def create_world_cup_awards_summary(outputs: dict, validation_passed: bool) -> dict[str, Any]:
    """Create compact summary for the broader Step 17 awards outputs."""
    team_of_tournament = outputs.get("team_of_tournament", pd.DataFrame())
    return {
        "status": "ok" if validation_passed else "validation_failed",
        "validation_passed": bool(validation_passed),
        "top_golden_ball_player": _top_value(outputs.get("golden_ball", pd.DataFrame()), "player"),
        "top_golden_boot_player": _top_value(outputs.get("golden_boot", pd.DataFrame()), "player"),
        "top_golden_glove_player": _top_value(outputs.get("golden_glove", pd.DataFrame()), "player"),
        "top_young_player": _top_value(outputs.get("young_player", pd.DataFrame()), "player"),
        "top_fair_play_team": _top_value(outputs.get("fair_play", pd.DataFrame()), "team"),
        "top_entertaining_team": _top_value(outputs.get("most_entertaining", pd.DataFrame()), "team"),
        "team_of_tournament_count": int(len(team_of_tournament)) if isinstance(team_of_tournament, pd.DataFrame) else 0,
        "notes": AWARDS_ANALYTICS_DISCLAIMER,
    }



def create_combined_awards_table(outputs: dict) -> pd.DataFrame:
    """Create a combined long-format awards table across all Step 17 outputs."""
    frames: list[pd.DataFrame] = []

    mapping: list[tuple[str, str, str, str, str]] = [
        ("golden_ball", "award_podium", "golden_ball_rank", "final_golden_ball_score", "golden_ball_probability"),
        ("golden_boot", "boot_podium", "golden_boot_rank", "golden_boot_tiebreak_score", "golden_boot_probability"),
        ("golden_glove", "award", "golden_glove_rank", "golden_glove_score", "golden_glove_probability"),
        ("young_player", "award", "young_player_rank", "young_player_score", "young_player_probability"),
        ("fair_play", "award", "fair_play_rank", "fair_play_score", "fair_play_probability"),
        ("most_entertaining", "award", "most_entertaining_rank", "most_entertaining_score", "most_entertaining_probability"),
        ("player_of_match_proxy", "player_of_match_proxy_rank", "player_of_match_proxy_rank", "estimated_potm_count", "player_impact_share_proxy"),
        ("goal_of_tournament_proxy", "goal_of_tournament_proxy_rank", "goal_of_tournament_proxy_rank", "goal_of_tournament_proxy_score", "goal_of_tournament_proxy_probability"),
    ]

    for key, award_col, rank_col, score_col, probability_col in mapping:
        df = outputs.get(key, pd.DataFrame())
        if not isinstance(df, pd.DataFrame) or df.empty:
            continue
        export = pd.DataFrame(
            {
                "award_category": key,
                "rank": df[rank_col] if rank_col in df.columns else pd.Series(range(1, len(df) + 1)),
                "award": df[award_col] if award_col in df.columns else "",
                "player": df["player"] if "player" in df.columns else "",
                "team": df["team"] if "team" in df.columns else "",
                "position": df["position"] if "position" in df.columns else "",
                "score": df[score_col] if score_col in df.columns else 0.0,
                "probability": df[probability_col] if probability_col in df.columns else 0.0,
                "notes": "proxy estimate" if key in {"player_of_match_proxy", "goal_of_tournament_proxy"} else "analytics estimate",
            }
        )
        frames.append(export)

    team_df = outputs.get("team_of_tournament", pd.DataFrame())
    if isinstance(team_df, pd.DataFrame) and not team_df.empty:
        export = pd.DataFrame(
            {
                "award_category": "team_of_tournament",
                "rank": range(1, len(team_df) + 1),
                "award": team_df.get("award", "Predicted Team of the Tournament"),
                "player": team_df.get("player", ""),
                "team": team_df.get("team", ""),
                "position": team_df.get("position", ""),
                "score": team_df.get("final_golden_ball_score", 0.0),
                "probability": team_df.get("golden_ball_probability", 0.0),
                "notes": "unofficial analytics XI",
            }
        )
        frames.append(export)

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(
        columns=["award_category", "rank", "award", "player", "team", "position", "score", "probability", "notes"]
    )



def create_world_cup_awards_markdown_report(outputs: dict, summary: dict) -> str:
    """Generate markdown report for the broader Step 17 awards system."""
    golden_ball = outputs.get("golden_ball", pd.DataFrame()).head(10)
    golden_boot = outputs.get("golden_boot", pd.DataFrame()).head(10)
    golden_glove = outputs.get("golden_glove", pd.DataFrame()).head(10)
    young_player = outputs.get("young_player", pd.DataFrame()).head(10)
    fair_play = outputs.get("fair_play", pd.DataFrame()).head(10)
    entertaining = outputs.get("most_entertaining", pd.DataFrame()).head(10)
    team_of_tournament = outputs.get("team_of_tournament", pd.DataFrame())
    potm_proxy = outputs.get("player_of_match_proxy", pd.DataFrame()).head(10)
    got_proxy = outputs.get("goal_of_tournament_proxy", pd.DataFrame()).head(10)

    lines = [
        "# FIFA World Cup Awards Predictor Report",
        "",
        "## Methodology",
        f"- {AWARDS_ANALYTICS_DISCLAIMER}",
        "- Player awards combine editable priors, position logic, expected minutes, and Monte Carlo team progression probabilities.",
        "- Team awards combine editable team-award profiles with tournament progression signals and player star-power context.",
        "- Player of the Match and Goal of the Tournament are proxy estimates because this project does not simulate full player-event logs or actual goal quality.",
        "",
        "## Golden Ball podium",
        _dataframe_to_markdown(golden_ball[[c for c in ["golden_ball_rank", "player", "team", "position", "golden_ball_probability", "award_podium"] if c in golden_ball.columns]]) if not golden_ball.empty else "No Golden Ball output available.",
        "",
        "## Golden Boot podium",
        _dataframe_to_markdown(golden_boot[[c for c in ["golden_boot_rank", "player", "team", "position", "expected_goals_score", "boot_podium"] if c in golden_boot.columns]]) if not golden_boot.empty else "No Golden Boot output available.",
        "",
        "## Golden Glove",
        _dataframe_to_markdown(golden_glove[[c for c in ["golden_glove_rank", "player", "team", "golden_glove_probability", "award"] if c in golden_glove.columns]]) if not golden_glove.empty else "No Golden Glove output available.",
        "",
        "## Young Player",
        _dataframe_to_markdown(young_player[[c for c in ["young_player_rank", "player", "team", "position", "young_player_probability", "award"] if c in young_player.columns]]) if not young_player.empty else "No Young Player output available.",
        "",
        "## Fair Play Trophy",
        _dataframe_to_markdown(fair_play[[c for c in ["fair_play_rank", "team", "fair_play_probability", "award"] if c in fair_play.columns]]) if not fair_play.empty else "No Fair Play output available.",
        "",
        "## Most Entertaining Team",
        _dataframe_to_markdown(entertaining[[c for c in ["most_entertaining_rank", "team", "most_entertaining_probability", "award"] if c in entertaining.columns]]) if not entertaining.empty else "No Most Entertaining Team output available.",
        "",
        "## Predicted Team of the Tournament",
        _dataframe_to_markdown(team_of_tournament[[c for c in ["formation_slot", "player", "team", "position"] if c in team_of_tournament.columns]]) if not team_of_tournament.empty else "No Team of the Tournament output available.",
        "",
        "## Player of the Match proxy",
        _dataframe_to_markdown(potm_proxy[[c for c in ["player_of_match_proxy_rank", "player", "team", "estimated_potm_count"] if c in potm_proxy.columns]]) if not potm_proxy.empty else "No Player of the Match proxy output available.",
        "",
        "## Goal of the Tournament proxy",
        _dataframe_to_markdown(got_proxy[[c for c in ["goal_of_tournament_proxy_rank", "player", "team", "goal_of_tournament_proxy_probability"] if c in got_proxy.columns]]) if not got_proxy.empty else "No Goal of the Tournament proxy output available.",
        "",
        "## Limitations",
        "- Manually editable priors may not reflect final squads or current form.",
        "- Monte Carlo probabilities depend on simulation sample size and upstream match model quality.",
        "- No live player-event data or official FIFA judging inputs are used.",
        "- Fan-vote awards are represented as proxy analytics, not actual fan-vote forecasts.",
        "- This is not an official FIFA prediction.",
        "- This is not betting advice.",
        "",
        "## Summary snapshot",
        f"- Top Golden Ball player: {summary.get('top_golden_ball_player', '—')}",
        f"- Top Golden Boot player: {summary.get('top_golden_boot_player', '—')}",
        f"- Top Golden Glove player: {summary.get('top_golden_glove_player', '—')}",
        f"- Top Young Player: {summary.get('top_young_player', '—')}",
        f"- Fair Play team: {summary.get('top_fair_play_team', '—')}",
        f"- Most Entertaining Team: {summary.get('top_entertaining_team', '—')}",
        f"- Team of the Tournament count: {summary.get('team_of_tournament_count', 0)}",
    ]
    return "\n".join(lines)



def save_awards_report(report_text: str, output_path: str | None = None) -> str:
    """Save awards markdown report to reports directory."""
    path = Path(output_path) if output_path else REPORTS_DIR / WORLD_CUP_AWARDS_REPORT_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report_text, encoding="utf-8")
    return str(path)
