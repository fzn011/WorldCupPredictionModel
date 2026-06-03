"""Tests for Step 6 advanced model builders."""

from __future__ import annotations

from src.models.advanced_models import (
    build_advanced_models,
    build_hist_gradient_boosting_model,
)


def test_build_hist_gradient_boosting_model_returns_model() -> None:
    model = build_hist_gradient_boosting_model()
    assert model is not None
    assert hasattr(model, "fit")


def test_build_advanced_models_always_includes_hist_gradient_boosting() -> None:
    models = build_advanced_models()
    assert "hist_gradient_boosting" in models
    assert models["hist_gradient_boosting"] is not None


def test_optional_models_absence_does_not_fail() -> None:
    models = build_advanced_models()
    # Optional models may or may not be present, but function should always return dict.
    assert isinstance(models, dict)
    assert "hist_gradient_boosting" in models
