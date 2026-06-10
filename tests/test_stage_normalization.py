"""Tests for Step 17H stage normalization."""

from __future__ import annotations

import pandas as pd

from src.official.stage_normalization import (
    apply_stage_normalization,
    is_group_stage_label,
    is_knockout_stage_label,
    normalize_stage_name,
)


def test_normalize_stage_name_first_stage():
    assert normalize_stage_name("First Stage") == "group_stage"
    assert normalize_stage_name("Group Stage") == "group_stage"


def test_is_group_stage_label_first_stage():
    assert is_group_stage_label("First Stage") is True
    assert is_group_stage_label("group_stage") is True


def test_is_knockout_stage_label():
    assert is_knockout_stage_label("Round of 16") is True
    assert is_knockout_stage_label("Final") is True
    assert is_knockout_stage_label("First Stage") is False


def test_apply_stage_normalization_converts_first_stage():
    df = pd.DataFrame({"stage": ["First Stage", "Final"], "match_id": ["m1", "m2"]})
    out = apply_stage_normalization(df)
    assert out.iloc[0]["stage"] == "group_stage"
    assert out.iloc[0]["original_stage"] == "First Stage"
    assert out.iloc[1]["stage"] == "final"
