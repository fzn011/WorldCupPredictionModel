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

## Step 17E: Source-Assisted Official FIFA Data Population

Step 17E adds a **source-assisted** population system that helps fill official World Cup 2026 data using **official FIFA URLs only** (plus manual CSV/XLSX fallback).

- Uses official FIFA source URLs only (`fifa.com`, `fdp.fifa.org`) — no whole-internet scraping.
- Saves raw HTML snapshots for auditability under `data/official/source_data/raw/`.
- Parses what can be parsed defensively; **does not fake** missing teams, fixtures, venues, or players.
- Supports manual CSV/XLSX and master workbook ingestion into **staging** before apply.
- Validates staged data against existing contracts before import.
- Exports a downloadable import pack ZIP.
- Applies staged data only through the existing safe import workflow (`apply_staged_official_data.py`).
- **`official_final` remains blocked** until all 15 readiness checks pass — this is correct.

> If FIFA pages are dynamic or parsing is partial, use the manual workbook path:
> `python scripts/ingest_manual_official_file.py --target workbook --file data/official/population/workbooks/official_worldcup_2026_master_import.xlsx`

### Step 17E workflow order

1. **17E-1** — Populate official teams and groups (staging)
2. **17E-2** — Populate official venues and stadium metadata
3. **17E-3** — Populate all 104 fixtures
4. **17E-4** — Populate official squads and players
5. **17E-5** — Populate editable player priors from official players
6. **17E-6** — Run readiness; promote only if `final_ready=true`

### Step 17E commands

```bash
python scripts/prepare_source_population.py
python scripts/prepare_source_population.py --download
python scripts/export_official_import_pack.py

python scripts/ingest_manual_official_file.py --target workbook --file data/official/population/workbooks/official_worldcup_2026_master_import.xlsx

python scripts/apply_staged_official_data.py --target all --preview
python scripts/apply_staged_official_data.py --target all --apply

python scripts/evaluate_official_final_readiness.py
python -m pytest -q
python -m streamlit run app/streamlit_app.py
```

### Step 17E outputs

| Artifact | Path |
|----------|------|
| Source registry | `data/official/source_data/official_source_registry.json` |
| Snapshot manifest | `data/official/source_data/official_source_snapshot_manifest.json` |
| Staged teams | `data/official/source_data/staging/staged_official_teams.csv` |
| Staged fixtures | `data/official/source_data/staging/staged_official_fixtures.csv` |
| Staged venues | `data/official/source_data/staging/staged_official_venues.csv` |
| Staged players | `data/official/source_data/staging/staged_official_players.csv` |
| Parse report | `data/official/source_data/reports/official_source_parse_report.csv` |
| Staging validation | `data/official/source_data/reports/official_staging_validation_report.csv` |
| Population summary | `data/official/source_data/reports/official_source_population_summary.json` |
| Import pack ZIP | `data/official/source_data/exports/official_worldcup_2026_import_pack.zip` |

---

## Step 17F: Populate Official FIFA World Cup Data

Step 17F consumes official FIFA schedule/squad files, staged Step 17E data, or saved FIFA snapshots to build **populated official import files**.

- Builds populated datasets under `data/official/populated/`.
- Checks completeness against final targets (48 teams, 104 fixtures, 1,248 players).
- Creates an official-ready import pack ZIP.
- Does **not** fake missing values or bypass readiness.
- Applies populated data only when `population_is_ready_for_apply` is true.
- **`official_final` remains blocked** while data is incomplete — correct behavior.
- **Step 18 Awards must wait** until `official_final` is ready.

### Step 17F commands

```bash
python scripts/prepare_populated_official_data.py
python scripts/import_fifa_schedule_file.py --file path/to/fifa_schedule.xlsx
python scripts/import_fifa_squad_file.py --file path/to/fifa_squads.csv
python scripts/prepare_populated_official_data.py --schedule-file path/to/fifa_schedule.xlsx --squad-file path/to/fifa_squads.csv
python scripts/apply_populated_official_data.py --preview
python scripts/apply_populated_official_data.py --apply
python scripts/evaluate_official_final_readiness.py
python -m pytest -q
python -m streamlit run app/streamlit_app.py
```

