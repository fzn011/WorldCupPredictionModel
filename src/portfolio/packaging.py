"""Portfolio packaging utilities (Step 19)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import src.utils.constants as C

PROJECT_ROOT = C.PROJECT_ROOT
PORTFOLIO_DIR = PROJECT_ROOT / C.PORTFOLIO_DIR
ASSETS_DIR = PROJECT_ROOT / C.PORTFOLIO_ASSETS_DIR
SCREENSHOTS_DIR = PROJECT_ROOT / C.PORTFOLIO_SCREENSHOTS_DIR


def ensure_portfolio_dirs() -> dict[str, str]:
    """Create portfolio directory structure."""
    for path in (PORTFOLIO_DIR, ASSETS_DIR, SCREENSHOTS_DIR):
        path.mkdir(parents=True, exist_ok=True)
    return {
        "portfolio_dir": str(PORTFOLIO_DIR),
        "assets_dir": str(ASSETS_DIR),
        "screenshots_dir": str(SCREENSHOTS_DIR),
    }


def generate_portfolio_readme() -> str:
    text = f"""# {C.PROJECT_NAME} — Portfolio Overview

## Problem statement

Forecast FIFA World Cup 2026 match outcomes, simulate full tournament paths, and produce explainable analytics for team progression and award-style player/team estimates — using official squad data when `official_final` mode is enabled.

## What this app predicts

- Match outcome probabilities (home / draw / away)
- Single-run and Monte Carlo tournament progression
- Award-style analytics (Golden Ball, Golden Boot, Golden Glove, team awards, proxy fan-vote estimates)

## Data sources

- Historical international match data (sample or user-provided raw files)
- FIFA/Elo ranking snapshots
- **Official World Cup 2026** teams, fixtures, squads (Steps 17A–17H)
- Editable **player award priors** (heuristic defaults + manual edits)

## Pipeline overview

1. Clean & feature-engineer historical matches
2. Train baseline / improved / ranking-enhanced models
3. Predict future matches
4. Simulate group + knockout + full tournament
5. Monte Carlo team stage probabilities
6. Awards analytics (official candidates only)

## Official data gate

Awards and official-mode workflows require `official_final_enabled=true` after readiness checks pass. Sample players cannot enter awards.

## Machine learning models

Logistic regression, random forest, gradient boosting, optional XGBoost/LightGBM, ranking-enhanced classifier with calibration and temporal backtesting.

## Monte Carlo simulation

Repeated full-tournament simulations produce champion and stage-reach probabilities per team.

## Awards predictor

Combines editable player priors with Monte Carlo progression. Outputs are **analytics estimates**, not official FIFA predictions.

## Screenshots

Add demo screenshots under `{C.PORTFOLIO_SCREENSHOTS_DIR}/` (Streamlit pages, Monte Carlo dashboard, awards podium).

## How to run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python main.py
python -m streamlit run app/streamlit_app.py
```

## Reproduce demo outputs

```bash
python scripts/run_final_demo_pipeline.py --simulations 10
```

## Limitations

See `{C.PROJECT_LIMITATIONS_FILE}` — prediction uncertainty, heuristic priors, no live injury/form feeds unless you add them.

## Future improvements

- Date-aware historical FIFA ranking joins
- Richer non-flat priors from curated public stats (manual import)
- Hosted deployment with secrets excluded
"""
    path = PORTFOLIO_DIR / "PORTFOLIO_README.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return text


def generate_demo_script() -> str:
    text = """# FIFA World Cup 2026 AI Predictor — Demo Script (5–7 minutes)

## 1. Intro (30s)

"This project forecasts World Cup 2026 match and tournament outcomes using ML plus Monte Carlo simulation. Award outputs are explainable analytics, not official FIFA predictions."

## 2. Official data readiness (60s)

- Open **13 Official Final Readiness** or homepage status cards
- Show `official_final_enabled=true`, 104 fixtures, 1,248 players
- Mention awards refuse to run without official final mode

## 3. Match predictor (60s)

- Open future match prediction page / API example
- Show probability outputs and explainability note

## 4. Monte Carlo simulation (90s)

- Open **9 Monte Carlo Simulator**
- Show champion probabilities and stage heatmap/report
- Note simulation count affects stability

## 5. Player prior enrichment (60s)

```bash
python scripts/enrich_player_priors.py --update-award-candidates
```

- Explain priors are heuristic unless manually edited
- Show prior quality report path

## 5b. Manual star-player priors (optional, 45s)

```bash
python scripts/generate_world_cup_awards.py --use-enriched --use-manual-priors
```

- Show demo preset `data/templates/player_award_manual_priors_demo.csv`
- Explain manual priors apply only to official candidates (Messi, Mbappé, etc.)

## 6. Awards predictor (90s)

- Open **17 World Cup Awards**
- Show Golden Ball / Boot / Glove podium and candidate source
- Highlight disclaimer banner

## 7. Reports & downloads (30s)

- Download CSV/MD reports from Streamlit or `data/processed/`

## 8. Limitations & closing (30s)

"No betting use. Uncertainty remains. Priors can be improved by editing official player prior files."
"""
    path = PORTFOLIO_DIR / "demo_script.md"
    path.write_text(text, encoding="utf-8")
    return text


def generate_project_architecture_doc() -> str:
    text = """# Project Architecture

## Layers

| Layer | Components |
|-------|------------|
| Data ingestion | Raw/sample match files, Kaggle helpers, manual official imports |
| Official data | Teams, fixtures, squads, priors, readiness, `official_final` gate |
| Feature engineering | Leakage-safe pre-match features, ranking/Elo merge |
| Model training | Baseline, improved, ranking-enhanced joblib artifacts |
| Prediction | Future match API/UI, explainability reports |
| Simulation | Group stage, knockout, full tournament orchestrator |
| Monte Carlo | Repeated simulations → stage/champion probabilities |
| Awards | Official candidates + priors + progression → award estimates |
| Reporting | Markdown/CSV summaries, Streamlit dashboards, portfolio pack |

## Data flow (awards)

```
official_players.csv + player_award_priors.csv
        ↓
