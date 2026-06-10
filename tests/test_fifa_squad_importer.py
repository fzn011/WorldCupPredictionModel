"""Tests for Step 17F FIFA squad importer."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import src.utils.constants as C
from src.official.fifa_squad_importer import (
    load_fifa_squad_csv_or_xlsx,
    normalize_squad_to_official_schema,
    save_populated_squad_outputs,
    validate_imported_squad_completeness,
)


def _sample_squad(n_teams: int = 1, players_per_team: int = 26) -> pd.DataFrame:
    rows = []
    for t in range(n_teams):
        team = f"Team{t+1}"
        for p in range(players_per_team):
            rows.append(
                {
                    "team": team,
                    "player_name": f"Player {t+1}-{p+1}",
                    "pos": "MF",
                    "dob": "1995-01-01",
                    "club": "Club",
                }
            )
    return pd.DataFrame(rows)


def test_normalize_squad_to_official_schema():
    squad_df = _sample_squad(1, 2)
    players_df, audit_df = normalize_squad_to_official_schema(squad_df)
    assert len(players_df) == 2
    assert "player_name" in players_df.columns
    assert not audit_df.empty


def test_load_fifa_squad_csv(tmp_path):
    path = tmp_path / "squads.csv"
    _sample_squad(1, 3).to_csv(path, index=False)
    players_df = load_fifa_squad_csv_or_xlsx(str(path))
    assert len(players_df) == 3


def test_validate_imported_squad_completeness_detects_incomplete():
    players_df, _ = normalize_squad_to_official_schema(_sample_squad(1, 5))
    passed, report = validate_imported_squad_completeness(players_df)
    assert passed is False
    assert not report.empty


def test_save_populated_squad_outputs(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    players_df, audit_df = normalize_squad_to_official_schema(_sample_squad(1, 2))
    outputs = save_populated_squad_outputs(players_df, audit_df)
    assert Path(outputs["players_path"]).is_file()
