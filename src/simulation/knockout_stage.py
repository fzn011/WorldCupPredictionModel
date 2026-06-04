"""Step 13 knockout simulation engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.models.predict_match import predict_future_match
from src.simulation.prepare_group_stage import prepare_step12_group_stage_simulation
import src.utils.constants as C

PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")
ROUND_OF_32_QUALIFIERS_FILE = getattr(C, "ROUND_OF_32_QUALIFIERS_FILE", "round_of_32_qualifiers.csv")
KNOCKOUT_BRACKET_FILLED_FILE = getattr(C, "KNOCKOUT_BRACKET_FILLED_FILE", "knockout_bracket_filled.csv")
KNOCKOUT_SIMULATED_MATCHES_FILE = getattr(C, "KNOCKOUT_SIMULATED_MATCHES_FILE", "knockout_simulated_matches.csv")
SINGLE_TOURNAMENT_RESULT_FILE = getattr(C, "SINGLE_TOURNAMENT_RESULT_FILE", "single_tournament_result.json")
KNOCKOUT_SIMULATION_SUMMARY_FILE = getattr(C, "KNOCKOUT_SIMULATION_SUMMARY_FILE", "knockout_simulation_summary.json")
KNOCKOUT_SIMULATION_VALIDATION_REPORT_FILE = getattr(
    C,
    "KNOCKOUT_SIMULATION_VALIDATION_REPORT_FILE",
    "knockout_simulation_validation_report.csv",
)

KNOCKOUT_ROUNDS = getattr(
    C,
    "KNOCKOUT_ROUNDS",
    ["round_of_32", "round_of_16", "quarter_final", "semi_final", "third_place", "final"],
)
KNOCKOUT_ROUND_MATCH_COUNTS = getattr(
    C,
    "KNOCKOUT_ROUND_MATCH_COUNTS",
    {
        "round_of_32": 16,
        "round_of_16": 8,
        "quarter_final": 4,
        "semi_final": 2,
        "third_place": 1,
        "final": 1,
    },
)
KNOCKOUT_SCORELINE_TEMPLATES = getattr(
    C,
    "KNOCKOUT_SCORELINE_TEMPLATES",
    {
        "team_a_win_regular": [(1, 0), (2, 0), (2, 1), (3, 1), (3, 2)],
        "team_b_win_regular": [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)],
        "team_a_win_extra": [(1, 1), (2, 2), (0, 0)],
        "team_b_win_extra": [(1, 1), (2, 2), (0, 0)],
    },
)

TOURNAMENT_STAGE_ROUND_OF_32 = getattr(C, "TOURNAMENT_STAGE_ROUND_OF_32", "round_of_32")
TOURNAMENT_STAGE_ROUND_OF_16 = getattr(C, "TOURNAMENT_STAGE_ROUND_OF_16", "round_of_16")
TOURNAMENT_STAGE_QUARTER_FINAL = getattr(C, "TOURNAMENT_STAGE_QUARTER_FINAL", "quarter_final")
TOURNAMENT_STAGE_SEMI_FINAL = getattr(C, "TOURNAMENT_STAGE_SEMI_FINAL", "semi_final")
TOURNAMENT_STAGE_THIRD_PLACE = getattr(C, "TOURNAMENT_STAGE_THIRD_PLACE", "third_place")
TOURNAMENT_STAGE_FINAL = getattr(C, "TOURNAMENT_STAGE_FINAL", "final")

ROUND_DATE_MAP: dict[str, str] = {
    TOURNAMENT_STAGE_ROUND_OF_32: "2026-06-28",
    TOURNAMENT_STAGE_ROUND_OF_16: "2026-07-03",
    TOURNAMENT_STAGE_QUARTER_FINAL: "2026-07-09",
    TOURNAMENT_STAGE_SEMI_FINAL: "2026-07-14",
    TOURNAMENT_STAGE_THIRD_PLACE: "2026-07-18",
    TOURNAMENT_STAGE_FINAL: "2026-07-19",
}

ROUND_OF_32_PAIRINGS: list[tuple[int, int]] = [
    (1, 32),
    (16, 17),
    (8, 25),
    (9, 24),
    (4, 29),
    (13, 20),
    (5, 28),
    (12, 21),
    (2, 31),
    (15, 18),
    (7, 26),
    (10, 23),
    (3, 30),
    (14, 19),
    (6, 27),
    (11, 22),
]

QUALIFICATION_TYPE_ORDER = {
    "automatic_top_two": 0,
    "best_third_place": 1,
}


def _coerce_rng(
    random_seed: int | None = None,
    rng: np.random.Generator | None = None,
) -> np.random.Generator:
    if rng is not None:
        return rng
    return np.random.default_rng(random_seed)


def _normalise_probabilities(probabilities: dict[str, Any]) -> dict[str, float]:
    values = {
        "team_a_loss": max(0.0, float(probabilities.get("team_a_loss", 0.0) or 0.0)),
        "draw": max(0.0, float(probabilities.get("draw", 0.0) or 0.0)),
        "team_a_win": max(0.0, float(probabilities.get("team_a_win", 0.0) or 0.0)),
    }
    total = sum(values.values())
    if total <= 0:
        return {key: 1.0 / 3.0 for key in values}
    return {key: value / total for key, value in values.items()}


def _sample_label(labels: list[str], probabilities: list[float], rng: np.random.Generator) -> str:
    probabilities = [max(0.0, float(value)) for value in probabilities]
    total = sum(probabilities)
    if total <= 0:
        probabilities = [1.0 / len(labels)] * len(labels)
    else:
        probabilities = [value / total for value in probabilities]
    index = int(rng.choice(len(labels), p=probabilities))
    return labels[index]


def _round_date(round_name: str) -> str:
    return ROUND_DATE_MAP.get(round_name, "2026-07-19")


def _round_prefix(round_name: str) -> str:
    return {
        TOURNAMENT_STAGE_ROUND_OF_32: "R32",
        TOURNAMENT_STAGE_ROUND_OF_16: "R16",
        TOURNAMENT_STAGE_QUARTER_FINAL: "QF",
        TOURNAMENT_STAGE_SEMI_FINAL: "SF",
        TOURNAMENT_STAGE_THIRD_PLACE: "TP",
        TOURNAMENT_STAGE_FINAL: "F",
    }.get(round_name, "R")


def load_round_of_32_qualifiers(path: str | None = None) -> pd.DataFrame:
    """Load the Step 12 Round-of-32 qualifiers, generating them if needed."""
    candidate = Path(path) if path else PROCESSED_DATA_DIR / ROUND_OF_32_QUALIFIERS_FILE
    if not candidate.is_file():
        prepare_step12_group_stage_simulation()
        candidate = PROCESSED_DATA_DIR / ROUND_OF_32_QUALIFIERS_FILE
        if not candidate.is_file():
            raise FileNotFoundError(
                f"Round-of-32 qualifiers not found at {candidate}. Run Step 12 first."
            )

    qualifiers_df = pd.read_csv(candidate)
    if "team" not in qualifiers_df.columns:
        raise ValueError("Round-of-32 qualifiers must contain a 'team' column.")
    if len(qualifiers_df) != 32:
        raise ValueError(
            f"Round-of-32 qualifiers must contain exactly 32 rows, found {len(qualifiers_df)}."
        )
    return qualifiers_df


def assign_knockout_seeds(qualifiers_df: pd.DataFrame) -> pd.DataFrame:
    """Assign deterministic simulation seeds to the 32 qualifiers."""
    if "team" not in qualifiers_df.columns:
        raise ValueError("qualifiers_df must contain a 'team' column.")

    seeded = qualifiers_df.copy()
    if "qualification_type" not in seeded.columns:
        seeded["qualification_type"] = "automatic_top_two"
    if "group_rank" not in seeded.columns:
        seeded["group_rank"] = 0
    if "points" not in seeded.columns:
        seeded["points"] = 0
    if "goal_difference" not in seeded.columns:
        seeded["goal_difference"] = 0
    if "goals_for" not in seeded.columns:
        seeded["goals_for"] = 0
    if "group" not in seeded.columns:
        seeded["group"] = ""

    seeded["_qualification_type_order"] = seeded["qualification_type"].map(QUALIFICATION_TYPE_ORDER).fillna(99)
    seeded = seeded.sort_values(
        ["group_rank", "_qualification_type_order", "points", "goal_difference", "goals_for", "team"],
        ascending=[True, True, False, False, False, True],
        kind="mergesort",
    ).reset_index(drop=True)
    seeded["seed"] = range(1, len(seeded) + 1)
    seeded["seed_label"] = seeded["seed"].map(lambda value: f"S{int(value):02d}")
    return seeded.drop(columns=["_qualification_type_order"])


def create_round_of_32_bracket(seeded_qualifiers_df: pd.DataFrame) -> pd.DataFrame:
    """Create the deterministic simulation bracket for the Round of 32."""
    if "seed" not in seeded_qualifiers_df.columns:
        raise ValueError("seeded_qualifiers_df must contain a 'seed' column.")

    seed_map = seeded_qualifiers_df.set_index("seed")
    rows: list[dict[str, Any]] = []

    for index, (seed_a, seed_b) in enumerate(ROUND_OF_32_PAIRINGS, start=1):
        row_a = seed_map.loc[seed_a]
        row_b = seed_map.loc[seed_b]
        rows.append(
            {
                "round": TOURNAMENT_STAGE_ROUND_OF_32,
                "match_id": f"R32-{index:02d}",
                "team_a": str(row_a["team"]),
                "team_b": str(row_b["team"]),
                "seed_a": int(seed_a),
                "seed_b": int(seed_b),
                "source_a": str(row_a["seed_label"]),
                "source_b": str(row_b["seed_label"]),
                "winner_to": f"R16-{(index + 1) // 2:02d}",
                "group_a": str(row_a.get("group", "")),
                "group_b": str(row_b.get("group", "")),
                "qualification_type_a": str(row_a.get("qualification_type", "")),
                "qualification_type_b": str(row_b.get("qualification_type", "")),
            }
        )

    return pd.DataFrame(rows)


def convert_to_no_draw_probabilities(probabilities: dict[str, Any]) -> dict[str, float]:
    """Convert win/draw/loss probabilities into a no-draw knockout distribution."""
    normalised = _normalise_probabilities(probabilities)
    team_a_win = float(normalised.get("team_a_win", 0.0))
    team_a_loss = float(normalised.get("team_a_loss", 0.0))
    total = team_a_win + team_a_loss
    if total <= 0:
        team_a_knockout = 0.5
        team_b_knockout = 0.5
    else:
        team_a_knockout = team_a_win / total
        team_b_knockout = team_a_loss / total

    return {
        "team_a_loss_probability": team_a_loss,
        "draw_probability": float(normalised.get("draw", 0.0)),
        "team_a_win_probability": team_a_win,
        "team_a_knockout_win_probability": team_a_knockout,
        "team_b_knockout_win_probability": team_b_knockout,
    }


def sample_knockout_winner(
    team_a: str,
    team_b: str,
    probabilities: dict[str, Any],
    rng: np.random.Generator | None = None,
) -> str:
    """Sample a knockout winner from no-draw probabilities and return the team name."""
    rng = _coerce_rng(rng=rng)
    team_a_probability = float(
        probabilities.get("team_a_knockout_win_probability", probabilities.get("team_a_win_probability", 0.0)) or 0.0
    )
    team_b_probability = float(
        probabilities.get("team_b_knockout_win_probability", probabilities.get("team_a_loss_probability", 0.0)) or 0.0
    )
    total = team_a_probability + team_b_probability
    if total <= 0:
        team_a_probability = team_b_probability = 0.5
    else:
        team_a_probability /= total
        team_b_probability /= total
    return str(rng.choice([team_a, team_b], p=[team_a_probability, team_b_probability]))


def sample_knockout_scoreline(*args: Any, rng: np.random.Generator | None = None, **kwargs: Any) -> tuple[int, int, str]:
    """Sample a transparent knockout scoreline and method.

    Supports two calling patterns:
    - ``sample_knockout_scoreline("team_a_win_regular")`` for direct template tests.
    - ``sample_knockout_scoreline(team_a, team_b, winner, normal_time_result)`` for the simulator.
    """
    rng = _coerce_rng(rng=rng)

    if len(args) == 1 and not kwargs:
        result_label = str(args[0])
        if result_label == "team_b_win_regular":
            templates = KNOCKOUT_SCORELINE_TEMPLATES.get("team_b_win_regular", [(0, 1)])
            outcome_method = "regular_time"
        elif result_label == "team_a_win_extra":
            templates = KNOCKOUT_SCORELINE_TEMPLATES.get("team_a_win_extra", [(1, 1)])
            outcome_method = "extra_time_or_penalties"
        elif result_label == "team_b_win_extra":
            templates = KNOCKOUT_SCORELINE_TEMPLATES.get("team_b_win_extra", [(1, 1)])
            outcome_method = "extra_time_or_penalties"
        elif result_label == "draw":
            templates = KNOCKOUT_SCORELINE_TEMPLATES.get("team_a_win_extra", [(1, 1)])
            outcome_method = "extra_time_or_penalties"
        else:
            templates = KNOCKOUT_SCORELINE_TEMPLATES.get("team_a_win_regular", [(1, 0)])
            outcome_method = "regular_time"

        index = int(rng.integers(0, len(templates)))
        team_a_score, team_b_score = templates[index]
        return int(team_a_score), int(team_b_score), outcome_method

    team_a = str(args[0]) if len(args) > 0 else str(kwargs.get("team_a", "team_a"))
    team_b = str(args[1]) if len(args) > 1 else str(kwargs.get("team_b", "team_b"))
    winner = str(args[2]) if len(args) > 2 else str(kwargs.get("winner", team_a))
    normal_time_result = str(args[3]) if len(args) > 3 else str(kwargs.get("normal_time_result", "team_a_win"))

    if normal_time_result == "draw":
        templates = KNOCKOUT_SCORELINE_TEMPLATES.get("team_a_win_extra", [(1, 1)])
        outcome_method = "extra_time_or_penalties"
        team_a_score, team_b_score = templates[int(rng.integers(0, len(templates)))]
        return int(team_a_score), int(team_b_score), outcome_method

    if winner == team_a:
        templates = KNOCKOUT_SCORELINE_TEMPLATES.get("team_a_win_regular", [(1, 0)])
        team_a_score, team_b_score = templates[int(rng.integers(0, len(templates)))]
        return int(team_a_score), int(team_b_score), "regular_time"

    templates = KNOCKOUT_SCORELINE_TEMPLATES.get("team_b_win_regular", [(0, 1)])
    team_a_score, team_b_score = templates[int(rng.integers(0, len(templates)))]
    return int(team_a_score), int(team_b_score), "regular_time"


def _sample_normal_time_result(probabilities: dict[str, float], rng: np.random.Generator) -> str:
    labels = ["team_a_loss", "draw", "team_a_win"]
    values = [float(probabilities.get(label, 0.0)) for label in labels]
    return _sample_label(labels, values, rng)


def simulate_knockout_match(
    match_row: pd.Series,
    round_name: str,
    random_seed: int | None = None,
    rng: np.random.Generator | None = None,
) -> dict[str, Any]:
    """Simulate a single knockout match with a guaranteed winner."""
    rng = _coerce_rng(random_seed=random_seed, rng=rng)

    team_a = str(match_row["team_a"])
    team_b = str(match_row["team_b"])
    match_id = str(match_row["match_id"])
    match_date = _round_date(round_name)
    tournament = "FIFA World Cup"
    prediction_error = ""
    model_type = "unknown"

    try:
        prediction = predict_future_match(
            team_a=team_a,
            team_b=team_b,
            match_date=match_date,
            tournament=tournament,
            city=str(match_row.get("city", "Unknown")),
            country=str(match_row.get("country", "Unknown")),
            neutral=1,
        )
        probabilities = _normalise_probabilities(prediction.get("probabilities", {}))
        model_type = str(prediction.get("model_type", "unknown"))
    except Exception as exc:  # pragma: no cover - resiliency path
        probabilities = _normalise_probabilities({})
        prediction_error = str(exc)
        model_type = "fallback"

    no_draw_probabilities = convert_to_no_draw_probabilities(probabilities)
    winner = sample_knockout_winner(team_a, team_b, no_draw_probabilities, rng=rng)
    normal_time_result = _sample_normal_time_result(probabilities, rng=rng)
    team_a_score, team_b_score, outcome_method = sample_knockout_scoreline(
        team_a,
        team_b,
        winner,
        normal_time_result,
        rng=rng,
    )
    loser = team_b if winner == team_a else team_a

    return {
        "round": round_name,
        "match_id": match_id,
        "date": match_date,
        "team_a": team_a,
        "team_b": team_b,
        "model_type": model_type,
        "team_a_loss_probability": float(no_draw_probabilities["team_a_loss_probability"]),
        "draw_probability": float(no_draw_probabilities["draw_probability"]),
        "team_a_win_probability": float(no_draw_probabilities["team_a_win_probability"]),
        "team_a_knockout_win_probability": float(no_draw_probabilities["team_a_knockout_win_probability"]),
        "team_b_knockout_win_probability": float(no_draw_probabilities["team_b_knockout_win_probability"]),
        "normal_time_result": normal_time_result,
        "simulated_team_a_score": int(team_a_score),
        "simulated_team_b_score": int(team_b_score),
        "outcome_method": outcome_method,
        "winner": winner,
        "loser": loser,
        "prediction_error": prediction_error,
    }


def build_next_round_matches(
    previous_round_results: pd.DataFrame,
    next_round_name: str,
) -> pd.DataFrame:
    """Pair winners from the previous round into the next round's bracket."""
    if previous_round_results.empty:
        return pd.DataFrame(columns=["round", "match_id", "team_a", "team_b", "source_a", "source_b", "winner_to"])

    results = previous_round_results.sort_values("match_id").reset_index(drop=True)
    if len(results) % 2 != 0:
        raise ValueError("previous_round_results must contain an even number of winners.")

    rows: list[dict[str, Any]] = []
    prefix = _round_prefix(next_round_name)
    next_prefix = {
        TOURNAMENT_STAGE_ROUND_OF_16: "QF",
        TOURNAMENT_STAGE_QUARTER_FINAL: "SF",
        TOURNAMENT_STAGE_SEMI_FINAL: "F",
        TOURNAMENT_STAGE_FINAL: "CHAMPION",
        TOURNAMENT_STAGE_THIRD_PLACE: "THIRD_PLACE",
    }.get(next_round_name, "NEXT")

    for index in range(0, len(results), 2):
        match_number = index // 2 + 1
        row_a = results.iloc[index]
        row_b = results.iloc[index + 1]
        rows.append(
            {
                "round": next_round_name,
                "match_id": f"{prefix}-{match_number:02d}",
                "team_a": str(row_a["winner"]),
                "team_b": str(row_b["winner"]),
                "source_a": str(row_a["match_id"]),
                "source_b": str(row_b["match_id"]),
                "winner_to": (
                    next_prefix
                    if next_prefix in {"CHAMPION", "THIRD_PLACE"}
                    else f"{next_prefix}-{match_number:02d}"
                ),
            }
        )

    return pd.DataFrame(rows)


