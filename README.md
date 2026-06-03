# FIFA World Cup 2026 AI Predictor

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-65%20passed-brightgreen)](./tests)
[![Pipeline](https://img.shields.io/badge/pipeline-Step%205%20baseline-success)](#step-5-baseline-match-result-model)
[![Upstream](https://img.shields.io/badge/upstream-WorldCupPredictionModel-black)](https://github.com/fzn011/WorldCupPredictionModel)

A machine learning and simulation-based dashboard that predicts FIFA World Cup
2026 match outcomes, tournament progression, champion probabilities, and
Golden Ball / best player candidates.

## Quick Navigation

- [Upstream repository](#upstream-repository)
- [Current Status](#current-status)
- [Step 5: Baseline Match Result Model](#step-5-baseline-match-result-model)
- [Future Roadmap](#future-roadmap)

## Current Snapshot

- Feature rows: **32,179**
- Feature columns: **125**
- Train/Test split (Step 5): **27,719 / 4,460**
- Baseline models: **Dummy, Logistic Regression, Random Forest**
- Current best baseline: **Random Forest**
- Tests: **65 passed**

## Upstream repository

This workspace is now being maintained alongside the GitHub repository below:

- https://github.com/fzn011/WorldCupPredictionModel.git

When the upstream repo changes, I’ll treat it as the reference source for
future updates in this project.

## Project Description

This project combines historical international football data, FIFA rankings,
Elo ratings, and recent team form to build predictive models. A Monte Carlo
tournament simulator then projects how the World Cup 2026 might unfold across
the group stage and knockout rounds.

## Main Objective

Build a clean, transparent, portfolio-quality ML pipeline that can:

- Predict the result of any international football match.
- Estimate the most likely scoreline.
- Simulate the full World Cup 2026 thousands of times.
- Estimate per-team champion probabilities.
- Predict Golden Ball / best player candidates.
- Explain its predictions using feature importance and SHAP values.

## Planned Features

- Match result probabilities (win / draw / loss).
- Expected goals and most likely scoreline.
- Round-by-round team progression probabilities.
- Champion probability rankings.
- Best player / Golden Ball candidate ranking.
- Model evaluation and explainability dashboard.

## Machine Learning Approach

- Baseline: Logistic Regression / Random Forest on engineered match features.
- Advanced: Gradient boosting (XGBoost, LightGBM) with calibrated probabilities.
- Score model: Poisson / bivariate Poisson for expected goals.
- Simulation: Monte Carlo with 10,000+ tournament runs.
- Explainability: Feature importance and SHAP values.

## Dataset Plan

Planned data sources (to be integrated in later steps):

- International match results (historical).
- FIFA world rankings.
- Elo ratings for national teams.
- Player-level statistics for the Golden Ball model.
- World Cup 2026 group draw and schedule.

> Step 1 ships with a small synthetic sample dataset only.

## Project Structure

```
world-cup-2026-ai-predictor/
├── data/              # raw, processed, external, sample
├── notebooks/         # exploration and modeling notebooks
├── src/               # source code (data, features, models, simulation, players, utils)
├── app/               # Streamlit dashboard
├── models/            # trained model artifacts
├── reports/           # generated reports and figures
├── tests/             # pytest tests
├── requirements.txt
├── config.yaml
├── main.py
└── README.md
```

## Setup

```bash
# 1. Create a virtual environment
python -m venv .venv

# 2. Activate it
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Run the Pipeline

```bash
python main.py
```

## Run the Streamlit App

```bash
streamlit run app/streamlit_app.py
```

## Run the Tests

```bash
python -m pytest -q
```

## Current Status

- **Step 1 completed** — project foundation and GitHub-ready structure.
- **Step 2 completed** — dataset collection and data-source setup.
- **Step 3 completed** — cleaned canonical dataset + shootout handling.
- **Step 4 completed** — leakage-safe historical feature engineering.
- **Step 5 completed** — trained baseline models with chronological evaluation.

Current best baseline model is **Random Forest**, saved at:
`models/baseline/best_baseline_model.joblib`.

## Step 2: Dataset Collection and Data Source Setup

- Real datasets are expected inside `data/raw/`:
  - `data/raw/matches/results.csv` — historical international matches.
  - `data/raw/rankings/fifa_rankings.csv` and `elo_ratings.csv`.
  - `data/raw/world_cup_2026/world_cup_2026_{teams,groups,schedule}.csv`.
- Sample fallback datasets live under `data/sample/` and are used
  automatically whenever a real file is missing.
- CSV templates with the expected headers live under `data/external/`.
- Dataset documentation lives in [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md)
  and [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md).
- The project does **not** scrape any website and does **not** require any
  API key. Real datasets are placed manually.
- This step prepares the project for feature engineering and model training.

### Useful commands

```bash
python scripts/check_datasets.py
python scripts/download_kaggle_datasets.py   # optional, requires Kaggle credentials
python main.py
python -m pytest -q
python -m streamlit run app/streamlit_app.py
```

### Optional: automatic Kaggle download

If you have a Kaggle account, you can auto-download the historical match
dataset (`martj42/international-football-results-from-1872-to-2017`) into
`data/raw/matches/` instead of placing the file manually:

1. At https://www.kaggle.com/settings click **Create New API Token** to
   download `kaggle.json`.
2. Place it at `%USERPROFILE%\.kaggle\kaggle.json` (Windows) or
   `~/.kaggle/kaggle.json` (macOS/Linux). **Do not** put it inside this repo.
3. Run `python scripts/download_kaggle_datasets.py`.

If credentials are missing, the script exits cleanly with setup instructions
and the project continues using the sample fallback under `data/sample/`.
`kaggle.json`, `.kaggle/`, and `*.zip` are already in `.gitignore`.

## Step 3: Data Cleaning and Canonical Dataset

This step deep-cleans the raw historical results and penalty shootouts, then
builds a single **canonical match dataset** plus a **team registry**. Real
Kaggle data is used when present; otherwise the bundled sample data is used.

What the cleaning pipeline does:

- Standardizes team names (e.g. `USA` → `United States`, `Korea Republic` →
  `South Korea`) and generates URL-safe team slugs.
- Parses dates, coerces scores to non-negative integers, and drops invalid
  or duplicate rows.
- Builds the canonical schema with derived fields: `result`/`result_label`,
  `winner`/`loser`, `score_difference`, `total_goals`, `is_draw`, etc.
- Merges penalty shootouts: drawn matches with a shootout keep `result =
  draw` but record `has_shootout`, `shootout_winner`/`shootout_loser`, and a
  `progression_winner`.
- Creates a team registry (first/last match dates, matches played, WC2026
  host flag).

Processed outputs are written to `data/processed/`:

- `canonical_matches.csv` (real data) or `canonical_matches_sample.csv`
  (sample fallback).
- `team_registry.csv`
- `shootout_outcomes.csv`
- `data_quality_report.csv`
- `cleaning_summary.json`

This step does **not** train models, engineer advanced features, run
simulations, or scrape any website.

### Useful commands

```bash
python main.py                          # run the Step 3 cleaning pipeline
python scripts/inspect_clean_data.py    # inspect the processed datasets
python -m pytest -q
python -m streamlit run app/streamlit_app.py
```

## Step 4: Feature Engineering Part 1

Step 4 turns the cleaned canonical matches into a **machine-learning-ready**
feature dataset while avoiding data leakage. Every historical feature is
computed using only matches before the current match date.

What this step adds:

- Leakage-safe historical team features for Team A and Team B.
- Recent-form windows using the last 5 and last 10 matches.
- Goals scored / conceded averages, win/draw/loss rates, and points per match.
- Difference features between Team A and Team B.
- Match context flags such as friendly, World Cup, qualifier, and major
  tournament indicators.
- 2026 host flags for Canada, Mexico, and the United States.

Processed outputs are written to `data/processed/`:

- `feature_dataset.csv` or `feature_dataset_sample.csv`
- `feature_quality_report.csv`
- `feature_summary.json`

### Useful commands

```bash
python main.py
python scripts/inspect_features.py
python -m pytest -q
python -m streamlit run app/streamlit_app.py
```

## Step 5: Baseline Match Result Model

Step 5 trains the first real multiclass classifiers on the leakage-safe
feature dataset. The split is chronological so that the model is always
trained on the past and evaluated on the future.

What this step adds:

- Chronological train/test split with a default boundary of `2022-01-01`.
- Leakage-safe numeric feature selection.
- Dummy baseline, Logistic Regression, and Random Forest models.
- Metrics including accuracy, macro F1, weighted F1, log loss, and
  multi-class Brier score.
- Saved model artifacts under `models/baseline/`.
- Evaluation reports under `reports/`.

Processed outputs are written to:

- `models/baseline/best_baseline_model.joblib`
- `models/baseline/feature_columns.json`
- `reports/model_metrics.csv`
- `reports/feature_importance_random_forest.csv`

### Useful commands

```bash
python scripts/train_baseline_models.py
python scripts/inspect_model_results.py
python main.py
python -m pytest -q
```

## Future Roadmap

- **Step 2:** Real data ingestion and cleaning (historical matches, rankings).
- **Step 3:** Canonical match cleaning and shootout handling.
- **Step 4:** Feature engineering (Elo, form, ranking diff, venue, etc.).
- **Step 5:** Baseline match-result model + evaluation.
- **Step 6:** Advanced gradient boosting model + calibration.
- **Step 7:** Score / expected-goals model.
- **Step 8:** Full Monte Carlo World Cup 2026 simulator.
- **Step 9:** Golden Ball / best player model.
- **Step 10:** Streamlit dashboard polish + SHAP explainability.
- **Step 11:** Deployment and documentation.

## Disclaimer

This is a sports analytics and educational project. It is **not** betting
advice. All predictions are probabilistic estimates based on historical data
and modeling assumptions.
