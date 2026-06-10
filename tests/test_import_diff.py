"""Tests for import diff utilities."""

from __future__ import annotations

import pandas as pd

from src.official.import_diff import compare_import_to_current, infer_key_columns


def test_infer_key_columns_returns_expected_keys():
    assert infer_key_columns("teams") == ["team"]
    assert infer_key_columns("groups") == ["group", "slot"]
    assert infer_key_columns("fixtures") == ["match_id"]
    assert infer_key_columns("players") == ["player_id"]
    assert infer_key_columns("player_priors") == ["player", "team"]


def test_compare_import_to_current_detects_changes():
    current = pd.DataFrame({"team": ["Brazil"], "team_code": ["BRA"]})
    import_df = pd.DataFrame({"team": ["Brazil"], "team_code": ["BRAZ"]})

    diff = compare_import_to_current(import_df, current, ["team"], "teams")
    change_types = set(diff["change_type"].tolist())
    assert "changed_value" in change_types

    current2 = pd.DataFrame({"team": ["Brazil", "France"], "team_code": ["BRA", "FRA"]})
    import2 = pd.DataFrame({"team": ["Brazil", "Germany"], "team_code": ["BRA", "GER"]})
    diff2 = compare_import_to_current(import2, current2, ["team"], "teams")
    change_types2 = set(diff2["change_type"].tolist())
    assert "added_row" in change_types2
    assert "removed_row" in change_types2