def _build_third_place_match(semifinal_results: pd.DataFrame) -> pd.DataFrame:
    if semifinal_results.empty:
        return pd.DataFrame(columns=["round", "match_id", "team_a", "team_b", "source_a", "source_b", "winner_to"])

    results = semifinal_results.sort_values("match_id").reset_index(drop=True)
    if len(results) < 2:
        raise ValueError("Semifinal results must contain two matches to build the third-place match.")

    return pd.DataFrame(
        [
            {
                "round": TOURNAMENT_STAGE_THIRD_PLACE,
                "match_id": "TP-01",
                "team_a": str(results.iloc[0]["loser"]),
                "team_b": str(results.iloc[1]["loser"]),
                "source_a": str(results.iloc[0]["match_id"]),
                "source_b": str(results.iloc[1]["match_id"]),
                "winner_to": "THIRD_PLACE",
            }
        ]
    )


def simulate_knockout_round(
    matches_df: pd.DataFrame,
    round_name: str,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Simulate all matches in a knockout round."""
    if matches_df.empty:
        return pd.DataFrame()
    rows = [simulate_knockout_match(row, round_name=round_name, rng=rng) for _, row in matches_df.iterrows()]
    return pd.DataFrame(rows)


def simulate_knockout_stage(
    qualifiers_df: pd.DataFrame | None = None,
    random_seed: int = 42,
) -> dict[str, Any]:
    """Simulate one complete knockout bracket for a single tournament run."""
    if qualifiers_df is None:
        qualifiers_df = load_round_of_32_qualifiers()

    seeded_qualifiers = assign_knockout_seeds(qualifiers_df)
    round_of_32_bracket = create_round_of_32_bracket(seeded_qualifiers)
    rng = np.random.default_rng(random_seed)

    bracket_parts: list[pd.DataFrame] = [round_of_32_bracket.copy()]
    simulated_parts: list[pd.DataFrame] = []

    r32_results = simulate_knockout_round(round_of_32_bracket, TOURNAMENT_STAGE_ROUND_OF_32, rng)
    simulated_parts.append(r32_results)

    r16_bracket = build_next_round_matches(r32_results, TOURNAMENT_STAGE_ROUND_OF_16)
    bracket_parts.append(r16_bracket.copy())
    r16_results = simulate_knockout_round(r16_bracket, TOURNAMENT_STAGE_ROUND_OF_16, rng)
    simulated_parts.append(r16_results)

    qf_bracket = build_next_round_matches(r16_results, TOURNAMENT_STAGE_QUARTER_FINAL)
    bracket_parts.append(qf_bracket.copy())
    qf_results = simulate_knockout_round(qf_bracket, TOURNAMENT_STAGE_QUARTER_FINAL, rng)
    simulated_parts.append(qf_results)

    sf_bracket = build_next_round_matches(qf_results, TOURNAMENT_STAGE_SEMI_FINAL)
    bracket_parts.append(sf_bracket.copy())
    sf_results = simulate_knockout_round(sf_bracket, TOURNAMENT_STAGE_SEMI_FINAL, rng)
    simulated_parts.append(sf_results)

    third_place_bracket = _build_third_place_match(sf_results)
    bracket_parts.append(third_place_bracket.copy())
    third_place_results = simulate_knockout_round(third_place_bracket, TOURNAMENT_STAGE_THIRD_PLACE, rng)
    simulated_parts.append(third_place_results)

    final_bracket = build_next_round_matches(sf_results, TOURNAMENT_STAGE_FINAL)
    bracket_parts.append(final_bracket.copy())
    final_results = simulate_knockout_round(final_bracket, TOURNAMENT_STAGE_FINAL, rng)
    simulated_parts.append(final_results)

    simulated_matches_df = pd.concat(simulated_parts, ignore_index=True) if simulated_parts else pd.DataFrame()
    bracket_filled_df = pd.concat(bracket_parts, ignore_index=True) if bracket_parts else pd.DataFrame()

    champion = str(final_results.iloc[0]["winner"]) if not final_results.empty else None
    runner_up = str(final_results.iloc[0]["loser"]) if not final_results.empty else None
    third_place = str(third_place_results.iloc[0]["winner"]) if not third_place_results.empty else None
    fourth_place = str(third_place_results.iloc[0]["loser"]) if not third_place_results.empty else None

    result_dict: dict[str, Any] = {
        "seeded_qualifiers": seeded_qualifiers,
        "bracket_filled": bracket_filled_df,
        "simulated_matches": simulated_matches_df,
        "champion": champion,
        "runner_up": runner_up,
        "third_place": third_place,
        "fourth_place": fourth_place,
    }

    validation_passed, validation_report = validate_knockout_simulation(simulated_matches_df, result_dict)
    summary = create_knockout_summary(result_dict, validation_passed, random_seed)
    result_dict.update(
        {
            "validation_passed": validation_passed,
            "validation_report": validation_report,
            "summary": summary,
        }
    )
    return result_dict


def validate_knockout_simulation(
    simulated_matches_df: pd.DataFrame,
    result_summary: dict[str, Any],
) -> tuple[bool, pd.DataFrame]:
    """Validate knockout match counts and the single-tournament winner path."""
    checks: list[dict[str, Any]] = []

    def _add(check: str, expected: Any, actual: Any, passed: bool) -> None:
        checks.append({"check": check, "expected": expected, "actual": actual, "passed": bool(passed)})

    round_counts = simulated_matches_df.groupby("round") ["match_id"].count().to_dict() if not simulated_matches_df.empty and "round" in simulated_matches_df.columns else {}

    _add(
        "total_knockout_matches",
        32,
        int(len(simulated_matches_df)),
        int(len(simulated_matches_df)) == 32,
    )
    for round_name in KNOCKOUT_ROUNDS:
        _add(
            f"{round_name}_count",
            int(KNOCKOUT_ROUND_MATCH_COUNTS[round_name]),
            int(round_counts.get(round_name, 0)),
            int(round_counts.get(round_name, 0)) == int(KNOCKOUT_ROUND_MATCH_COUNTS[round_name]),
        )

    winner_count_ok = bool("winner" in simulated_matches_df.columns and simulated_matches_df["winner"].notna().all())
    _add("every_match_has_winner", True, winner_count_ok, winner_count_ok)

    final_rows = simulated_matches_df.loc[simulated_matches_df.get("round", pd.Series(dtype=str)) == TOURNAMENT_STAGE_FINAL].copy() if not simulated_matches_df.empty else pd.DataFrame()
    final_winner_count = int(final_rows["winner"].notna().sum()) if not final_rows.empty and "winner" in final_rows.columns else 0
    _add("final_has_exactly_one_winner", 1, final_winner_count, final_winner_count == 1)

    champion = result_summary.get("champion")
    champion_present = champion is not None and str(champion).strip() != "" and str(champion).lower() != "nan"
    _add("champion_present", True, champion_present, champion_present)

    final_winner = str(final_rows.iloc[0]["winner"]) if final_winner_count == 1 else None
    champion_matches_final = champion_present and final_winner is not None and str(champion) == final_winner
    _add("champion_matches_final_winner", True, champion_matches_final, champion_matches_final)

    report_df = pd.DataFrame(checks)
    return bool(report_df["passed"].all()) if not report_df.empty else False, report_df


def create_knockout_summary(result_dict: dict[str, Any], validation_passed: bool, random_seed: int) -> dict[str, Any]:
    """Create a summary payload for Step 13 persistence and UI display."""
    simulated_matches_df = result_dict.get("simulated_matches", pd.DataFrame())
    if isinstance(simulated_matches_df, pd.DataFrame) and not simulated_matches_df.empty and "round" in simulated_matches_df.columns:
        round_counts = simulated_matches_df.groupby("round") ["match_id"].count().to_dict()
    else:
        round_counts = {}

    return {
        "status": "ok" if validation_passed else "validation_failed",
        "validation_passed": bool(validation_passed),
        "random_seed": int(random_seed),
        "champion": result_dict.get("champion"),
        "runner_up": result_dict.get("runner_up"),
        "third_place": result_dict.get("third_place"),
        "fourth_place": result_dict.get("fourth_place"),
        "total_knockout_matches": int(len(simulated_matches_df)) if isinstance(simulated_matches_df, pd.DataFrame) else 0,
        "round_counts": {key: int(value) for key, value in round_counts.items()},
        "notes": [
            "Step 13 simulates one knockout bracket only.",
            "Knockout winner selection uses no-draw adjusted probabilities.",
            "Bracket order is a deterministic simulation seed order, not the official FIFA bracket.",
            "Monte Carlo and champion probabilities are reserved for later steps.",
        ],
    }
