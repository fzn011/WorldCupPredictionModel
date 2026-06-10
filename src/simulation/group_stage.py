"""Step 12 group-stage simulation engine."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.models.predict_match import predict_future_match
from src.tournament.fixtures import load_tournament_fixtures
import src.utils.constants as C

TOURNAMENT_STAGE_GROUP = getattr(C, "TOURNAMENT_STAGE_GROUP", "group_stage")
WC2026_TOTAL_GROUP_MATCHES = getattr(C, "WC2026_TOTAL_GROUP_MATCHES", 72)
WC2026_GROUP_MATCHES_PER_GROUP = getattr(C, "WC2026_GROUP_MATCHES_PER_GROUP", 6)
WC2026_TOTAL_TEAMS = getattr(C, "WC2026_TOTAL_TEAMS", 48)
WC2026_QUALIFIED_FROM_GROUP_TOP_N = getattr(C, "WC2026_QUALIFIED_FROM_GROUP_TOP_N", 2)
WC2026_BEST_THIRD_PLACED_QUALIFIERS = getattr(C, "WC2026_BEST_THIRD_PLACED_QUALIFIERS", 8)
SCORELINE_TEMPLATES = getattr(C, "SCORELINE_TEMPLATES", {
    "team_a_win": [(1, 0), (2, 0), (2, 1), (3, 1), (3, 2)],
    "draw": [(0, 0), (1, 1), (2, 2)],
    "team_a_loss": [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)],
})
GROUP_TABLE_COLUMNS = getattr(C, "GROUP_TABLE_COLUMNS", [
    "group",
    "team",
    "played",
    "wins",
    "draws",
    "losses",
    "goals_for",
    "goals_against",
    "goal_difference",
    "points",
    "group_rank",
])

RESULT_KEYS = ["team_a_loss", "draw", "team_a_win"]


def normalize_probabilities(probabilities: dict) -> dict[str, float]:
    """Normalize result probabilities to valid distribution across known keys."""
    values: dict[str, float] = {}
    for key in RESULT_KEYS:
        raw_value = probabilities.get(key, 0.0) if isinstance(probabilities, dict) else 0.0
        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            value = 0.0
        if not np.isfinite(value) or value < 0:
            value = 0.0
        values[key] = value

    total = sum(values.values())
    if total <= 0:
        return {key: 1.0 / 3.0 for key in RESULT_KEYS}

    return {key: values[key] / total for key in RESULT_KEYS}


def sample_match_result(
    probabilities: dict,
    rng: np.random.Generator | None = None,
) -> str:
    """Sample a match result label from normalized probabilities."""
    rng = rng or np.random.default_rng()
    p = normalize_probabilities(probabilities)
    return str(rng.choice(RESULT_KEYS, p=[p[k] for k in RESULT_KEYS]))


def sample_scoreline(
    result_label: str,
    rng: np.random.Generator | None = None,
) -> tuple[int, int]:
    """Sample a transparent approximate scoreline from templates."""
    rng = rng or np.random.default_rng()
    templates = SCORELINE_TEMPLATES.get(result_label, SCORELINE_TEMPLATES.get("draw", [(1, 1)]))
    idx = int(rng.integers(0, len(templates)))
    a_score, b_score = templates[idx]
    return int(a_score), int(b_score)


def simulate_group_match(
    fixture_row: pd.Series,
    random_seed: int | None = None,
    rng: np.random.Generator | None = None,
    predictor: Any | None = None,
) -> dict[str, Any]:
    """Simulate one group-stage fixture using prediction probabilities + sampling."""
    if rng is None:
        rng = np.random.default_rng(random_seed)

    team_a = str(fixture_row.get("team_a", ""))
    team_b = str(fixture_row.get("team_b", ""))
    match_date = str(fixture_row.get("date", C.DEFAULT_FUTURE_MATCH_DATE))
    tournament = str(fixture_row.get("tournament", C.DEFAULT_FUTURE_TOURNAMENT))
    city = str(fixture_row.get("city", C.DEFAULT_FUTURE_CITY))
    country = str(fixture_row.get("country", C.DEFAULT_FUTURE_COUNTRY))
    neutral = int(pd.to_numeric(pd.Series([fixture_row.get("neutral", C.DEFAULT_FUTURE_NEUTRAL)]), errors="coerce").fillna(C.DEFAULT_FUTURE_NEUTRAL).iloc[0])

    model_type = "unknown"
    prediction_error = ""

    try:
        if predictor is not None:
            prediction = predictor.predict(
                team_a=team_a,
                team_b=team_b,
                match_date=match_date,
                tournament=tournament,
                city=city,
                country=country,
                neutral=neutral,
            )
        else:
            prediction = predict_future_match(
                team_a=team_a,
                team_b=team_b,
                match_date=match_date,
                tournament=tournament,
                city=city,
                country=country,
                neutral=neutral,
            )
        probabilities = normalize_probabilities(prediction.get("probabilities", {}))
        model_type = str(prediction.get("model_type", "unknown"))
    except Exception as exc:  # pragma: no cover - resiliency path
        probabilities = normalize_probabilities({})
        prediction_error = str(exc)

    simulated_result = sample_match_result(probabilities, rng=rng)
    team_a_score, team_b_score = sample_scoreline(simulated_result, rng=rng)

    if team_a_score > team_b_score:
        winner = team_a
        is_draw = 0
        points_team_a, points_team_b = 3, 0
    elif team_b_score > team_a_score:
        winner = team_b
        is_draw = 0
        points_team_a, points_team_b = 0, 3
    else:
        winner = "draw"
        is_draw = 1
        points_team_a, points_team_b = 1, 1

    return {
        "match_id": fixture_row.get("match_id"),
        "group": fixture_row.get("group"),
        "matchday": fixture_row.get("matchday"),
        "date": match_date,
        "team_a": team_a,
        "team_b": team_b,
        "model_type": model_type,
        "team_a_loss_probability": probabilities["team_a_loss"],
        "draw_probability": probabilities["draw"],
        "team_a_win_probability": probabilities["team_a_win"],
        "simulated_result": simulated_result,
        "team_a_score": team_a_score,
        "team_b_score": team_b_score,
        "winner": winner,
        "is_draw": is_draw,
        "points_team_a": points_team_a,
        "points_team_b": points_team_b,
        "prediction_error": prediction_error,
    }


def simulate_group_stage(
    fixtures_df: pd.DataFrame | None = None,
    random_seed: int = 42,
    predictor: Any | None = None,
) -> pd.DataFrame:
    """Simulate all group-stage fixtures and return a 72-row DataFrame for full setup."""
    if fixtures_df is None:
        fixtures_df = load_tournament_fixtures()

    group_fixtures = fixtures_df.loc[fixtures_df["stage"] == TOURNAMENT_STAGE_GROUP].copy()
    group_fixtures = group_fixtures.sort_values(["group", "matchday", "match_id"]).reset_index(drop=True)

    rng = np.random.default_rng(random_seed)
    rows = [simulate_group_match(row, rng=rng, predictor=predictor) for _, row in group_fixtures.iterrows()]
    return pd.DataFrame(rows)


def build_group_tables(simulated_matches_df: pd.DataFrame) -> pd.DataFrame:
    """Build unranked group tables from simulated group-stage matches."""
    records: dict[tuple[str, str], dict[str, Any]] = {}

    def _ensure(group: str, team: str) -> None:
        key = (group, team)
        if key not in records:
            records[key] = {
                "group": group,
                "team": team,
                "played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "goals_for": 0,
                "goals_against": 0,
                "goal_difference": 0,
                "points": 0,
                "group_rank": np.nan,
            }

    for _, row in simulated_matches_df.iterrows():
        group = str(row["group"])
        team_a = str(row["team_a"])
        team_b = str(row["team_b"])
        a_score = int(row["team_a_score"])
        b_score = int(row["team_b_score"])

        _ensure(group, team_a)
        _ensure(group, team_b)

        a = records[(group, team_a)]
        b = records[(group, team_b)]

        a["played"] += 1
        b["played"] += 1

        a["goals_for"] += a_score
        a["goals_against"] += b_score
        b["goals_for"] += b_score
        b["goals_against"] += a_score

        if a_score > b_score:
            a["wins"] += 1
            a["points"] += 3
            b["losses"] += 1
        elif b_score > a_score:
            b["wins"] += 1
            b["points"] += 3
            a["losses"] += 1
        else:
            a["draws"] += 1
            b["draws"] += 1
            a["points"] += 1
            b["points"] += 1

    table = pd.DataFrame(list(records.values()))
    if table.empty:
        return pd.DataFrame(columns=GROUP_TABLE_COLUMNS)

    table["goal_difference"] = table["goals_for"] - table["goals_against"]
    return table[GROUP_TABLE_COLUMNS]


def rank_group_tables(group_tables_df: pd.DataFrame) -> pd.DataFrame:
    """Rank each group by points, GD, GF, wins, then team name."""
    if group_tables_df.empty:
        return group_tables_df.copy()

    ranked = group_tables_df.copy()
    ranked = ranked.sort_values(
        ["group", "points", "goal_difference", "goals_for", "wins", "team"],
        ascending=[True, False, False, False, False, True],
    )
    ranked["group_rank"] = ranked.groupby("group").cumcount() + 1
    return ranked.reset_index(drop=True)


def select_group_qualifiers(
    ranked_tables_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Select top-two automatic qualifiers and best eight third-placed teams."""
    auto = ranked_tables_df.loc[ranked_tables_df["group_rank"] <= WC2026_QUALIFIED_FROM_GROUP_TOP_N].copy()
    auto["qualification_type"] = "automatic_top_two"

    thirds = ranked_tables_df.loc[ranked_tables_df["group_rank"] == 3].copy()
    thirds = thirds.sort_values(
        ["points", "goal_difference", "goals_for", "wins", "team"],
        ascending=[False, False, False, False, True],
    ).reset_index(drop=True)
    best_third = thirds.head(WC2026_BEST_THIRD_PLACED_QUALIFIERS).copy()
    best_third["qualification_type"] = "best_third_place"

    qualifiers = pd.concat([auto, best_third], ignore_index=True)
    qualifiers = qualifiers.sort_values(["qualification_type", "group", "group_rank", "team"]).reset_index(drop=True)
    return auto, best_third, qualifiers