official_award_candidates.csv
        ↓ (Step 19 enrich)
enriched_official_award_candidates.csv
        ↓ (Step 20 optional manual overrides)
manual prior CSV (official player IDs only)
        ↓
Monte Carlo team stage probabilities
        ↓
world_cup_awards_predictions.csv + reports
```

## Entry points

- `python main.py` — core ML pipeline
- `python scripts/run_monte_carlo.py` — tournament simulation batch
- `python scripts/generate_world_cup_awards.py --use-enriched` — awards
- `python -m streamlit run app/streamlit_app.py` — dashboard
"""
    path = PORTFOLIO_DIR / "project_architecture.md"
    path.write_text(text, encoding="utf-8")
    return text


def generate_limitations_doc() -> str:
    text = """# Limitations

- **Prediction uncertainty** — Models trained on historical data; future form/injuries not fully captured.
- **Official data updates** — FIFA schedules/squads may change; re-run import and readiness workflows.
- **Model scope** — Snapshot rankings in some experiments; strict backtests need date-aware joins.
- **Award priors** — Mostly heuristic position/role defaults unless manually curated; not official season stats.
- **Manual prior overrides (Step 20)** — Optional user-provided boosts for portfolio demos; never add unofficial players.
- **No live feeds** — No automatic injury/form scraping; user must update priors manually.
- **Proxy awards** — Player of the Match / Goal of the Tournament are analytics proxies, not fan-vote forecasts.
- **Not official FIFA** — All award outputs are explainable analytics estimates.
- **No betting use** — Educational sports-analytics project only.
"""
    path = PORTFOLIO_DIR / "limitations.md"
    path.write_text(text, encoding="utf-8")
    return text


def generate_deployment_guide() -> str:
    text = """# Deployment Guide

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Streamlit

```bash
python -m streamlit run app/streamlit_app.py --server.port 8501
```

## Environment notes

- Python 3.12+ recommended (see README)
- Model/joblib artifacts generated locally — not all committed
- Official data under `data/official/` — promote `official_final` only after readiness passes

## Kaggle credentials

If using `scripts/download_kaggle_datasets.py`, store `kaggle.json` outside the repo and never commit credentials.

## Streamlit Community Cloud (optional)

- Deploy from GitHub with `requirements.txt`
- Exclude secrets and large raw files via `.gitignore`
- Run `main.py` or ship pre-built artifacts as release assets for faster demos
- Set startup command: `streamlit run app/streamlit_app.py`

## Demo pipeline

```bash
python scripts/run_final_demo_pipeline.py --simulations 10
```
"""
    path = PORTFOLIO_DIR / "deployment_guide.md"
    path.write_text(text, encoding="utf-8")
    return text


def generate_reproducibility_checklist() -> str:
    text = """# Reproducibility Checklist

- [ ] Clone repo and create venv
- [ ] `pip install -r requirements.txt`
- [ ] `python main.py` (or use committed model artifacts if available)
- [ ] Verify official data applied: `python scripts/evaluate_official_final_readiness.py`
- [ ] Confirm `official_final_enabled=true` if awards required
- [ ] `python scripts/run_monte_carlo.py --simulations 10 --seed 42`
- [ ] `python scripts/enrich_player_priors.py --update-award-candidates`
- [ ] `python scripts/generate_world_cup_awards.py --use-enriched`
- [ ] (Optional) `python scripts/generate_world_cup_awards.py --use-enriched --use-manual-priors`
- [ ] `python scripts/prepare_final_project_pack.py`
- [ ] `python -m pytest -q`
- [ ] `python -m streamlit run app/streamlit_app.py`
"""
    path = PORTFOLIO_DIR / "reproducibility_checklist.md"
    path.write_text(text, encoding="utf-8")
    return text


def prepare_step19_portfolio_pack() -> dict[str, Any]:
    """Generate all Step 19 portfolio documents."""
    dirs = ensure_portfolio_dirs()
    paths = {
        "portfolio_readme": str(PORTFOLIO_DIR / "PORTFOLIO_README.md"),
        "demo_script": str(PORTFOLIO_DIR / "demo_script.md"),
        "architecture": str(PORTFOLIO_DIR / "project_architecture.md"),
        "limitations": str(PORTFOLIO_DIR / "limitations.md"),
        "deployment_guide": str(PORTFOLIO_DIR / "deployment_guide.md"),
        "reproducibility_checklist": str(PORTFOLIO_DIR / "reproducibility_checklist.md"),
    }
    generate_portfolio_readme()
    generate_demo_script()
    generate_project_architecture_doc()
    generate_limitations_doc()
    generate_deployment_guide()
    generate_reproducibility_checklist()
    return {"status": "ok", **dirs, **paths}
