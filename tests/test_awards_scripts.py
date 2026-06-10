"""Smoke tests for Step 17 awards scripts."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from scripts.generate_golden_ball_predictions import main as generate_golden_main
from scripts.generate_world_cup_awards import main as generate_awards_main
from scripts.inspect_golden_ball_predictions import main as inspect_golden_main
from scripts.inspect_world_cup_awards import main as inspect_awards_main
from scripts import inspect_golden_ball_predictions as inspect_golden_mod
from scripts import inspect_world_cup_awards as inspect_awards_mod


def test_generate_world_cup_awards_script_smoke(monkeypatch) -> None:
    monkeypatch.setattr(
        "scripts.generate_world_cup_awards.prepare_step18_world_cup_awards",
        lambda: {
            "status": "ok",
            "validation_passed": True,
            "top_golden_ball_player": "Player A",
            "top_golden_boot_player": "Player B",
            "top_golden_glove_player": "Player C",
            "top_young_player": "Player D",
            "top_fair_play_team": "Japan",
            "top_entertaining_team": "Brazil",
            "team_of_tournament_count": 11,
            "report_path": "reports/world_cup_awards_report.md",
            "validation_report_path": "data/processed/world_cup_awards_validation_report.csv",
        },
    )
    assert generate_awards_main() == 0


def test_generate_golden_ball_compatibility_script_smoke(monkeypatch) -> None:
    monkeypatch.setattr(
        "scripts.generate_golden_ball_predictions.prepare_step18_world_cup_awards",
        lambda: {
            "status": "ok",
            "validation_passed": True,
            "top_golden_ball_player": "Player A",
            "top_golden_boot_player": "Player B",
            "top_golden_glove_player": "Player C",
            "report_path": "reports/world_cup_awards_report.md",
            "validation_report_path": "data/processed/world_cup_awards_validation_report.csv",
        },
    )
    assert generate_golden_main() == 0


def test_inspect_world_cup_awards_script_smoke(monkeypatch, tmp_path: Path) -> None:
    processed = tmp_path / "processed"
    reports = tmp_path / "reports"
    processed.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)

    pd.DataFrame({"award_category": ["golden_ball"], "rank": [1], "award": ["Golden Ball"], "player": ["Player A"], "team": ["France"], "position": ["forward"], "score": [10.0], "probability": [1.0], "notes": ["analytics estimate"]}).to_csv(processed / "world_cup_awards_predictions.csv", index=False)
    pd.DataFrame({"golden_ball_rank": [1], "player": ["Player A"], "team": ["France"], "position": ["forward"], "golden_ball_probability": [1.0], "award_podium": ["Golden Ball"]}).to_csv(processed / "golden_ball_predictions.csv", index=False)
    pd.DataFrame({"golden_boot_rank": [1], "player": ["Player B"], "team": ["England"], "position": ["forward"], "expected_goals_score": [5.0], "boot_podium": ["Golden Boot"]}).to_csv(processed / "golden_boot_predictions.csv", index=False)
    pd.DataFrame({"golden_glove_rank": [1], "player": ["Player C"], "team": ["Brazil"], "position": ["goalkeeper"], "golden_glove_probability": [1.0], "award": ["Golden Glove"]}).to_csv(processed / "golden_glove_predictions.csv", index=False)
    pd.DataFrame({"young_player_rank": [1], "player": ["Player D"], "team": ["Spain"], "position": ["midfielder"], "young_player_probability": [1.0], "award": ["Young Player Award"]}).to_csv(processed / "young_player_predictions.csv", index=False)
    pd.DataFrame({"fair_play_rank": [1], "team": ["Japan"], "fair_play_probability": [1.0], "award": ["Fair Play Trophy"]}).to_csv(processed / "fair_play_predictions.csv", index=False)
    pd.DataFrame({"most_entertaining_rank": [1], "team": ["Brazil"], "most_entertaining_probability": [1.0], "award": ["Most Entertaining Team"]}).to_csv(processed / "most_entertaining_team_predictions.csv", index=False)
    pd.DataFrame({"formation_slot": ["GK1"], "player": ["Player C"], "team": ["Brazil"], "position": ["goalkeeper"]}).to_csv(processed / "team_of_the_tournament.csv", index=False)
    pd.DataFrame({"check": ["ok"], "passed": [True]}).to_csv(processed / "world_cup_awards_validation_report.csv", index=False)
    with (processed / "world_cup_awards_summary.json").open("w", encoding="utf-8") as f:
        json.dump({"status": "ok", "top_golden_ball_player": "Player A"}, f)
    (reports / "world_cup_awards_report.md").write_text("# Awards Report\n", encoding="utf-8")

    monkeypatch.setattr(inspect_awards_mod, "PROCESSED_DATA_DIR", processed)
    monkeypatch.setattr(inspect_awards_mod, "REPORTS_DIR", reports)
    assert inspect_awards_main() == 0


def test_inspect_golden_ball_compatibility_script_smoke(monkeypatch, tmp_path: Path) -> None:
    processed = tmp_path / "processed"
    reports = tmp_path / "reports"
    processed.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)

    pd.DataFrame({"golden_ball_rank": [1], "player": ["Player A"], "team": ["France"], "position": ["forward"], "golden_ball_probability": [1.0], "award_podium": ["Golden Ball"]}).to_csv(processed / "golden_ball_predictions.csv", index=False)
    pd.DataFrame({"check": ["ok"], "passed": [True]}).to_csv(processed / "world_cup_awards_validation_report.csv", index=False)
    with (processed / "world_cup_awards_summary.json").open("w", encoding="utf-8") as f:
        json.dump({"status": "ok", "top_golden_ball_player": "Player A"}, f)
    (reports / "world_cup_awards_report.md").write_text("# Awards Report\n", encoding="utf-8")

    monkeypatch.setattr(inspect_golden_mod, "PROCESSED_DATA_DIR", processed)
    monkeypatch.setattr(inspect_golden_mod, "REPORTS_DIR", reports)
    assert inspect_golden_main() == 0
