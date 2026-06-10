# FIFA World Cup 2026 AI Predictor

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-65%20passed-brightgreen)](./tests)
[![Pipeline](https://img.shields.io/badge/pipeline-Step%205%20baseline-success)](#step-5-baseline-match-result-model)
[![Upstream](https://img.shields.io/badge/upstream-WorldCupPredictionModel-black)](https://github.com/fzn011/WorldCupPredictionModel)

A machine learning and simulation-based dashboard that predicts FIFA World Cup
2026 match outcomes, tournament progression, champion probabilities, and
Golden Ball / best player candidates.

## Quick Navigation

- [Full project reference (CHAT_HISTORY.md)](CHAT_HISTORY.md) · [docs/PROJECT_REFERENCE.md](docs/PROJECT_REFERENCE.md)
- [Upstream repository](#upstream-repository)
- [Step 6: Model Improvement Part 1](#step-6-model-improvement-part-1)
- [Step 7: FIFA Rankings and Elo Integration](#step-7-fifa-rankings-and-elo-integration)
- [Step 8: Future Match Feature Generator](#step-8-future-match-feature-generator)
- [Step 10: Match Prediction Explainability](#step-10-match-prediction-explainability)
- [Step 11: Tournament Fixture and Group Setup](#step-11-tournament-fixture-and-group-setup)
- [Step 12: Group-Stage Simulation Engine](#step-12-group-stage-simulation-engine)
- [Step 15: Monte Carlo Tournament Simulator](#step-15-monte-carlo-tournament-simulator)
- [Step 16: Monte Carlo Dashboard and Report Polish](#step-16-monte-carlo-dashboard-and-report-polish)
- [Step 17A: Official World Cup 2026 Data Lock](#step-17a-official-world-cup-2026-data-lock)

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
- Uses cached match predictions across simulations for better local runtime.
- Default simulation count is **100** for local development.
- First verification run should use **10 simulations**.
- Larger simulation counts can be run later after performance optimization.
- Results are simulation estimates, not certainties.

### Step 15 commands

```bash
python scripts/run_monte_carlo.py --simulations 100 --seed 42
python scripts/inspect_monte_carlo_results.py
python -m pytest -q
python -m streamlit run app/streamlit_app.py
```

## Step 16: Monte Carlo Dashboard and Report Polish

Step 16 makes the Monte Carlo outputs more visual, transparent, and portfolio-ready.

- Champion probability visualization added.
- Stage progression heatmap/table added.
- Summary cards added.
- Markdown report generation added.
- Downloadable dashboard export added.
- Results remain simulation estimates, not certainties.

### Step 16 commands

```bash
python scripts/run_monte_carlo.py --simulations 10 --seed 42
python scripts/generate_monte_carlo_report.py
python scripts/inspect_monte_carlo_report.py
python -m pytest -q
python -m streamlit run app/streamlit_app.py
```

## Step 17A: Official World Cup 2026 Data Lock

Step 17A prevents predictions and simulations from silently using teams, fixtures, venues, or later players that are not officially part of the World Cup 2026 data contract.

- Adds an `data/official/` folder structure for raw, processed, and report-layer official data.
- Adds official teams/groups/fixtures/venues/match-calendar contracts.
- Adds official data validation and summary reports.
- Adds official mode vs sample mode support.
- Match prediction can restrict teams to the official World Cup 2026 team list.
- If current local files are generated from placeholders, they are clearly marked as `sample_to_be_verified` and must be manually checked against FIFA.

### Important follow-up note

- The future awards predictor must use `official_players.csv` from Step 17B.
- Sample player candidates are not allowed in official mode.
- Player award priors must later be joined to official squad players only.

### Step 17A commands

```bash
python scripts/prepare_official_worldcup_data.py
python scripts/inspect_official_worldcup_data.py
python -m pytest -q
python -m streamlit run app/streamlit_app.py
```

## Step 17D: Official Data Population Pack

Step 17D creates a complete manual data population workflow for verified FIFA World Cup 2026 data.

- Generates manual import templates under `data/official/import_templates/`.
- Generates a master workbook for official data entry.
- Generates a population guide with step-by-step instructions.
- Creates missing-data reports and import preview/diff tools.
- Supports safe import application with backups and audit logs.
- Supports `official_final` promotion only when readiness passes.
- Does **not** scrape, OCR, or auto-fetch data.
- Does **not** fake official data or mark unverified rows as verified.
- Keeps sample and official-draft modes separate.

> **Warning:** `promote_official_final.py --confirm` should only succeed when official
> readiness is fully complete. If current data still has 72 fixtures and about 65 players,
> promotion should remain blocked. That is correct behavior.

### Step 17D commands

```bash
python scripts/prepare_official_population_pack.py
python scripts/generate_official_import_templates.py

# Preview before applying (always preview first)
python scripts/preview_official_import.py --target teams    --file data/official/import_templates/official_teams_import_template.csv
python scripts/preview_official_import.py --target players  --file data/official/import_templates/official_players_import_template.csv

# Apply in dependency order: teams → groups → venues → fixtures → players → player_priors
python scripts/apply_official_import.py --target teams         --file data/official/import_templates/official_teams_import_template.csv    --preview
python scripts/apply_official_import.py --target teams         --file data/official/import_templates/official_teams_import_template.csv
python scripts/apply_official_import.py --target groups        --file data/official/import_templates/official_groups_import_template.csv
python scripts/apply_official_import.py --target venues        --file data/official/import_templates/official_venues_import_template.csv
python scripts/apply_official_import.py --target fixtures      --file data/official/import_templates/official_fixtures_import_template.csv
python scripts/apply_official_import.py --target players       --file data/official/import_templates/official_players_import_template.csv
python scripts/apply_official_import.py --target player_priors --file data/official/import_templates/player_award_priors_import_template.csv

python scripts/evaluate_official_final_readiness.py
python scripts/promote_official_final.py
python scripts/promote_official_final.py --confirm
python -m pytest -q
python -m streamlit run app/streamlit_app.py
```

## Step 17E: Fill and Verify Official Teams, Groups, Venues, and Fixtures

> **Data population step — no code changes required.**

Fill these four templates from verified FIFA sources before touching players or awards.

### Target after Step 17E

| Dataset | Required | Source template |
|---------|----------|-----------------|
| Teams | 48 rows | `official_teams_import_template.csv` |
| Groups | 48 rows (12 × 4) | `official_groups_import_template.csv` |
| Venues | 16+ rows | `official_venues_import_template.csv` |
| Fixtures | 104 rows (72 group + 32 KO) | `official_fixtures_import_template.csv` |

Templates live in `data/official/import_templates/`.

### Step 17E fill order

1. **Teams** — 48 qualified nations, group assignments, confederation, host flags
2. **Groups** — 12 groups × 4 teams; must match teams file exactly
3. **Venues** — stadiums, cities, countries, timezones, capacity
4. **Fixtures** — all 104 matches; kickoff times (local + UTC), venue, team codes

### Step 17E apply commands

```bash
python scripts/apply_official_import.py --target teams    --file data/official/import_templates/official_teams_import_template.csv    --preview
python scripts/apply_official_import.py --target teams    --file data/official/import_templates/official_teams_import_template.csv
python scripts/apply_official_import.py --target groups   --file data/official/import_templates/official_groups_import_template.csv
python scripts/apply_official_import.py --target venues   --file data/official/import_templates/official_venues_import_template.csv
python scripts/apply_official_import.py --target fixtures --file data/official/import_templates/official_fixtures_import_template.csv
python scripts/evaluate_official_final_readiness.py
```

### Step 17E checklist

- [ ] 48 teams, no `sample_to_be_verified`
- [ ] 12 groups, each with exactly 4 teams
- [ ] Groups match teams (team names identical)
- [ ] 16+ venues with city, country, timezone
- [ ] 72 group-stage fixtures with kickoff times
- [ ] 32 knockout fixtures/placeholders
- [ ] No blocking placeholder values in any of the above

---

## Step 17F: Fill and Verify Official Squads and Player Priors

> **Data population step — no code changes required. Requires Step 17E to pass first.**

### Target after Step 17F

| Dataset | Required |
|---------|----------|
| Players | 1,248 rows (48 × 26) |
| Teams with full squads | 48 / 48 |
| Player priors | 1,248 rows |
| `sample_to_be_verified` rows | 0 |
| Blocking placeholders | 0 |

### Step 17F fill order

5. **Players** — 26 players per team; shirt number, position, DOB, club
6. **Player priors** — editable estimates for the awards model (fill after players)

### Step 17F apply commands

```bash
python scripts/apply_official_import.py --target players       --file data/official/import_templates/official_players_import_template.csv --preview
python scripts/apply_official_import.py --target players       --file data/official/import_templates/official_players_import_template.csv
python scripts/apply_official_import.py --target player_priors --file data/official/import_templates/player_award_priors_import_template.csv
python scripts/evaluate_official_final_readiness.py
python scripts/promote_official_final.py --confirm
```

### Step 17F checklist

- [ ] 1,248 players across 48 squads
- [ ] 26 players per team exactly
- [ ] No `sample_to_be_verified` players
- [ ] Player priors filled for all official squad players
- [ ] `official_final` promotion succeeds

---

## Step 18: FIFA World Cup Awards Predictor

> **Code step — blocked until Steps 17E and 17F are complete and `official_final = true`.**

Awards predictions (Golden Ball, Golden Boot, Golden Glove, Young Player, Team of the Tournament)
are only trustworthy when official squads are complete. Do not implement Step 18 while
`official_final_enabled = false`.