### Step 17F outputs

| Artifact | Path |
|----------|------|
| Populated teams | `data/official/populated/populated_official_teams.csv` |
| Populated groups | `data/official/populated/populated_official_groups.csv` |
| Populated fixtures | `data/official/populated/populated_official_fixtures.csv` |
| Populated venues | `data/official/populated/populated_official_venues.csv` |
| Populated players | `data/official/populated/populated_official_players.csv` |
| Populated priors | `data/official/populated/populated_player_award_priors.csv` |
| Completeness report | `data/official/populated/reports/official_population_completeness_report.csv` |
| Final summary | `data/official/populated/reports/official_population_final_summary.json` |
| Import pack ZIP | `data/official/populated/exports/official_ready_import_pack.zip` |

---

## Step 17G: Official Data Import Execution

Step 17G runs the **actual official data import workflow** using existing Step 17E–17F tooling.

- Accepts official FIFA schedule/squad files or the master import workbook.
- Stages data safely, validates it, previews diffs, and applies **only when ready**.
- Rebuilds squads/award candidates and re-runs final readiness after apply.
- Fixes future-match team dropdown behavior (`get_available_teams(official_only=...)`).
- Does **not** build awards or fake `official_final`.
- **Step 18 remains blocked** until `final_ready=true`.

### Step 17G commands

```bash
python scripts/fix_and_check_future_team_filter.py
python -m pytest tests/test_future_match_features.py -q
python scripts/run_official_import_execution.py
python scripts/run_official_import_execution.py --schedule-file path/to/fifa_schedule.xlsx --squad-file path/to/fifa_squads.csv
python scripts/run_official_import_execution.py --workbook-file data/official/population/workbooks/official_worldcup_2026_master_import.xlsx
python scripts/run_official_import_execution.py --schedule-file path --squad-file path --apply
python scripts/evaluate_official_final_readiness.py
python -m pytest -q
python -m streamlit run app/streamlit_app.py
```

### Step 17G outputs

| Artifact | Path |
|----------|------|
| Import execution summary | `data/official/populated/reports/official_import_execution_summary.json` |
| Completeness report | `data/official/populated/reports/official_population_completeness_report.csv` |
| Final readiness report | `data/official/processed/official_final_readiness_report.json` |
| Final readiness checklist | `data/official/processed/official_final_readiness_checklist.csv` |

---

## Step 17H: Official Data Apply Blocker Cleanup

Step 17H cleans up remaining blockers after imported FIFA schedule/squad data is staged in populated CSVs.

- Normalizes FIFA stage labels like **First Stage** → `group_stage`.
- Rebuilds teams/groups from verified imported schedule when possible (48 teams, 12 groups).
- Cleans source labels for verified imports (`fifa_schedule_api`, `fifa_squad_pdf`, etc.).
- Separates **true blockers** from optional metadata warnings (capacity, lat/long, height).
- Fixes official team dropdown count via populated-team preference in `get_official_team_list()`.
- Does **not** bypass readiness or build awards.

### Step 17H commands

```bash
python scripts/cleanup_official_apply_blockers.py
python scripts/cleanup_official_apply_blockers.py --apply
python scripts/prepare_populated_official_data.py --schedule-file data/official/imports/fifa_schedule.xlsx --squad-file data/official/imports/fifa_squads.csv
python scripts/apply_populated_official_data.py --preview
python scripts/apply_populated_official_data.py --apply
python scripts/evaluate_official_final_readiness.py
python scripts/fix_and_check_future_team_filter.py
python -m pytest -q
python -m streamlit run app/streamlit_app.py
```

### Step 17H outputs

| Artifact | Path |
|----------|------|
| Blocker cleanup report | `data/official/populated/reports/official_apply_blocker_cleanup_report.csv` |
| Completeness report | `data/official/populated/reports/official_population_completeness_report.csv` |

---

## Step 18: FIFA World Cup Awards Predictor

