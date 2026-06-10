"""Smoke tests for Step 19 final demo scripts."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_script(name: str):
    path = Path(__file__).resolve().parents[1] / "scripts" / name
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_prepare_final_project_pack_importable():
    mod = _load_script("prepare_final_project_pack.py")
    assert hasattr(mod, "main")


def test_run_final_demo_pipeline_importable():
    mod = _load_script("run_final_demo_pipeline.py")
    assert hasattr(mod, "main")


def test_enrich_player_priors_importable():
    mod = _load_script("enrich_player_priors.py")
    assert hasattr(mod, "main")


def test_export_player_award_prior_template_importable():
    mod = _load_script("export_player_award_prior_template.py")
    assert hasattr(mod, "main")


def test_run_final_demo_pipeline_supports_manual_priors():
    mod = _load_script("run_final_demo_pipeline.py")
    import inspect

    source = inspect.getsource(mod.main)
    assert "--use-manual-priors" in source
