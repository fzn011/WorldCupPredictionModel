"""Leakage-safe historical feature helpers for match prediction."""

from __future__ import annotations

import pandas as pd

import src.utils.constants as C

RECENT_FORM_WINDOWS = getattr(C, "RECENT_FORM_WINDOWS", [5, 10])


def get_team_match_history(
    canonical_df: pd.DataFrame,
    team: str,
    before_date: pd.Timestamp,
) -> pd.DataFrame:
    """Return all matches for ``team`` strictly before ``before_date``.

    The match can appear either as ``team_a`` or ``team_b``. The filter is
    strict so same-day matches are excluded, which avoids leakage when several
    fixtures share a date.
    """
    if canonical_df is None or canonical_df.empty or not team:
        return pd.DataFrame(columns=canonical_df.columns if canonical_df is not None else [])

    df = canonical_df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    before_date = pd.Timestamp(before_date)

    mask = (
        (df["date"].notna())
        & (df["date"] < before_date)
        & ((df["team_a"] == team) | (df["team_b"] == team))
    )
    return df.loc[mask].sort_values("date").reset_index(drop=True)


def get_team_perspective_history(
    history_df: pd.DataFrame,
    team: str,
) -> pd.DataFrame:
    """Convert a team's match history into a team-centric perspective.

    Each row is transformed so that goals scored/conceded, result, points and
    derived indicators are measured from ``team``'s point of view.
    """
    if history_df is None or history_df.empty:
        return pd.DataFrame(
            columns=[
                "date",
                "team",
                "opponent",
                "goals_for",
                "goals_against",
                "result_code",
                "points",
                "win",
                "draw",
                "loss",
                "clean_sheet",
                "failed_to_score",
                "goal_diff",
            ]
        )

    df = history_df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    rows: list[dict] = []
    for _, row in df.iterrows():
        if row.get("team_a") == team:
            goals_for = int(row["team_a_score"])
            goals_against = int(row["team_b_score"])
            result_code = int(row["result"])
            opponent = row.get("team_b", "")
        elif row.get("team_b") == team:
            goals_for = int(row["team_b_score"])
            goals_against = int(row["team_a_score"])
            # Invert the canonical team_a-based encoding.
            result_code = 2 if int(row["result"]) == 0 else 0 if int(row["result"]) == 2 else 1
            opponent = row.get("team_a", "")
        else:
            continue

        win = int(goals_for > goals_against)
        draw = int(goals_for == goals_against)
        loss = int(goals_for < goals_against)
        rows.append(
            {
                "date": row["date"],
                "team": team,
                "opponent": opponent,
                "goals_for": goals_for,
                "goals_against": goals_against,
                "result_code": result_code,
                "points": 3 * win + draw,
                "win": win,
                "draw": draw,
                "loss": loss,
                "clean_sheet": int(goals_against == 0),
                "failed_to_score": int(goals_for == 0),
                "goal_diff": goals_for - goals_against,
            }
        )

    return pd.DataFrame(rows)


def _safe_rate(numerator: float, denominator: float) -> float:
    return float(numerator / denominator) if denominator else 0.0


def _empty_history_summary() -> dict[str, float | int]:
    return {
        "matches_played": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "win_rate": 0.0,
        "draw_rate": 0.0,
        "loss_rate": 0.0,
        "points_per_match": 0.0,
        "goals_scored_avg": 0.0,
        "goals_conceded_avg": 0.0,
        "goal_diff_avg": 0.0,
        "clean_sheet_rate": 0.0,
        "failed_to_score_rate": 0.0,
        "unbeaten_rate": 0.0,
    }


