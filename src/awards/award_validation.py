"""Validate Step 18 World Cup awards outputs."""

from __future__ import annotations

from typing import Any

import pandas as pd

import src.utils.constants as C
from src.awards.award_data import require_official_final_ready
from src.official.promotion import load_official_final_mode


def create_award_validation_row(
    check: str,
    expected: Any,
    actual: Any,
    passed: bool,
    severity: str = "error",
) -> dict[str, Any]:
    return {
        "check": check,
        "expected": expected,
        "actual": actual,
        "passed": passed,
        "severity": severity,
    }


def _prob_sum_close(series: pd.Series, tol: float = 1e-5) -> bool:
    if series.empty:
        return False
    total = float(pd.to_numeric(series, errors="coerce").fillna(0.0).sum())
    return abs(total - 1.0) <= tol


def validate_award_outputs(
    outputs: dict[str, pd.DataFrame],
    official_candidates: pd.DataFrame | None = None,
    official_teams: pd.DataFrame | None = None,
) -> tuple[bool, pd.DataFrame]:
    """Validate award prediction outputs against Step 18 rules."""
    rows: list[dict[str, Any]] = []

    mode = load_official_final_mode()
    rows.append(
        create_award_validation_row(
            "official_final_enabled",
            True,
            bool(mode.get("official_final_enabled", False)),
            bool(mode.get("official_final_enabled", False)),
        )
    )

    golden_ball = outputs.get("golden_ball", pd.DataFrame())
    golden_boot = outputs.get("golden_boot", pd.DataFrame())
    golden_glove = outputs.get("golden_glove", pd.DataFrame())
    young_player = outputs.get("young_player", pd.DataFrame())
    fair_play = outputs.get("fair_play", pd.DataFrame())
    entertaining = outputs.get("most_entertaining", pd.DataFrame())
    team_xi = outputs.get("team_of_tournament", pd.DataFrame())
    combined = outputs.get("combined_awards", pd.DataFrame())

    rows.append(create_award_validation_row("golden_ball_not_empty", ">=1", len(golden_ball), not golden_ball.empty))
    rows.append(
        create_award_validation_row(
            "golden_ball_probabilities_sum",
            "~1.0",
            float(golden_ball.get("golden_ball_probability", pd.Series(dtype=float)).sum()) if not golden_ball.empty else 0,
            _prob_sum_close(golden_ball.get("golden_ball_probability", pd.Series(dtype=float))) if not golden_ball.empty else False,
        )
    )
    rows.append(create_award_validation_row("golden_boot_not_empty", ">=1", len(golden_boot), not golden_boot.empty))
    rows.append(
        create_award_validation_row(
            "golden_boot_probabilities_sum",
            "~1.0",
            float(golden_boot.get("golden_boot_probability", pd.Series(dtype=float)).sum()) if not golden_boot.empty else 0,
            _prob_sum_close(golden_boot.get("golden_boot_probability", pd.Series(dtype=float))) if not golden_boot.empty else False,
        )
    )
    rows.append(create_award_validation_row("golden_glove_not_empty", ">=1", len(golden_glove), not golden_glove.empty))
    gk_only = True
    if not golden_glove.empty:
        pos_code = golden_glove.get("position_code", pd.Series(dtype=str)).astype(str).str.upper()
        pos_group = golden_glove.get("position_group", golden_glove.get("position", pd.Series(dtype=str))).astype(str).str.lower()
        gk_only = bool((pos_code == "GK").all() or pos_group.eq("goalkeeper").all())
    rows.append(create_award_validation_row("golden_glove_goalkeepers_only", "GK only", gk_only, gk_only))
    rows.append(
        create_award_validation_row(
            "golden_glove_probabilities_sum",
            "~1.0",
            float(golden_glove.get("golden_glove_probability", pd.Series(dtype=float)).sum()) if not golden_glove.empty else 0,
            _prob_sum_close(golden_glove.get("golden_glove_probability", pd.Series(dtype=float))) if not golden_glove.empty else False,
        )
    )

    young_ok = True
    if not young_player.empty:
        from src.awards.player_awards import is_young_player_eligible

        young_ok = bool(young_player.apply(is_young_player_eligible, axis=1).all())
    rows.append(
        create_award_validation_row(
            "young_player_eligibility",
            "eligible only",
            young_ok,
            young_ok if not young_player.empty else True,
            severity="warning" if young_player.empty else "error",
        )
    )

    official_team_set: set[str] = set()
    if official_teams is not None and not official_teams.empty:
        official_team_set = set(official_teams["team"].astype(str))
    if official_team_set:
        fair_teams = set(fair_play.get("team", pd.Series(dtype=str)).astype(str)) if not fair_play.empty else set()
        ent_teams = set(entertaining.get("team", pd.Series(dtype=str)).astype(str)) if not entertaining.empty else set()
        rows.append(
            create_award_validation_row(
                "fair_play_official_teams",
                "subset of official teams",
                sorted(fair_teams - official_team_set) or "ok",
                fair_teams.issubset(official_team_set) if fair_teams else True,
            )
        )
        rows.append(
            create_award_validation_row(
                "most_entertaining_official_teams",
                "subset of official teams",
                sorted(ent_teams - official_team_set) or "ok",
                ent_teams.issubset(official_team_set) if ent_teams else True,
            )
        )

    pos_counts = (
        team_xi.get("position_group", team_xi.get("position", pd.Series(dtype=str))).astype(str).str.lower().value_counts()
        if not team_xi.empty
        else pd.Series(dtype=int)
    )
    formation_ok = (
        len(team_xi) == 11
        and int(pos_counts.get("goalkeeper", 0)) == 1
        and int(pos_counts.get("defender", 0)) == 4
        and int(pos_counts.get("midfielder", 0)) == 3
        and int(pos_counts.get("forward", 0)) == 3
    )
    rows.append(create_award_validation_row("team_of_tournament_size", 11, len(team_xi), len(team_xi) == 11))
    rows.append(
        create_award_validation_row(
            "team_of_tournament_formation",
            "1 GK / 4 DEF / 3 MID / 3 FWD",
            pos_counts.to_dict(),
            formation_ok,
        )
    )

    if official_candidates is not None and not official_candidates.empty:
        allowed_players = set(official_candidates.get("player_id", pd.Series(dtype=str)).astype(str))
        allowed_names = set(official_candidates.get("player_name", official_candidates.get("player", pd.Series(dtype=str))).astype(str))
        for key in ("golden_ball", "golden_boot", "golden_glove", "young_player"):
            df = outputs.get(key, pd.DataFrame())
            if df.empty:
                continue
            if "player_id" in df.columns:
                unknown = df[~df["player_id"].astype(str).isin(allowed_players)]
            else:
                name_col = "player_name" if "player_name" in df.columns else "player"
                unknown = df[~df[name_col].astype(str).isin(allowed_names)]
            rows.append(
                create_award_validation_row(
                    f"{key}_official_candidates_only",
                    "0 non-official players",
                    len(unknown),
                    len(unknown) == 0,
                )
            )

    rows.append(create_award_validation_row("combined_awards_exists", ">=1 row", len(combined), not combined.empty))

    report_df = pd.DataFrame(rows)
    valid = not ((report_df["severity"] == "error") & (~report_df["passed"])).any()
    return bool(valid), report_df
