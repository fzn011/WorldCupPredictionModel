"""Tests for Step 17H source label helpers."""

from __future__ import annotations

import pandas as pd

from src.official.source_labels import (
    is_official_source_label,
    is_sample_source_label,
    replace_sample_source_labels_for_verified_imports,
)


def test_sample_labels_detected():
    assert is_sample_source_label("sample_to_be_verified") is True
    assert is_sample_source_label("ai_prefilled_needs_verification") is True
    assert is_sample_source_label("fifa_schedule_api") is False


def test_official_labels_detected():
    assert is_official_source_label("fifa_schedule_api") is True
    assert is_official_source_label("fifa_squad_pdf") is True
    assert is_official_source_label("sample") is False


def test_replace_sample_source_labels_when_requirements_met():
    df = pd.DataFrame(
        {
            "team": ["Mexico"],
            "source": ["ai_prefilled_needs_verification"],
        }
    )
    out = replace_sample_source_labels_for_verified_imports(
        df, "teams", "fifa_schedule_api", require_min_rows=1
    )
    assert out.iloc[0]["source"] == "fifa_schedule_api"


def test_replace_sample_source_labels_skips_when_min_rows_not_met():
    df = pd.DataFrame({"team": ["Mexico"], "source": ["sample_to_be_verified"]})
    out = replace_sample_source_labels_for_verified_imports(
        df, "teams", "fifa_schedule_api", require_min_rows=48
    )
    assert out.iloc[0]["source"] == "sample_to_be_verified"