def validate_group_stage_simulation(
    simulated_matches_df: pd.DataFrame,
    ranked_tables_df: pd.DataFrame,
    qualifiers_df: pd.DataFrame,
) -> tuple[bool, pd.DataFrame]:
    """Validate key Step 12 simulation outputs and counts."""
    checks: list[dict[str, Any]] = []

    def _add(check: str, expected: Any, actual: Any, passed: bool) -> None:
        checks.append({"check": check, "expected": expected, "actual": actual, "passed": bool(passed)})

    group_matches = simulated_matches_df.groupby("group")["match_id"].count().to_dict() if not simulated_matches_df.empty else {}

    _add(
        "simulated_matches_count",
        WC2026_TOTAL_GROUP_MATCHES,
        int(len(simulated_matches_df)),
        int(len(simulated_matches_df)) == WC2026_TOTAL_GROUP_MATCHES,
    )
    _add(
        "matches_per_group",
        WC2026_GROUP_MATCHES_PER_GROUP,
        group_matches,
        bool(group_matches) and all(v == WC2026_GROUP_MATCHES_PER_GROUP for v in group_matches.values()),
    )

    team_games = pd.concat(
        [
            simulated_matches_df[["group", "team_a"]].rename(columns={"team_a": "team"}),
            simulated_matches_df[["group", "team_b"]].rename(columns={"team_b": "team"}),
        ],
        ignore_index=True,
    ) if not simulated_matches_df.empty else pd.DataFrame(columns=["group", "team"])
    team_game_counts = team_games.groupby(["group", "team"]).size().tolist() if not team_games.empty else []
    _add(
        "team_games_count_equals_3",
        3,
        "all teams play 3" if team_game_counts and all(v == 3 for v in team_game_counts) else str(team_game_counts[:8]),
        bool(team_game_counts) and all(v == 3 for v in team_game_counts),
    )

    _add(
        "group_table_team_count",
        WC2026_TOTAL_TEAMS,
        int(len(ranked_tables_df)),
        int(len(ranked_tables_df)) == WC2026_TOTAL_TEAMS,
    )

    ranks_ok = ranked_tables_df.groupby("group")["group_rank"].apply(lambda s: sorted(s.tolist()) == [1, 2, 3, 4]).all() if not ranked_tables_df.empty else False
    _add("group_ranks_1_to_4", "[1,2,3,4] per group", bool(ranks_ok), bool(ranks_ok))

    auto_count = int((qualifiers_df["qualification_type"] == "automatic_top_two").sum()) if not qualifiers_df.empty else 0
    best_third_count = int((qualifiers_df["qualification_type"] == "best_third_place").sum()) if not qualifiers_df.empty else 0

    _add("automatic_qualifiers_count", 24, auto_count, auto_count == 24)
    _add("best_third_count", 8, best_third_count, best_third_count == 8)
    _add("round_of_32_qualifiers_count", 32, int(len(qualifiers_df)), int(len(qualifiers_df)) == 32)

    report_df = pd.DataFrame(checks)
    return bool(report_df["passed"].all()), report_df


