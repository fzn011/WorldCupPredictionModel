"""Tests for official World Cup data contracts."""

from __future__ import annotations

import pandas as pd

from src.official.official_data_contracts import check_required_columns, get_official_contract


def test_get_official_contract_returns_required_columns() -> None:
    contract = get_official_contract("teams")
    assert "team" in contract
    assert "team_code" in contract


def test_check_required_columns_detects_missing_columns() -> None:
    df = pd.DataFrame({"team": ["France"]})
    ok, missing = check_required_columns(df, ["team", "team_code"], "teams")
    assert ok is False
    assert missing == ["team_code"]
