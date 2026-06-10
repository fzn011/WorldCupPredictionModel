# FIFA World Cup 2026 AI Predictor — Portfolio Overview

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

Add demo screenshots under `portfolio/screenshots/` (Streamlit pages, Monte Carlo dashboard, awards podium).

## How to run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
python -m streamlit run app/streamlit_app.py
```

## Reproduce demo outputs

```bash
python scripts/run_final_demo_pipeline.py --simulations 10
```

## Limitations

See `portfolio/limitations.md` — prediction uncertainty, heuristic priors, no live injury/form feeds unless you add them.

## Future improvements

- Date-aware historical FIFA ranking joins
- Richer non-flat priors from curated public stats (manual import)
- Hosted deployment with secrets excluded