def create_group_stage_summary(
    simulated_matches_df: pd.DataFrame,
    ranked_tables_df: pd.DataFrame,
    automatic_qualifiers_df: pd.DataFrame,
    best_third_df: pd.DataFrame,
    qualifiers_df: pd.DataFrame,
    validation_passed: bool,
    random_seed: int = 42,
) -> dict[str, Any]:
    """Create Step 12 summary payload for scripts/UI and artifact persistence."""
    return {
        "status": "ok" if validation_passed else "validation_failed",
        "validation_passed": bool(validation_passed),
        "simulated_matches": int(len(simulated_matches_df)),
        "groups": int(ranked_tables_df["group"].nunique()) if not ranked_tables_df.empty else 0,
        "teams": int(len(ranked_tables_df)),
        "automatic_qualifiers": int(len(automatic_qualifiers_df)),
        "best_third_placed_qualifiers": int(len(best_third_df)),
        "round_of_32_qualifiers": int(len(qualifiers_df)),
        "highest_points": int(ranked_tables_df["points"].max()) if not ranked_tables_df.empty else 0,
        "lowest_points": int(ranked_tables_df["points"].min()) if not ranked_tables_df.empty else 0,
        "random_seed": int(random_seed),
        "notes": [
            "Step 12 simulates group stage only.",
            "Scoreline generation is a transparent approximation for table metrics.",
            "Knockout simulation starts in a later step.",
        ],
    }