def _summarize_history_records(records: list[dict]) -> dict[str, float | int]:
    if not records:
        return _empty_history_summary()

    matches = len(records)
    wins = sum(int(record["win"]) for record in records)
    draws = sum(int(record["draw"]) for record in records)
    losses = sum(int(record["loss"]) for record in records)
    goals_for = [int(record["goals_for"]) for record in records]
    goals_against = [int(record["goals_against"]) for record in records]
    goal_diff = [int(record["goal_diff"]) for record in records]
    points = sum(int(record["points"]) for record in records)
    clean_sheets = sum(int(record["clean_sheet"]) for record in records)
    failed_to_score = sum(int(record["failed_to_score"]) for record in records)

    return {
        "matches_played": matches,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "win_rate": _safe_rate(wins, matches),
        "draw_rate": _safe_rate(draws, matches),
        "loss_rate": _safe_rate(losses, matches),
        "points_per_match": _safe_rate(points, matches),
        "goals_scored_avg": sum(goals_for) / matches,
        "goals_conceded_avg": sum(goals_against) / matches,
        "goal_diff_avg": sum(goal_diff) / matches,
        "clean_sheet_rate": _safe_rate(clean_sheets, matches),
        "failed_to_score_rate": _safe_rate(failed_to_score, matches),
        "unbeaten_rate": _safe_rate(wins + draws, matches),
    }


def _make_team_history_record(row: pd.Series, team: str) -> dict:
    if row["team_a"] == team:
        goals_for = int(row["team_a_score"])
        goals_against = int(row["team_b_score"])
    else:
        goals_for = int(row["team_b_score"])
        goals_against = int(row["team_a_score"])

    win = int(goals_for > goals_against)
    draw = int(goals_for == goals_against)
    loss = int(goals_for < goals_against)
    return {
        "date": row["date"],
        "team": team,
        "goals_for": goals_for,
        "goals_against": goals_against,
        "points": 3 * win + draw,
        "win": win,
        "draw": draw,
        "loss": loss,
        "clean_sheet": int(goals_against == 0),
        "failed_to_score": int(goals_for == 0),
        "goal_diff": goals_for - goals_against,
    }


def _build_feature_map(
    match_row: pd.Series,
    team_a_summary: dict[str, float | int],
    team_b_summary: dict[str, float | int],
    team_a_recent_by_window: dict[int, dict[str, float | int]],
    team_b_recent_by_window: dict[int, dict[str, float | int]],
    windows: list[int],
) -> dict[str, float | int | str]:
    features: dict[str, float | int | str] = {
        "team_a_has_prior_history": int(team_a_summary["matches_played"] > 0),
        "team_b_has_prior_history": int(team_b_summary["matches_played"] > 0),
    }
    features.update(_feature_dict_from_summary("team_a", team_a_summary))
    features.update(_feature_dict_from_summary("team_b", team_b_summary))

    for window in windows:
        a_recent = team_a_recent_by_window[window]
        b_recent = team_b_recent_by_window[window]
        features.update(
            {
                f"team_a_last_{window}_matches_played": a_recent["matches_played"],
                f"team_a_last_{window}_win_rate": a_recent["win_rate"],
                f"team_a_last_{window}_draw_rate": a_recent["draw_rate"],
                f"team_a_last_{window}_loss_rate": a_recent["loss_rate"],
                f"team_a_last_{window}_points_per_match": a_recent["points_per_match"],
                f"team_a_last_{window}_goals_scored_avg": a_recent["goals_scored_avg"],
                f"team_a_last_{window}_goals_conceded_avg": a_recent["goals_conceded_avg"],
                f"team_a_last_{window}_goal_diff_avg": a_recent["goal_diff_avg"],
                f"team_a_last_{window}_clean_sheet_rate": a_recent["clean_sheet_rate"],
                f"team_a_last_{window}_failed_to_score_rate": a_recent["failed_to_score_rate"],
                f"team_a_last_{window}_unbeaten_rate": a_recent["unbeaten_rate"],
                f"team_b_last_{window}_matches_played": b_recent["matches_played"],
                f"team_b_last_{window}_win_rate": b_recent["win_rate"],
                f"team_b_last_{window}_draw_rate": b_recent["draw_rate"],
                f"team_b_last_{window}_loss_rate": b_recent["loss_rate"],
                f"team_b_last_{window}_points_per_match": b_recent["points_per_match"],
                f"team_b_last_{window}_goals_scored_avg": b_recent["goals_scored_avg"],
                f"team_b_last_{window}_goals_conceded_avg": b_recent["goals_conceded_avg"],
                f"team_b_last_{window}_goal_diff_avg": b_recent["goal_diff_avg"],
                f"team_b_last_{window}_clean_sheet_rate": b_recent["clean_sheet_rate"],
                f"team_b_last_{window}_failed_to_score_rate": b_recent["failed_to_score_rate"],
                f"team_b_last_{window}_unbeaten_rate": b_recent["unbeaten_rate"],
                f"diff_last_{window}_win_rate": a_recent["win_rate"] - b_recent["win_rate"],
                f"diff_last_{window}_points_per_match": a_recent["points_per_match"] - b_recent["points_per_match"],
                f"diff_last_{window}_goals_scored_avg": a_recent["goals_scored_avg"] - b_recent["goals_scored_avg"],
                f"diff_last_{window}_goals_conceded_avg": a_recent["goals_conceded_avg"] - b_recent["goals_conceded_avg"],
                f"diff_last_{window}_goal_diff_avg": a_recent["goal_diff_avg"] - b_recent["goal_diff_avg"],
            }
        )

    features.update(
        {
            "diff_matches_played_before": team_a_summary["matches_played"] - team_b_summary["matches_played"],
            "diff_win_rate_before": team_a_summary["win_rate"] - team_b_summary["win_rate"],
            "diff_points_per_match_before": team_a_summary["points_per_match"] - team_b_summary["points_per_match"],
            "diff_goals_scored_avg_before": team_a_summary["goals_scored_avg"] - team_b_summary["goals_scored_avg"],
            "diff_goals_conceded_avg_before": team_a_summary["goals_conceded_avg"] - team_b_summary["goals_conceded_avg"],
            "diff_goal_diff_avg_before": team_a_summary["goal_diff_avg"] - team_b_summary["goal_diff_avg"],
            "diff_clean_sheet_rate_before": team_a_summary["clean_sheet_rate"] - team_b_summary["clean_sheet_rate"],
            "diff_failed_to_score_rate_before": team_a_summary["failed_to_score_rate"] - team_b_summary["failed_to_score_rate"],
            "diff_unbeaten_rate_before": team_a_summary["unbeaten_rate"] - team_b_summary["unbeaten_rate"],
        }
    )
    return features


