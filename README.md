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
- [Step 6: Model Improvement Part 1](#step-6-model-improvement-part-1)
- [Step 7: FIFA Rankings and Elo Integration](#step-7-fifa-rankings-and-elo-integration)
- [Step 8: Future Match Feature Generator](#step-8-future-match-feature-generator)
- [Step 10: Match Prediction Explainability](#step-10-match-prediction-explainability)
- [Step 11: Tournament Fixture and Group Setup](#step-11-tournament-fixture-and-group-setup)
- [Step 12: Group-Stage Simulation Engine](#step-12-group-stage-simulation-engine)
- [Step 15: Monte Carlo Tournament Simulator](#step-15-monte-carlo-tournament-simulator)

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

## Step 6: Model Improvement Part 1

Step 6 improves the baseline model layer for probability-focused forecasting.

- **XGBoost** and **LightGBM** are optional and are skipped gracefully when unavailable.
- **HistGradientBoostingClassifier** is always trained as the safe fallback.
- **Probability calibration** is applied (sigmoid) to improve probability reliability.
- **Temporal backtesting** is run across multiple chronological windows.
- **Baseline vs improved comparison reports** are saved under `reports/`.
- The best improved model is saved under `models/improved/`.

### Step 6 commands

```bash
python scripts/train_improved_models.py
python scripts/inspect_improved_model_results.py
python main.py
python -m pytest -q
```

## Step 7: FIFA Rankings and Elo Integration

Step 7 adds external team-strength signals from FIFA rankings and Elo ratings.

- FIFA ranking and Elo snapshot features are merged into the feature dataset.
- Team-level strength score is computed from normalized FIFA points and Elo.
- Ranking-enhanced dataset is saved under `data/processed/`.
- Ranking-enhanced model is trained and saved under `models/ranking_enhanced/`.
- Step 7 reports are saved under `reports/`.
- Snapshot-ranking limitation is documented in metadata and summaries.

### Snapshot limitation

This Step 7 version is a **snapshot ranking experiment**: latest available
FIFA/Elo snapshots are applied across historical rows. For strict historical
backtesting, date-aware historical ranking joins should be added in a later
refinement.

### Step 7 commands

```bash
python scripts/prepare_ranking_features.py
python scripts/inspect_ranking_features.py
python scripts/train_ranking_enhanced_model.py
python scripts/inspect_ranking_model_results.py
python main.py
python -m pytest -q
```

## Step 8: Future Match Feature Generator

Step 8 enables **real arbitrary future match prediction** by generating a fresh
pre-match feature row at inference time.

- Arbitrary future match prediction is now supported.
- Historical features are generated from matches strictly before the selected match date.
- Ranking/Elo snapshot features are added when available.
- The best available model is used in this order:
	`ranking_enhanced -> improved -> baseline`.
- Future predictions are no longer placeholders.
- CLI scripts are available for inspection and prediction.

### Step 8 commands

```bash
python scripts/inspect_future_feature_row.py --team-a Argentina --team-b France --date 2026-06-11
python scripts/predict_future_match.py --team-a Argentina --team-b France --date 2026-06-11 --tournament "FIFA World Cup" --neutral 1
python -m pytest -q
python -m streamlit run app/streamlit_app.py
```

## Step 10: Match Prediction Explainability

Step 10 adds **local prediction explanations** for future match predictions.

- Local explanations are generated from the actual future feature row and saved model.
- **SHAP** is used when available and compatible with the selected model.
- If SHAP is unavailable/incompatible, a **model-agnostic local sensitivity fallback** is used.
- Natural-language explanation text is generated for faster interpretation.
- Global feature-importance inspection is available via CLI.
- Explanation artifacts are saved under `reports/`.

### Step 10 commands

```bash
python scripts/explain_future_match.py --team-a Argentina --team-b France --date 2026-06-11 --tournament "FIFA World Cup" --neutral 1
python scripts/inspect_global_explanation.py
python -m pytest -q
python -m streamlit run app/streamlit_app.py
uvicorn api.main:app --reload
```

## Step 11: Tournament Fixture and Group Setup

Step 11 builds simulation-ready tournament infrastructure for the 2026 format.

- 48 teams, 12 groups, 4 teams per group.
- Group-stage fixtures are generated/validated from editable group slots.
- 72 group-stage fixtures are prepared (6 per group).
- Knockout placeholders are created for Round of 32 through Final.
- Output files are saved under `data/processed/`.
- This step **does not** simulate results or predict standings.

> The sample group and schedule CSV files are intentionally editable templates.
> Update them from official FIFA sources when final data is available.

### Step 11 commands

```bash
python scripts/prepare_tournament_setup.py
python scripts/inspect_tournament_setup.py
python -m pytest -q
python -m streamlit run app/streamlit_app.py
```

## Step 12: Group-Stage Simulation Engine

Step 12 simulates all **72 group-stage fixtures** using the trained match prediction system.

- Uses `predict_future_match()` per fixture to get win/draw/loss probabilities.
- Samples realistic outcomes from model probabilities (instead of always taking argmax).
- Generates transparent approximate scorelines for table metrics.
- Builds group tables and rankings.
- Selects top two from each group + best eight third-placed teams.
- Produces a Round-of-32 qualifier list.
- Does **not** simulate knockout rounds yet.

### Step 12 commands

```bash
python scripts/simulate_group_stage.py --seed 42
python scripts/inspect_group_stage_results.py
python -m pytest -q
python -m streamlit run app/streamlit_app.py
```

## Step 13: Knockout Simulation Engine

Step 13 simulates one complete knockout bracket from the 32 Round-of-32 qualifiers produced in Step 12.

- Consumes the saved Round-of-32 qualifier list.
- Creates a deterministic simulation seed-order bracket.
- Simulates Round of 32, Round of 16, Quarter-finals, Semi-finals, Third-place match, and Final.
- Uses no-draw adjusted probabilities so every knockout match has a winner.
- Produces champion, runner-up, third place, and fourth place for one tournament run.
- Saves the filled bracket, simulated matches, single-tournament result, summary, and validation report.
- Does **not** run Monte Carlo yet.
- Does **not** produce champion probabilities yet.

### Step 13 commands

```bash
python scripts/simulate_knockout_stage.py --seed 42
python scripts/inspect_knockout_results.py
python -m pytest -q
python -m streamlit run app/streamlit_app.py
```

## Step 14: Full Tournament Single-Run Orchestrator

Step 14 combines the Step 12 group-stage simulation and Step 13 knockout simulation into one complete sampled tournament run.

- Runs group-stage simulation and selects Round-of-32 qualifiers.
- Passes fresh in-memory qualifiers directly into the knockout simulator.
- Produces one full tournament path from group stage to champion.
- Saves champion, runner-up, third place, and fourth place.
- Saves full match logs, stage summaries, path reports, and validation reports.
- This is **not** Monte Carlo yet and does **not** produce probability tables.
- Monte Carlo simulation will be added in Step 15.

### Step 14 commands

```bash
python scripts/simulate_full_tournament.py --seed 42
python scripts/inspect_full_tournament_results.py
python -m pytest -q
python -m streamlit run app/streamlit_app.py
```

## Step 15: Monte Carlo Tournament Simulator

Step 15 repeats the full tournament single-run simulation many times and aggregates probability estimates.

- Repeats full tournament simulation for a configurable number of runs.
- Produces champion probabilities.
- Produces stage progression probabilities.
- Produces finalists and semifinalists frequency tables.
- Saves summary and validation reports to `data/processed/`.
- Default simulation count is **100** for local development.
- Larger simulation counts can be run later after performance optimization.
- Results are simulation estimates, not certainties.

### Step 15 commands

```bash
python scripts/run_monte_carlo.py --simulations 100 --seed 42
python scripts/inspect_monte_carlo_results.py
python -m pytest -q
python -m streamlit run app/streamlit_app.py
```

