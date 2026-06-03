"""Tests for Step 6 improved model training pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from src.models.train_improved_model import train_improved_models
from tests.test_train_baseline_models import _synthetic_feature_df


def test_train_improved_models_returns_ok() -> None:
    summary = train_improved_models(feature_df=_synthetic_feature_df(), test_start_date="2022-01-01")
    assert summary["status"] == "ok"
    assert summary["train_rows"] > 0
    assert summary["calibration_rows"] > 0
    assert summary["test_rows"] > 0
    assert summary["feature_count"] > 0


def test_train_improved_models_saves_artifacts() -> None:
    summary = train_improved_models(feature_df=_synthetic_feature_df(), test_start_date="2022-01-01")
    assert Path(summary["improved_metrics_path"]).is_file()
    assert Path(summary["best_model_path"]).is_file()
    metadata_path = Path("models/improved/improved_model_metadata.json")
    assert metadata_path.is_file()
    metadata = json.loads(metadata_path.read_text())
    assert metadata["best_model_name"]
