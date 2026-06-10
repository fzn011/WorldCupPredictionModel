"""Tests for Step 17G future team filter fix."""

from __future__ import annotations

import pandas as pd
import pytest

import src.utils.constants as C
from src.features.future_match_features import get_available_teams


def test_get_available_teams_fallback_returns_non_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = pd.DataFrame({"team": ["Brazil", "Argentina", "France"]})
    monkeypatch.setattr(
        "src.features.future_match_features.get_official_team_list",
        lambda: [],
    )
    monkeypatch.setattr(
        "src.features.future_match_features.load_best_available_processed_data",
        lambda: {
            "canonical_matches": pd.DataFrame(),
            "ranking_feature_dataset": pd.DataFrame(),
            "team_strength_snapshot": pd.DataFrame(),
            "team_registry": registry,
        },
    )
    teams = get_available_teams(official_only=False)
    assert teams
    assert teams == sorted(teams)


def test_get_official_team_list_prefers_populated_48_teams(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    populated = tmp_path / "data" / "official" / "populated"
    processed = tmp_path / "data" / "official" / "processed"
    populated.mkdir(parents=True)
    processed.mkdir(parents=True)

    teams = []
    for i in range(48):
        teams.append(
            {
                "team": f"Team {i}",
                "team_code": f"T{i:02d}",
                "confederation": "UEFA",
                "group": chr(ord("A") + (i // 4)),
                "group_slot": (i % 4) + 1,
                "is_host": 0,
                "qualified": 1,
                "source": "fifa_schedule_api",
            }
        )
    pd.DataFrame(teams).to_csv(populated / C.POPULATED_OFFICIAL_TEAMS_FILE, index=False)
    pd.DataFrame({"team": ["Old Team"], "source": ["ai_prefilled_needs_verification"]}).to_csv(
        processed / C.OFFICIAL_TEAMS_FILE, index=False
    )

    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr("src.official.loaders.PROJECT_ROOT", tmp_path)
    monkeypatch.setattr("src.official.loaders.OFFICIAL_PROCESSED_DIR", processed)

    from src.official.loaders import get_official_team_list

    official = get_official_team_list()
    assert len(official) == 48
    assert official == sorted(official)


def test_get_available_teams_official_only_returns_official_teams(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    processed = tmp_path / "data" / "official" / "processed"
    processed.mkdir(parents=True)
    pd.DataFrame(
        {
            "team_id": ["t1", "t2"],
            "team": ["Mexico", "Brazil"],
            "team_code": ["MEX", "BRA"],
            "confederation": ["CONCACAF", "CONMEBOL"],
            "group": ["A", "B"],
            "group_slot": [1, 1],
            "is_host": [1, 0],
            "qualified": [1, 1],
            "source": ["fifa_official_manual", "fifa_official_manual"],
            "last_verified_at": ["2026-01-01", "2026-01-01"],
        }
    ).to_csv(processed / C.OFFICIAL_TEAMS_FILE, index=False)

    monkeypatch.setattr(C, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr("src.official.loaders.PROJECT_ROOT", tmp_path)
    monkeypatch.setattr("src.official.loaders.OFFICIAL_PROCESSED_DIR", processed)

    teams = get_available_teams(official_only=True)
    assert teams == ["Brazil", "Mexico"]


def test_get_available_teams_returns_sorted_unique_values(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = pd.DataFrame({"team": ["France", "Argentina", "France", "Brazil"]})
    monkeypatch.setattr(
        "src.features.future_match_features.get_official_team_list",
        lambda: [],
    )
    monkeypatch.setattr(
        "src.features.future_match_features.load_best_available_processed_data",
        lambda: {
            "canonical_matches": pd.DataFrame(),
            "ranking_feature_dataset": pd.DataFrame(),
            "team_strength_snapshot": pd.DataFrame(),
            "team_registry": registry,
        },
    )
    teams = get_available_teams(official_only=False)
    assert teams == ["Argentina", "Brazil", "France"]
    assert len(teams) == len(set(teams))
