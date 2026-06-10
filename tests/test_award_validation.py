"""Tests for Step 18 award validation."""

from __future__ import annotations

import pandas as pd

from src.awards.award_validation import validate_award_outputs


def _valid_outputs() -> dict:
    golden_ball = pd.DataFrame(
        {
            "player_id": ["p1"],
            "player_name": ["A"],
            "team": ["France"],
            "position_code": ["FW"],
            "position_group": ["forward"],
            "golden_ball_probability": [1.0],
            "final_golden_ball_score": [10.0],
            "award": ["Golden Ball"],
        }
    )
    golden_boot = pd.DataFrame({"player_id": ["p1"], "player_name": ["A"], "golden_boot_probability": [1.0], "boot_tiebreak_score": [5.0], "award": ["Golden Boot"]})
    golden_glove = pd.DataFrame({"player_id": ["g1"], "player_name": ["G"], "position_code": ["GK"], "position_group": ["goalkeeper"], "golden_glove_probability": [1.0], "award": ["Golden Glove"]})
    young = pd.DataFrame({"player_id": ["y1"], "player_name": ["Y"], "age_at_tournament_start": [20], "date_of_birth": ["2010-01-01"], "young_player_probability": [1.0], "award": ["Young Player Award"]})
    fair = pd.DataFrame({"team": ["France"], "fair_play_probability": [1.0], "award": ["Fair Play Trophy"]})
    ent = pd.DataFrame({"team": ["France"], "most_entertaining_probability": [1.0], "award": ["Most Entertaining Team"]})
    xi = pd.DataFrame(
        {
            "player_id": [f"p{i}" for i in range(11)],
            "player_name": [f"P{i}" for i in range(11)],
            "team": ["France"] * 11,
            "position_group": ["goalkeeper"] + ["defender"] * 4 + ["midfielder"] * 3 + ["forward"] * 3,
            "position_code": ["GK"] + ["DF"] * 4 + ["MF"] * 3 + ["FW"] * 3,
            "final_golden_ball_score": [1.0] * 11,
            "golden_ball_probability": [0.1] * 11,
            "award": ["Predicted Team of the Tournament"] * 11,
            "formation_slot": ["GK1", "DEF1", "DEF2", "DEF3", "DEF4", "MID1", "MID2", "MID3", "FWD1", "FWD2", "FWD3"],
        }
    )
    combined = pd.DataFrame({"award_category": ["golden_ball"], "rank": [1]})
    return {
        "golden_ball": golden_ball,
        "golden_boot": golden_boot,
        "golden_glove": golden_glove,
        "young_player": young,
        "fair_play": fair,
        "most_entertaining": ent,
        "team_of_tournament": xi,
        "combined_awards": combined,
    }


def test_validate_award_outputs_passes_valid(monkeypatch):
    monkeypatch.setattr("src.awards.award_validation.load_official_final_mode", lambda: {"official_final_enabled": True})
    ok, report = validate_award_outputs(_valid_outputs(), official_teams=pd.DataFrame({"team": ["France"]}))
    assert ok
    assert report["passed"].all()


def test_validate_award_outputs_fails_non_goalkeeper_in_glove(monkeypatch):
    monkeypatch.setattr("src.awards.award_validation.load_official_final_mode", lambda: {"official_final_enabled": True})
    outputs = _valid_outputs()
    outputs["golden_glove"] = pd.DataFrame({"player_id": ["p1"], "position_code": ["FW"], "position_group": ["forward"], "golden_glove_probability": [1.0]})
    ok, report = validate_award_outputs(outputs)
    assert not ok
    assert not report[report["check"] == "golden_glove_goalkeepers_only"]["passed"].iloc[0]


def test_validate_award_outputs_fails_wrong_team_of_tournament_shape(monkeypatch):
    monkeypatch.setattr("src.awards.award_validation.load_official_final_mode", lambda: {"official_final_enabled": True})
    outputs = _valid_outputs()
    outputs["team_of_tournament"] = outputs["team_of_tournament"].head(5)
    ok, report = validate_award_outputs(outputs)
    assert not ok