def summarize_team_history(history_df: pd.DataFrame) -> dict[str, float | int]:
    """Summarize a full team history in team-centric terms."""
    if history_df is None or history_df.empty:
        return {
            "matches_played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "win_rate": 0.0,
            "draw_rate": 0.0,
            "loss_rate": 0.0,
            "points_per_match": 0.0,
            "goals_scored_avg": 0.0,
            "goals_conceded_avg": 0.0,
            "goal_diff_avg": 0.0,
            "clean_sheet_rate": 0.0,
            "failed_to_score_rate": 0.0,
            "unbeaten_rate": 0.0,
        }

    df = history_df.copy()
    matches = len(df)
    wins = int(df["win"].sum())
    draws = int(df["draw"].sum())
    losses = int(df["loss"].sum())
    return {
        "matches_played": matches,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "win_rate": _safe_rate(wins, matches),
        "draw_rate": _safe_rate(draws, matches),
        "loss_rate": _safe_rate(losses, matches),
        "points_per_match": _safe_rate(df["points"].sum(), matches),
        "goals_scored_avg": float(df["goals_for"].mean()),
        "goals_conceded_avg": float(df["goals_against"].mean()),
        "goal_diff_avg": float(df["goal_diff"].mean()),
        "clean_sheet_rate": _safe_rate(df["clean_sheet"].sum(), matches),
        "failed_to_score_rate": _safe_rate(df["failed_to_score"].sum(), matches),
        "unbeaten_rate": _safe_rate(wins + draws, matches),
    }


def summarize_recent_form(
    history_df: pd.DataFrame,
    window: int,
) -> dict[str, float | int]:
    """Summarize the most recent ``window`` matches from a team history."""
    if history_df is None or history_df.empty:
        return summarize_team_history(history_df)

    recent = history_df.sort_values("date").tail(window).reset_index(drop=True)
    summary = summarize_team_history(recent)
    summary["matches_played"] = len(recent)
    return summary


