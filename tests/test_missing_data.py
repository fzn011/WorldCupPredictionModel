"""Tests for missing-data reporting."""

from __future__ import annotations

import pandas as pd

from src.official.missing_data import find_missing_or_placeholder_values, build_official_missing_data_report


def test_find_missing_or_placeholder_values_detects_issues():
    df = pd.DataFrame(
        {
            "team": ["Brazil", "TBD", ""],
            "team_code": ["BRA", "XXX", "YYY"],
        }
    )
    report = find_missing_or_placeholder_values(
        df,
        "teams",
        ["team", "team_code"],
        ["TBD", ""],
    )
    issue_types = set(report["issue_type"].tolist())
    assert "placeholder_value" in issue_types
    assert "missing_value" in issue_types


def test_build_official_missing_data_report_returns_dataframe():
    report = build_official_missing_data_report()
    assert isinstance(report, pd.DataFrame)
    expected_cols = {"dataset", "row_index", "column", "value", "issue_type", "severity", "message"}
    assert expected_cols.issubset(set(report.columns))
