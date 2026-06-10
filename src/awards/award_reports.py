"""Reporting utilities for Step 18 World Cup awards analytics."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C
from src.awards.award_data import resolve_player_sort_column

PROJECT_ROOT = C.PROJECT_ROOT
REPORTS_DIR = PROJECT_ROOT / C.AWARDS_REPORT_DIR
AWARDS_ANALYTICS_DISCLAIMER = C.AWARDS_ANALYTICS_DISCLAIMER


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
        return "_No data available._"
    headers = [str(column) for column in df.columns]
    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"
    data_rows = [
        "| " + " | ".join(_format_markdown_value(v) for v in row) + " |"
        for row in df.itertuples(index=False, name=None)
    ]
    return "\n".join([header_row, separator_row, *data_rows])


def _player_col(df: pd.DataFrame) -> str | None:
    if df.empty:
        return None
    try:
        return resolve_player_sort_column(df)
    except KeyError:
        return None


def _top_value(df: pd.DataFrame, column: str) -> str:
    if df.empty or column not in df.columns:
        return "—"
    return str(df.iloc[0][column])


def create_world_cup_awards_summary(outputs: dict, validation_passed: bool) -> dict[str, Any]:
    """Create compact summary for Step 18 awards outputs."""
    golden_ball = outputs.get("golden_ball", pd.DataFrame())
    return {
        "status": "ok" if validation_passed else "validation_failed",
        "validation_passed": bool(validation_passed),
        "top_golden_ball_player": _top_value(golden_ball, _player_col(golden_ball)),
        "top_golden_boot_player": _top_value(outputs.get("golden_boot", pd.DataFrame()), _player_col(outputs.get("golden_boot", pd.DataFrame()))),
        "top_golden_glove_player": _top_value(outputs.get("golden_glove", pd.DataFrame()), _player_col(outputs.get("golden_glove", pd.DataFrame()))),
        "top_young_player": _top_value(outputs.get("young_player", pd.DataFrame()), _player_col(outputs.get("young_player", pd.DataFrame()))),
        "top_fair_play_team": _top_value(outputs.get("fair_play", pd.DataFrame()), "team"),
        "top_entertaining_team": _top_value(outputs.get("most_entertaining", pd.DataFrame()), "team"),
        "team_of_tournament_count": int(len(outputs.get("team_of_tournament", pd.DataFrame()))),
        "notes": AWARDS_ANALYTICS_DISCLAIMER,
    }


def create_combined_awards_table(outputs: dict) -> pd.DataFrame:
    """Create long-format combined awards table."""
    frames: list[pd.DataFrame] = []
    mapping: list[tuple[str, str, str, str, str]] = [
        ("golden_ball", "award", "golden_ball_rank", "final_golden_ball_score", "golden_ball_probability"),
        ("golden_boot", "award", "golden_boot_rank", "boot_tiebreak_score", "golden_boot_probability"),
        ("golden_glove", "award", "golden_glove_rank", "golden_glove_score", "golden_glove_probability"),
        ("young_player", "award", "young_player_rank", "young_player_score", "young_player_probability"),
        ("fair_play", "award", "fair_play_rank", "fair_play_score", "fair_play_probability"),
        ("most_entertaining", "award", "most_entertaining_rank", "most_entertaining_score", "most_entertaining_probability"),
        ("player_of_match_proxy", "player_of_match_proxy_rank", "player_of_match_proxy_rank", "estimated_potm_count", "player_impact_share"),
        ("goal_of_tournament_proxy", "goal_of_tournament_proxy_rank", "goal_of_tournament_proxy_rank", "goal_of_tournament_proxy_score", "goal_of_tournament_proxy_probability"),
    ]

    for key, award_col, rank_col, score_col, prob_col in mapping:
        df = outputs.get(key, pd.DataFrame())
        if df.empty:
            continue
        pname = _player_col(df)
        player_values = df[pname] if pname and pname in df.columns else ""
        pos = df.get("position_group", df.get("position", pd.Series("", index=df.index)))
        frames.append(
            pd.DataFrame(
                {
                    "award_category": key,
                    "rank": df[rank_col] if rank_col in df.columns else range(1, len(df) + 1),
                    "award": df[award_col] if award_col in df.columns else "",
                    "player_id": df.get("player_id", ""),
                    "player_name": player_values,
                    "player": player_values,
                    "team": df.get("team", ""),
                    "position": pos,
                    "position_code": df.get("position_code", ""),
                    "score": df[score_col] if score_col in df.columns else 0.0,
                    "probability": df[prob_col] if prob_col in df.columns else 0.0,
                    "notes": "proxy estimate" if "proxy" in key else "analytics estimate",
                }
            )
        )

    team_df = outputs.get("team_of_tournament", pd.DataFrame())
    if not team_df.empty:
        pname = _player_col(team_df)
        player_values = team_df[pname] if pname and pname in team_df.columns else ""
        frames.append(
            pd.DataFrame(
                {
                    "award_category": "team_of_tournament",
                    "rank": range(1, len(team_df) + 1),
                    "award": team_df.get("award", "Predicted Team of the Tournament"),
                    "player_id": team_df.get("player_id", ""),
                    "player_name": player_values,
                    "player": player_values,
                    "team": team_df.get("team", ""),
                    "position": team_df.get("position", ""),
                    "position_code": team_df.get("position_code", ""),
                    "score": team_df.get("final_golden_ball_score", 0.0),
                    "probability": team_df.get("golden_ball_probability", 0.0),
                    "notes": "unofficial analytics XI",
                }
            )
        )

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(
        columns=[
            "award_category",
            "rank",
            "award",
            "player_id",
            "player_name",
            "team",
            "position",
            "position_code",
            "score",
            "probability",
            "notes",
        ]
    )


def create_world_cup_awards_markdown_report(
    outputs: dict,
    summary: dict,
    readiness: dict | None = None,
) -> str:
    """Generate markdown report for Step 18 awards."""
    golden_ball = outputs.get("golden_ball", pd.DataFrame()).head(10)
    golden_boot = outputs.get("golden_boot", pd.DataFrame()).head(10)
    golden_glove = outputs.get("golden_glove", pd.DataFrame()).head(10)
    young_player = outputs.get("young_player", pd.DataFrame()).head(10)
    fair_play = outputs.get("fair_play", pd.DataFrame()).head(10)
    entertaining = outputs.get("most_entertaining", pd.DataFrame()).head(10)
    team_of_tournament = outputs.get("team_of_tournament", pd.DataFrame())
    potm_proxy = outputs.get("player_of_match_proxy", pd.DataFrame()).head(10)
    got_proxy = outputs.get("goal_of_tournament_proxy", pd.DataFrame()).head(10)
    pname = _player_col(golden_ball) if not golden_ball.empty else "player_name"

    lines = [
        "# FIFA World Cup 2026 Awards Predictor Report",
        "",
        "## Official data status",
        f"- official_final_enabled: {summary.get('official_final_enabled', readiness.get('official_final_enabled') if readiness else False)}",
        f"- final_ready: {readiness.get('final_ready', True) if readiness else True}",
        "",
        "## Methodology",
        f"- {AWARDS_ANALYTICS_DISCLAIMER}",
        "- Player awards combine official squad priors, position logic, expected minutes, and Monte Carlo team progression.",
        "- Team awards combine official team profiles with tournament progression and squad star-power context.",
        "- Player of the Match and Goal of the Tournament are proxy estimates (no match-level player-event simulation).",
        "",
        "## Golden Ball podium",
        _dataframe_to_markdown(golden_ball[[c for c in [pname, "team", "position_code", "golden_ball_probability", "award"] if c in golden_ball.columns]]),
        "",
        "## Golden Boot podium",
        _dataframe_to_markdown(golden_boot[[c for c in [pname, "team", "expected_goals", "award"] if c in golden_boot.columns]]),
        "",
        "## Golden Glove",
        _dataframe_to_markdown(golden_glove[[c for c in [pname, "team", "golden_glove_probability", "award"] if c in golden_glove.columns]]),
        "",
        "## Young Player",
        _dataframe_to_markdown(young_player[[c for c in [pname, "team", "young_player_probability", "award"] if c in young_player.columns]] if not young_player.empty else pd.DataFrame()),
        "",
        "## Fair Play Trophy",
        _dataframe_to_markdown(fair_play[[c for c in ["team", "fair_play_probability", "award"] if c in fair_play.columns]]),
        "",
        "## Most Entertaining Team",
        _dataframe_to_markdown(entertaining[[c for c in ["team", "most_entertaining_probability", "award"] if c in entertaining.columns]]),
        "",
        "## Predicted Team of the Tournament",
        _dataframe_to_markdown(team_of_tournament[[c for c in ["formation_slot", "player_name", "team", "position_code"] if c in team_of_tournament.columns]]),
        "",
        "## Player of the Match proxy",
        _dataframe_to_markdown(potm_proxy[[c for c in [pname, "team", "estimated_potm_count"] if c in potm_proxy.columns]]),
        "",
        "## Goal of the Tournament proxy",
        _dataframe_to_markdown(got_proxy[[c for c in [pname, "team", "goal_of_tournament_proxy_probability"] if c in got_proxy.columns]]),
        "",
        "## Limitations",
        "- Analytics estimate only; not an official FIFA prediction.",
        "- Depends on Monte Carlo sample size and upstream match model quality.",
        "- Depends on editable player priors and conservative team profile defaults.",
        "- Fan-voted style awards are proxy analytics, not fan-vote forecasts.",
        "- No match-level player event simulation or actual goal-quality modeling.",
        "- No betting advice.",
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


def save_world_cup_awards_report(report_text: str, output_path: str | None = None) -> str:
    """Save awards markdown report."""
    path = Path(output_path) if output_path else REPORTS_DIR / C.WORLD_CUP_AWARDS_REPORT_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report_text, encoding="utf-8")
    return str(path)


def save_awards_report(report_text: str, output_path: str | None = None) -> str:
    """Backward-compatible alias."""
    return save_world_cup_awards_report(report_text, output_path)