def _feature_dict_from_summary(prefix: str, summary: dict[str, float | int]) -> dict[str, float | int]:
    return {
        f"{prefix}_matches_played_before": summary["matches_played"],
        f"{prefix}_wins_before": summary["wins"],
        f"{prefix}_draws_before": summary["draws"],
        f"{prefix}_losses_before": summary["losses"],
        f"{prefix}_win_rate_before": summary["win_rate"],
        f"{prefix}_draw_rate_before": summary["draw_rate"],
        f"{prefix}_loss_rate_before": summary["loss_rate"],
        f"{prefix}_points_per_match_before": summary["points_per_match"],
        f"{prefix}_goals_scored_avg_before": summary["goals_scored_avg"],
        f"{prefix}_goals_conceded_avg_before": summary["goals_conceded_avg"],
        f"{prefix}_goal_diff_avg_before": summary["goal_diff_avg"],
        f"{prefix}_clean_sheet_rate_before": summary["clean_sheet_rate"],
        f"{prefix}_failed_to_score_rate_before": summary["failed_to_score_rate"],
        f"{prefix}_unbeaten_rate_before": summary["unbeaten_rate"],
    }


def build_historical_features_for_match(
    match_row: pd.Series,
    canonical_df: pd.DataFrame,
    windows: list[int] | None = None,
) -> dict[str, float | int | str]:
    """Build leakage-safe historical features for a single match row."""
    windows = windows or RECENT_FORM_WINDOWS
    match_date = pd.Timestamp(match_row["date"])
    team_a = match_row["team_a"]
    team_b = match_row["team_b"]

    team_a_history_raw = get_team_match_history(canonical_df, team_a, match_date)
    team_b_history_raw = get_team_match_history(canonical_df, team_b, match_date)
    team_a_history = get_team_perspective_history(team_a_history_raw, team_a)
    team_b_history = get_team_perspective_history(team_b_history_raw, team_b)

    team_a_summary = summarize_team_history(team_a_history)
    team_b_summary = summarize_team_history(team_b_history)
    team_a_recent_by_window = {window: summarize_recent_form(team_a_history, window) for window in windows}
    team_b_recent_by_window = {window: summarize_recent_form(team_b_history, window) for window in windows}
    return _build_feature_map(
        match_row,
        team_a_summary,
        team_b_summary,
        team_a_recent_by_window,
        team_b_recent_by_window,
        windows,
    )


def build_historical_feature_dataset(
    canonical_df: pd.DataFrame,
    windows: list[int] | None = None,
    min_year: int | None = None,
) -> pd.DataFrame:
    """Build a leakage-safe feature dataset from canonical matches.

    Matches are processed in date order. For each match, features are computed
    from the already-seen history only. When ``min_year`` is provided, rows
    before that year are excluded from the output but still contribute to the
    history used by later matches.
    """
    if canonical_df is None or canonical_df.empty:
        return pd.DataFrame()

    windows = windows or RECENT_FORM_WINDOWS
    df = canonical_df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["year"] = pd.to_numeric(df.get("year"), errors="coerce")
    df = df.sort_values(["date", "match_id"]).reset_index(drop=True)

    histories: dict[str, list[dict]] = {}
    output_rows: list[dict] = []

    for match_date, batch in df.groupby("date", sort=True):
        batch = batch.sort_values("match_id")
        batch_records: list[dict[str, object]] = []

        for _, row in batch.iterrows():
            team_a = row["team_a"]
            team_b = row["team_b"]
            team_a_records = histories.get(team_a, [])
            team_b_records = histories.get(team_b, [])

            team_a_summary = _summarize_history_records(team_a_records)
            team_b_summary = _summarize_history_records(team_b_records)
            team_a_recent_by_window = {
                window: _summarize_history_records(team_a_records[-window:])
                for window in windows
            }
            team_b_recent_by_window = {
                window: _summarize_history_records(team_b_records[-window:])
                for window in windows
            }

            feature_map = _build_feature_map(
                row,
                team_a_summary,
                team_b_summary,
                team_a_recent_by_window,
                team_b_recent_by_window,
                windows,
            )
            row_dict = row.to_dict()
            row_dict.update(feature_map)

            year_value = row_dict.get("year")
            if min_year is None or (pd.notna(year_value) and int(year_value) >= min_year):
                batch_records.append(row_dict)

        # Update histories only after the whole date batch has been scored.
        for _, row in batch.iterrows():
            team_a = row["team_a"]
            team_b = row["team_b"]
            histories.setdefault(team_a, []).append(_make_team_history_record(row, team_a))
            histories.setdefault(team_b, []).append(_make_team_history_record(row, team_b))

        output_rows.extend(batch_records)

    return pd.DataFrame(output_rows).reset_index(drop=True)