Step 18 estimates FIFA World Cup award outcomes using **official data only**. Awards generation **requires** `official_final_enabled=true` and `final_ready=true`; if official final mode is disabled, awards generation refuses to run.

### Requirements

- **official_final** must be promoted (`python scripts/promote_official_final.py --confirm`)
- Monte Carlo team stage probabilities (`python scripts/run_monte_carlo.py --simulations 10 --seed 42`)
- Uses **official_award_candidates.csv** only — no sample players can enter awards
- Uses official 48 teams, 104 fixtures, and 1,248 official players
- Combines editable player priors with Monte Carlo team progression probabilities

### Awards produced

| Category | Awards |
|----------|--------|
| Player impact | Golden Ball, Silver Ball, Bronze Ball |
| Scoring | Golden Boot, Silver Boot, Bronze Boot |
| Goalkeeper | Golden Glove |
| Youth | Young Player Award |
| Team | Fair Play Trophy, Most Entertaining Team |
| Analytics XI | Predicted Team of the Tournament (4-3-3) |
| Proxies | Player of the Match proxy, Goal of the Tournament proxy |

All outputs are **explainable analytics estimates**, not official FIFA predictions. No betting advice.

### Commands

```bash
python scripts/generate_world_cup_awards.py
python scripts/inspect_world_cup_awards.py
python scripts/generate_golden_ball_predictions.py
python scripts/inspect_golden_ball_predictions.py
python -m pytest -q
python -m streamlit run app/streamlit_app.py
```

### Key outputs

| Artifact | Path |
|----------|------|
| Combined predictions | `data/processed/world_cup_awards_predictions.csv` |
| Golden Ball | `data/processed/golden_ball_predictions.csv` |
| Golden Boot | `data/processed/golden_boot_predictions.csv` |
| Golden Glove | `data/processed/golden_glove_predictions.csv` |
| Young Player | `data/processed/young_player_predictions.csv` |
| Fair Play | `data/processed/fair_play_predictions.csv` |
| Most Entertaining Team | `data/processed/most_entertaining_team_predictions.csv` |
| Team of the Tournament | `data/processed/team_of_the_tournament.csv` |
| Summary | `data/processed/world_cup_awards_summary.json` |
| Validation | `data/processed/world_cup_awards_validation_report.csv` |
| Report | `reports/world_cup_awards_report.md` |

Streamlit page: **17 World Cup Awards** (`app/pages/17_World_Cup_Awards.py`).

---

## Step 19: Final Polish + Player Prior Enrichment + Portfolio Packaging

Step 19 makes the project **portfolio-ready** and improves award differentiation by enriching flat player priors with conservative position/role heuristics. Priors remain **heuristic/manual estimates**, not official season statistics.

### Player prior enrichment

- Reads `official_award_candidates.csv` only (no sample players)
- Applies position defaults, Monte Carlo progression uplift, shirt-number heuristics
- Saves `enriched_official_award_candidates.csv` (optional update of base file with backup)
- Awards prefer enriched candidates when available (`--use-enriched`)

### Portfolio outputs

| Artifact | Path |
|----------|------|
| Portfolio README | `portfolio/PORTFOLIO_README.md` |
| Demo script | `portfolio/demo_script.md` |
| Architecture | `portfolio/project_architecture.md` |
| Limitations | `portfolio/limitations.md` |
| Deployment guide | `portfolio/deployment_guide.md` |
| Reproducibility checklist | `portfolio/reproducibility_checklist.md` |
| Final summary | `data/processed/final_project_summary.json` |
| Final validation | `data/processed/final_project_validation_report.csv` |

### Commands

```bash
python scripts/enrich_player_priors.py
python scripts/enrich_player_priors.py --update-award-candidates
python scripts/generate_world_cup_awards.py --use-enriched
python scripts/prepare_final_project_pack.py
python scripts/run_final_demo_pipeline.py --simulations 10
python -m pytest -q
python -m streamlit run app/streamlit_app.py
```

Outputs remain **probabilistic analytics estimates**, not official FIFA predictions. No betting advice. The `official_final` gate is unchanged — awards refuse to run when disabled.

