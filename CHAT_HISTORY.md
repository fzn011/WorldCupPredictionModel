# FIFA World Cup 2026 AI Predictor — Full Project Reference

**GitHub:** https://github.com/fzn011/WorldCupPredictionModel  
**Last updated:** 2026-06-10  
**Current status:** Step 17E complete (structure) · **9/15** readiness checks passing · awaiting manual 17F data (kickoff times + squads) · 308 tests passing

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Roadmap — Step-by-Step Progress](#2-roadmap--step-by-step-progress)
3. [Architecture Summary](#3-architecture-summary)
4. [ML Pipeline](#4-ml-pipeline)
5. [Simulation Engine](#5-simulation-engine)
6. [Official Data Pipeline (17A–17D)](#6-official-data-pipeline-17a17d)
7. [Current Data State](#7-current-data-state)
8. [Test Suite](#8-test-suite)
9. [Key Design Decisions](#9-key-design-decisions)
10. [Files Created / Modified per Step](#10-files-created--modified-per-step)
11. [CLI Reference](#11-cli-reference)
12. [Streamlit Dashboard Pages](#12-streamlit-dashboard-pages)
13. [Next Steps](#13-next-steps)
14. [GitHub Repository](#14-github-repository)
- [Appendix A: Key Constants Quick Reference](#appendix-a-key-constants-quick-reference)
- [Appendix B: Result Encoding](#appendix-b-result-encoding)

---

## 1. Project Overview

### What was built

A portfolio-quality machine learning and simulation system that predicts FIFA World Cup 2026 match outcomes, tournament progression probabilities, champion likelihood, and (eventually) individual award winners.

### Why

To demonstrate a clean, end-to-end ML pipeline with transparent design decisions, covering data engineering, feature engineering, model training, probabilistic prediction, simulation, and explainability — all surfaced through an interactive Streamlit dashboard and FastAPI service.

### Core capabilities

- Predict the result (Win/Draw/Loss) of any arbitrary international football match
- Generate explainable feature-importance summaries for individual predictions
- Simulate the complete 2026 World Cup group stage + knockout stage
- Run Monte Carlo simulations (default 100 runs) to estimate champion and stage-progression probabilities
- Generate World Cup awards predictions (Golden Ball, Golden Boot, etc.) once official squads are verified
- Serve predictions via a REST API (FastAPI) independently of the dashboard

### Technology stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.12 (3.14 mentioned in README badge) |
| ML | scikit-learn, XGBoost (optional), LightGBM (optional), HistGradientBoosting |
| Explainability | SHAP (optional), model-agnostic sensitivity fallback |
| Dashboard | Streamlit (14 pages) |
| API | FastAPI + Uvicorn |
| Data | CSV / JSON / joblib (no database) |
| Tests | pytest (308 passing) |
| Version control | Git → GitHub |

---

## 2. Roadmap — Step-by-Step Progress

### Step 1: Project Scaffolding

**What was done:**

- Created the monorepo directory layout (`data/`, `src/`, `app/`, `models/`, `reports/`, `tests/`, `scripts/`)
- Added `requirements.txt`, `config.yaml`, `main.py`, `README.md`
- Shipped a small synthetic sample dataset under `data/sample/`
- Set up `src/utils/constants.py` as the project-wide constants hub

**Key outcome:** Runnable Python package with sample data and a minimal pipeline entry point.

### Step 2: Data Loading and Source Connectors

**What was done:**

- `src/data/load_data.py` — loads raw CSV files, falls back to sample data when real data is absent
- `src/data/data_sources.py` — defines data-source contracts and source prioritisation
- `scripts/download_kaggle_datasets.py` — optional Kaggle download helper (requires credentials)
- `scripts/check_datasets.py` — reports which datasets are present

**Key outcome:** Pipeline gracefully degrades to sample data when full real datasets are missing.

### Step 3: Data Cleaning Pipeline

**What was done:**

- `src/data/clean_data.py` — standardises column names, encodes results as 0/1/2, attaches shootout outcomes
- `src/data/prepare_datasets.py` — orchestrates the full cleaning run
- `src/data/validate_data.py` — schema and referential checks
- `src/utils/team_name_mapping.py` — canonical team name mapping (handles variant spellings)
- Canonical match schema defined: 22 columns, team_a/team_b perspective with result = 0/1/2
- Cleaned output saved to `data/processed/canonical_matches.csv`

**Key outcome:** 32,179 historical match rows in a clean canonical schema.

### Step 4: Feature Engineering

**What was done:**

- `src/features/build_features.py` — main feature builder
- `src/features/historical_features.py` — historical form, goal averages, head-to-head
- `src/features/prepare_features.py` — orchestrator that writes `data/processed/feature_dataset.csv`
- Features include: recent win rates (5/10-match windows), goals scored/conceded averages, goal difference, head-to-head record, tournament type flags, neutral ground flag

**Feature dataset stats:**

- Rows: 32,179
- Columns: 125
- Train/Test split (temporal at 2022-01-01): 27,719 / 4,460

### Step 5: Baseline Match Result Model

**What was done:**

- `src/models/train_match_model.py` — trains Dummy, Logistic Regression, Random Forest
- `src/models/split_data.py` — temporal train/test split; leakage columns removed
- `src/models/evaluate_model.py` — accuracy, classification report, confusion matrix, feature importance
- `src/models/model_features.py` — selects numeric feature columns, removes leakage
- Model artifacts saved to `models/baseline/`
- Reports saved to `reports/`

**Baseline results:**

| Model | Notes |
|-------|-------|
| Dummy classifier | Majority-class baseline |
| Logistic Regression | Probability-calibrated softmax |
| Random Forest | Best baseline — saved as `best_baseline_model.joblib` |

### Step 6: Model Improvement Part 1

**What was done:**

- `src/models/advanced_models.py` — adds XGBoost, LightGBM, HistGradientBoosting (optional imports)
- `src/models/calibration.py` — sigmoid/isotonic probability calibration
- `src/models/backtesting.py` — temporal backtesting across 4 chronological windows
- `src/models/train_improved_model.py` — orchestrator; saves best improved model
- Reports: `reports/baseline_vs_improved_metrics.csv`, `temporal_backtest_results.csv`, `calibration_report.csv`

**Backtest windows:**

| Window | Test start date |
|--------|-----------------|
| test_2018_onward | 2018-01-01 |
| test_2020_onward | 2020-01-01 |
| test_2022_onward | 2022-01-01 |
| test_2024_onward | 2024-01-01 |

**Design note:** XGBoost and LightGBM are imported optionally and skipped gracefully if not installed. HistGradientBoosting is always available as a safe fallback. Current best improved model: `hist_gradient_boosting`.

### Step 7: FIFA Rankings and Elo Integration

**What was done:**

- `src/features/ranking_features.py` — merges FIFA ranking and Elo snapshot data into feature rows
- `src/features/prepare_ranking_features.py` — orchestrates ranking feature generation
- `src/models/train_ranking_enhanced_model.py` — trains on ranking-enriched feature set
- New features added: `team_a_fifa_rank`, `team_b_fifa_rank`, `diff_fifa_rank`, `team_a_elo`, `team_b_elo`, `diff_elo`, `team_a_strength_score`, `diff_strength_score` (8 FIFA + 8 Elo + 3 composite = 19 new columns)
- Ranking-enhanced model saved to `models/ranking_enhanced/`

**Important snapshot limitation:** This step applies the latest available FIFA/Elo snapshot across all historical rows. It is an approximation (not date-aware historical joining). Date-aware historical ranking joins are documented as a future refinement.

### Step 8: Future Match Feature Generator

**What was done:**

- `src/features/future_match_features.py` — generates a complete feature row for any arbitrary future match at inference time using only data strictly before the requested match date
- `src/models/predict_match.py` — loads the best available model (preference order: ranking_enhanced → improved → baseline) and returns win/draw/loss probabilities
- `scripts/predict_future_match.py` — CLI prediction tool
- `scripts/inspect_future_feature_row.py` — debugging tool for inspecting what a feature row looks like

**Key outcome:** Real arbitrary future match predictions, not placeholders.

### Step 9: Prediction Reporting

**What was done:**

- Prediction history logging (`data/processed/prediction_history.csv`)
- Latest prediction report (`data/processed/latest_prediction_report.csv`)
- Confidence thresholds defined: High ≥ 0.60, Medium ≥ 0.45

### Step 10: Match Prediction Explainability

**What was done:**

- `src/models/explain_prediction.py` — local prediction explanations using SHAP (when available and compatible) or model-agnostic permutation sensitivity fallback
- Natural-language explanation text generated for faster interpretation
- Global feature importance available via `scripts/inspect_global_explanation.py`
- Explanation artifacts saved to `reports/`
- API endpoint added: `POST /predict/future-match` returns explanation alongside prediction

**Explanation methods (in priority order):**

1. SHAP values (if library available and model compatible)
2. Model permutation sensitivity
3. Feature importance (tree-based models)
4. Fallback (coefficient-based for linear models)

### Step 11: Tournament Fixture and Group Setup

**What was done:**

- `src/tournament/groups.py` — group definitions (12 groups × 4 teams)
- `src/tournament/fixtures.py` — 72 group-stage fixture generation (6 per group × 12 groups)
- `src/tournament/structure.py` — tournament metadata and structure
- `src/tournament/knockout.py` — knockout placeholder generation (Round of 32 through Final)
- `scripts/prepare_tournament_setup.py` — writes `data/processed/tournament_groups.csv`, `tournament_fixtures.csv`, `knockout_placeholders.csv`

**Tournament format:**

- 48 teams, 12 groups (A–L), 4 teams per group
- 72 group-stage matches (6 per group)
- Top 2 from each group (24 teams) + best 8 third-placed teams = 32 qualifiers
- Knockout: Round of 32 → Round of 16 → Quarter-final → Semi-final → Third-place → Final

### Step 12: Group-Stage Simulation Engine

**What was done:**

- `src/simulation/group_stage.py` — simulates all 72 group-stage fixtures
- Uses `predict_future_match()` per fixture to obtain win/draw/loss probabilities
- Samples outcomes from model probabilities (probabilistic, not argmax)
- Generates approximate scorelines from template dictionaries
- Builds group tables with points, goal difference, goals scored/against
- Selects top 2 from each group + best 8 third-placed → 32 Round-of-32 qualifiers
- `scripts/simulate_group_stage.py --seed 42`

**Scoreline templates (group stage):**

| Outcome | Scorelines |
|---------|------------|
| Team A win | 1-0, 2-0, 2-1, 3-1, 3-2 |
| Draw | 0-0, 1-1, 2-2 |
| Team A loss | 0-1, 0-2, 1-2, 1-3, 2-3 |

### Step 13: Knockout Simulation Engine

**What was done:**

- `src/simulation/knockout_stage.py` — simulates one complete knockout bracket
- Consumes Round-of-32 qualifier list from Step 12
- No-draw adjustment: draws are resolved to a winner (extra time / penalties implied)
- Simulates all 32 knockout matches across 6 rounds
- Produces champion, runner-up, third place, fourth place
- `scripts/simulate_knockout_stage.py --seed 42`

**Knockout match counts:**

| Round | Matches |
|-------|---------|
| Round of 32 | 16 |
| Round of 16 | 8 |
| Quarter-final | 4 |
| Semi-final | 2 |
| Third-place | 1 |
| Final | 1 |
| **Total** | **32** |

### Step 14: Full Tournament Single-Run Orchestrator

**What was done:**

- `src/simulation/full_tournament.py` — chains group-stage + knockout into one complete run
- Passes fresh in-memory qualifiers from group stage directly into knockout simulator
- Saves champion, runner-up, third/fourth place, full match logs, stage summaries, path reports
- `scripts/simulate_full_tournament.py --seed 42`

**Key outcome:** One complete reproducible tournament run from group draw to champion, end-to-end.

### Step 15: Monte Carlo Tournament Simulator

**What was done:**

- `src/simulation/monte_carlo.py` — repeats `run_full_tournament_single()` N times (default 100)
- `src/models/prediction_cache.py` — caches repeated match predictions across simulations for performance
- Aggregates: champion probabilities, stage-progression probabilities, finalists/semifinalists frequency tables
- `scripts/run_monte_carlo.py --simulations 100 --seed 42`
- Outputs saved to `data/processed/monte_carlo_*.csv`

**Stage probability columns tracked:**  
`group_stage` → `round_of_32` → `round_of_16` → `quarter_final` → `semi_final` → `final` → `champion`

### Step 16: Monte Carlo Dashboard and Report Polish

**What was done:**

- `src/reports/monte_carlo_report.py` — Markdown report generation
- `src/reports/monte_carlo_visuals.py` — champion probability bar chart, stage progression heatmap
- `src/reports/prepare_monte_carlo_report.py` — orchestrates report artifact creation
- Streamlit dashboard page `9_Monte_Carlo_Simulator.py` — champion probabilities, progression table, summary cards, downloadable export
- `scripts/generate_monte_carlo_report.py` — generates `reports/monte_carlo_report.md`

### Step 17A: Official World Cup 2026 Data Lock

**What was done:**

- Created `data/official/` directory tree: `raw/`, `processed/`, `reports/`
- `src/official/prepare_official_data.py` — initialises official data files with sample/placeholder structure
- `src/official/validators.py` — validates official data against contracts
- `src/official/official_data_contracts.py` — schema contracts for all official entities
- `src/official/loaders.py` — loads official data files, distinguishing official vs sample mode
- Official teams, groups, fixtures, venues, match-calendar CSV files created under `data/official/processed/`
- `DEFAULT_TOURNAMENT_DATA_MODE = "official"` — official mode is the default
- Match prediction can now restrict teams to the official World Cup 2026 team list

**Data mode flag:** Predictions that use non-official teams in official mode are warned/blocked.

### Step 17B: Official Squads and Player Priors

**What was done:**

- `src/official/prepare_squads.py` — initialises squad structure (sample players with `source = sample_to_be_verified`)
- `src/official/squad_validators.py`, `squad_contracts.py`, `squad_parser.py`, `squad_loaders.py`, `player_registry.py` — full squad management layer
- `src/awards/player_priors.py` — player award priors data model
- `data/official/processed/official_players.csv` — 65 sample players across 17 teams (partial, all `sample_to_be_verified`)
- `data/official/processed/official_squads.csv`, `official_team_player_map.csv` — squad aggregate tables
- Sample player award priors bootstrapped

**Important constraint:** The awards predictor (Step 18) must use `official_players.csv` only. Sample players are not allowed in official mode.

### Step 17C: Official Data Completion and Verification Framework

**What was done:**

- `src/official/final_readiness.py` — 15-point readiness checklist evaluating all six datasets
- `src/official/missing_data.py` — missing-data report generation
- `src/official/import_diff.py` — diff tool to compare incoming import vs current stored data
- `scripts/evaluate_official_final_readiness.py` — runs the readiness check and prints a pass/fail report
- `scripts/promote_official_final.py` — promotes to `official_final` mode only when all 15 checks pass
- `data/official/processed/official_final_readiness_checklist.csv` — checklist output

**Readiness levels:** `blocked` / `warning` / `ready`

### Step 17D: Official Data Population Pack

**What was done:**

- `src/official/prepare_population_pack.py` — generates population guide, master workbook, status tracker
- `src/official/import_templates.py` — generates the six import template CSV files
- `src/official/master_workbook.py` — master XLSX workbook for data entry
- `src/official/population_guide.py` — step-by-step population guide document
- `src/official/population_status.py` — tracks per-dataset population status
- `src/official/apply_imports.py` — safe import applicator with backups and audit logs
- `src/official/promotion.py` — final promotion logic (only succeeds when all blockers clear)

**Import templates generated** (under `data/official/import_templates/`):

| File | Purpose |
|------|---------|
| `official_teams_import_template.csv` | 48 rows for team data |
| `official_groups_import_template.csv` | 48 rows (12 × 4) group assignments |
| `official_venues_import_template.csv` | 16+ stadium rows |
| `official_fixtures_import_template.csv` | 104 match rows |
| `official_players_import_template.csv` | 1,248 player rows |
| `player_award_priors_import_template.csv` | 1,248 prior rows |

**Population workflow (safe apply order):**  
teams → groups → venues → fixtures → players → player_priors → evaluate readiness → promote

### Step 17E: Official Teams, Groups, Venues, and Fixtures Pre-fill (complete)

**What was done:**

- Fixed `UnicodeEncodeError` in `scripts/prefill_known_official_data.py` (replaced arrow characters for Windows console encoding)
- Fixed column mismatch (`group_slot` vs `slot`) so teams are derived correctly from groups
- Pre-filled **48 teams**, **48 group slots** (Groups A–L), and **16 venues** from the Dec 2024 WC draw — tagged `ai_prefilled_needs_verification`
- Added **32 knockout placeholder fixtures** (R32 × 16, R16 × 8, QF × 4, SF × 2, third-place, Final) → **104 total fixtures**
- Applied imports in order: teams → groups → venues → fixtures (backups + audit log)
- Pushed to `main`: `step-17e: apply teams/groups/venues/fixtures official data import`

**Readiness after 17E:** **9/15 checks passing**

| Check | Status |
|-------|--------|
| `teams_complete` (48/48) | Pass |
| `teams_no_placeholders` | Pass |
| `groups_complete` (48/48) | Pass |
| `groups_no_placeholders` | Pass |
| `venues_complete` (16/16) | Pass |
| `venues_no_placeholders` | Pass |
| `fixtures_complete` (104/104) | Pass |
| `player_priors_merged` | Pass |
| `data_consistency` (groups ↔ teams) | Pass |
| `fixtures_no_placeholders` | Fail — kickoff times / venue assignments TBD |
| `squads_complete` | Fail — 0/48 teams with 26 players |
| `players_complete` | Fail — 65/1,248 players |
| `no_sample_rows` | Fail — fixtures + players still pre-filled / sample |
| `data_consistency` (fixtures) | Fail — knockout TBD team names expected |
| `award_candidates_ready` | Warning |

**Regenerate pre-fill (preview before apply):**

```bash
python scripts/prefill_known_official_data.py
python scripts/_gen_knockout_fixtures.py
python scripts/apply_official_import.py --target teams    --file data/official/import_templates/official_teams_import_template.csv --preview
python scripts/evaluate_official_final_readiness.py
```

---

## 3. Architecture Summary

### Directory Layout

```
world-cup-2026-ai-predictor/
├── data/
│   ├── raw/                  # Historical results, FIFA rankings, Elo (not committed)
│   │   ├── matches/
│   │   ├── rankings/
│   │   └── world_cup_2026/
│   ├── sample/               # Small synthetic dataset for development
│   ├── processed/            # Feature datasets, simulation outputs, canonical matches
│   └── official/             # Official World Cup 2026 data layer
│       ├── raw/
│       ├── processed/        # official_teams, groups, fixtures, venues, players, squads
│       ├── reports/
│       ├── import_templates/ # Six editable CSV templates
│       └── population/       # Population guide, workbooks, reports, checklist
├── src/
│   ├── data/                 # load_data, clean_data, prepare_datasets, validate_data
│   ├── features/             # build_features, historical_features, future_match_features,
│   │                         # ranking_features, prepare_ranking_features, prepare_features
│   ├── models/               # train_match_model, train_improved_model,
│   │                         # train_ranking_enhanced_model, predict_match,
│   │                         # explain_prediction, calibration, backtesting,
│   │                         # advanced_models, prediction_cache, model_features,
│   │                         # evaluate_model, split_data, prediction_utils
│   ├── simulation/           # group_stage, knockout_stage, full_tournament, monte_carlo,
│   │                         # prepare_group_stage, prepare_knockout,
│   │                         # prepare_full_tournament, prepare_monte_carlo
│   ├── tournament/           # groups, fixtures, knockout, structure, prepare_tournament
│   ├── reports/              # monte_carlo_report, monte_carlo_visuals, prepare_monte_carlo_report
│   ├── awards/               # player_awards, award_reports, player_priors,
│   │                         # prepare_awards, team_awards, team_of_tournament
│   ├── players/              # golden_ball, prepare_golden_ball
│   ├── official/             # prepare_official_data, validators, official_data_contracts,
│   │                         # loaders, prepare_squads, squad_validators, squad_contracts,
│   │                         # squad_parser, squad_loaders, player_registry,
│   │                         # apply_imports, import_templates, import_diff,
│   │                         # missing_data, population_status, population_guide,
│   │                         # master_workbook, prepare_population_pack, final_readiness,
│   │                         # promotion
│   └── utils/                # constants.py, team_name_mapping.py
├── app/
│   ├── streamlit_app.py      # Main dashboard entry point
│   └── pages/                # 14 Streamlit pages (numbered 1–14)
├── api/
│   └── main.py               # FastAPI service
├── models/
│   ├── baseline/             # dummy, logistic_regression, random_forest, best_baseline
│   ├── improved/             # hist_gradient_boosting, best_improved_model
│   └── ranking_enhanced/     # best_ranking_enhanced_model
├── reports/                  # Generated CSVs, JSONs, PNGs, Markdown reports
├── scripts/                  # 44 CLI scripts (one per task)
├── tests/                    # 78 test files, 308 tests total
├── docs/
│   ├── DATA_DICTIONARY.md
│   ├── DATA_SOURCES.md
│   └── PROJECT_REFERENCE.md  # This file
├── main.py                   # Pipeline entry point
├── config.yaml
├── requirements.txt
├── README.md
└── AGENTS.md                 # Cursor Cloud agent instructions
```

### Data Flow

```
data/raw/ or data/sample/
        │
        ▼
src/data/load_data.py
src/data/clean_data.py
        │  canonical_matches.csv (32,179 rows)
        ▼
src/features/build_features.py
src/features/historical_features.py
src/features/ranking_features.py
        │  feature_dataset.csv (32,179 rows × 125 cols)
        │  ranking_feature_dataset.csv (32,179 rows × ~144 cols)
        ▼
src/models/train_match_model.py       → models/baseline/
src/models/train_improved_model.py    → models/improved/
src/models/train_ranking_enhanced_model.py → models/ranking_enhanced/
        │
        ▼
src/features/future_match_features.py
src/models/predict_match.py           (inference: ranking_enhanced > improved > baseline)
src/models/explain_prediction.py
        │
        ▼
src/simulation/group_stage.py
src/simulation/knockout_stage.py
src/simulation/full_tournament.py
src/simulation/monte_carlo.py
        │
        ▼
data/processed/monte_carlo_*.csv
reports/monte_carlo_report.md
        │
        ▼
app/streamlit_app.py (14 pages)
api/main.py (FastAPI REST)
```

---

## 4. ML Pipeline

### Feature Engineering

Historical features computed per match (from strictly pre-match data):

| Feature group | Description |
|---------------|-------------|
| `last_5_win_rate`, `last_10_win_rate` | Win rate over recent 5 and 10 matches |
| `goals_scored_avg_before` | Average goals scored in all prior matches |
| `goals_conceded_avg_before` | Average goals conceded |
| `goal_diff_avg_before` | Average goal difference |
| `h2h_wins`, `h2h_draws`, `h2h_losses` | Head-to-head record |
| `diff_*` variants | Team A minus Team B for all above |
| Tournament flags | `is_world_cup`, `is_qualifier`, `is_friendly`, `is_continental` |
| `neutral` | 1 if played at neutral venue |

Ranking/Elo features (Step 7+):

| Feature | Source |
|---------|--------|
| `team_a_fifa_rank`, `team_b_fifa_rank`, `diff_fifa_rank` | FIFA World Rankings |
| `team_a_fifa_points`, `team_b_fifa_points`, `diff_fifa_points` | FIFA ranking points |
| `team_a_elo`, `team_b_elo`, `diff_elo` | Club Elo / national team Elo |
| `team_a_strength_score`, `team_b_strength_score`, `diff_strength_score` | Composite normalised score |

**Target variable:** `result` — 0 = Team A loss, 1 = Draw, 2 = Team A win

**Leakage prevention:** Score columns, winner/loser, shootout outcomes are removed before model training.

### Model Tiers

```
Tier 1 — Baseline (models/baseline/)
  ├── DummyClassifier          (majority-class reference)
  ├── LogisticRegression       (calibrated softmax)
  └── RandomForest             ← best_baseline_model.joblib

Tier 2 — Improved (models/improved/)
  ├── XGBoostClassifier        (optional, skipped if not installed)
  ├── LightGBMClassifier       (optional, skipped if not installed)
  ├── HistGradientBoosting     (always available — scikit-learn built-in)
  └── Calibrated variants      (sigmoid calibration) ← best_improved_model.joblib

Tier 3 — Ranking Enhanced (models/ranking_enhanced/)
  └── HistGradientBoosting + ranking/Elo features ← best_ranking_enhanced_model.joblib
```

**Model preference at inference:** `ranking_enhanced` → `improved` → `baseline` (uses the best available).

### Probability Calibration

- **Method:** sigmoid (Platt scaling) via `CalibratedClassifierCV`
- Applied to Random Forest and gradient boosting models
- Improves reliability of probability estimates (predicted 0.7 should be correct ~70% of the time)

### Temporal Backtesting

Backtesting uses strict temporal splits — no future data leaks into training. Four windows evaluated:

- 2018-onward, 2020-onward, 2022-onward, 2024-onward

Reports saved to `reports/temporal_backtest_results.csv`.

---

## 5. Simulation Engine

### Group Stage (`src/simulation/group_stage.py`)

- Loads 72 group-stage fixtures from `data/processed/tournament_fixtures.csv`
- For each fixture: calls `predict_future_match(team_a, team_b, date, tournament, neutral=1)` → probabilities
- Samples a result from [win, draw, loss] using the predicted probability distribution
- Draws a scoreline from the appropriate template (probabilistic)
- Accumulates: wins/draws/losses, goals for/against, points (W=3, D=1, L=0)
- Ranks teams within each group by points → goal difference → goals scored
- Selects top 2 from each of 12 groups (24 teams) + best 8 third-placed teams = 32 qualifiers

### Knockout Stage (`src/simulation/knockout_stage.py`)

- Receives 32 qualifiers as a bracket
- For each match: calls `predict_future_match()` → adjusts to no-draw probabilities
- Probabilistically selects a winner (no draws allowed in knockout)
- Propagates winners through: R32 → R16 → QF → SF → 3rd-place match → Final
- Returns champion, runner-up, third place, fourth place

### Full Tournament (`src/simulation/full_tournament.py`)

Chains group stage → knockout stage in a single call with a shared RNG seed for reproducibility.

### Monte Carlo (`src/simulation/monte_carlo.py`)

```python
for i in range(n_simulations):
    seed = base_seed + i
    result = run_full_tournament_single(random_seed=seed, predictor=cached_predictor)
    # accumulate champion counts, stage appearances
```

- Default: 100 simulations (sufficient for local development; increase for production estimates)
- Uses `CachedMatchPredictor` to avoid re-calling the model for the same fixture across runs
- Outputs: champion probabilities table, stage-progression probabilities per team, finalists/semifinalists frequency

**Outputs written to `data/processed/`:**

| File | Contents |
|------|----------|
| `monte_carlo_simulation_results.csv` | Per-run champion, runner-up, 3rd, 4th |
| `monte_carlo_team_stage_probabilities.csv` | Per-team probability at each stage |
| `monte_carlo_champion_probabilities.csv` | Ranked champion probability table |
| `monte_carlo_finalists.csv` | Finalist frequency |
| `monte_carlo_semifinalists.csv` | Semifinalist frequency |
| `monte_carlo_summary.json` | Summary metadata |

---

## 6. Official Data Pipeline (17A–17D)

The official data pipeline introduces a strict separation between placeholder/sample data and verified official FIFA data.

### 17A — Data Lock and Contracts

- Created `data/official/` tree
- Defined schema contracts for all 5 entity types: teams, groups, venues, fixtures, match calendar
- Initialised blank official files with placeholder rows tagged `source = sample_to_be_verified`
- Added data_mode switching: sample vs official (default is official)
- Predictions in official mode are restricted to the official team list

### 17B — Squad and Player Layer

- Defined player schema (16 required columns per player)
- Bootstrapped 65 sample players across 17 teams (not full squads; all `sample_to_be_verified`)
- Created player registry, squad summary, and team-player map
- Defined player award priors schema (14 required columns per player)
- Awards predictor is blocked until full official squads replace sample rows

### 17C — Readiness Framework

- 15-point readiness checklist covering all 6 datasets
- Automated `evaluate_official_final_readiness.py` script
- Three readiness states: blocked (missing required data), warning (placeholders present), ready
- `promote_official_final.py --confirm` succeeds only when all 15 checks pass and all blockers are cleared

### 17D — Population Pack

- 6 import template CSV files generated with all required columns pre-populated
- Population guide Markdown doc (`data/official/population/official_data_population_guide.md`)
- Master XLSX workbook (`data/official/population/workbooks/`)
- Safe import applicator (`apply_official_import.py`) — always creates backup before overwriting
- Import audit log, diff report, promotion report
- Streamlit pages for official data health, squad health, readiness dashboard

### Official Data Promotion Blockers

Promotion to `official_final` mode is blocked if any of the following is true:

| Blocker | Condition |
|---------|-----------|
| `incomplete_teams` | Fewer than 48 verified teams |
| `incomplete_groups` | Not 12 groups × 4 teams |
| `incomplete_venues` | Fewer than 16 venues |
| `incomplete_fixtures` | Fewer than 104 fixtures |
| `incomplete_squads` | Not all 48 teams with 26 players |
| `incomplete_players` | Fewer than 1,248 players |
| `placeholder_values_detected` | Any TBD, Unknown, Sample Venue, etc. present |
| `sample_rows_detected` | Any `source = sample_to_be_verified` rows |
| `data_inconsistency` | Cross-dataset mismatch (team names, venue codes, etc.) |
| `validation_failed` | Schema validation errors |

---

## 7. Current Data State

As of 2026-06-10 (after **Step 17E** — structure applied, **9/15** readiness checks passing):

### Official Entities

| Dataset | Current count | Required | Status |
|---------|---------------|----------|--------|
| Teams | 48 (Dec 2024 draw, `ai_prefilled_needs_verification`) | 48 verified | Structure complete — needs human verification |
| Groups | 48 (12 × 4, draw-aligned) | 48 (12 × 4) | Structure complete — needs human verification |
| Venues | 16 stadiums with real metadata | 16+ verified | Complete — needs human verification |
| Fixtures (structure) | 104 (72 group + 32 knockout placeholders) | 104 | Structure complete |
| Fixtures (schedule) | Kickoff times / venue assignments TBD | Verified schedule | Blocker for `fixtures_no_placeholders` |
| Players | 65 rows across 17 teams (sample) | 1,248 (48 × 26) | Step 17F — manual FIFA squads |
| Player priors | 65 rows merged | 1,248 | Step 17F — fill after players |

### Sample Groups (current fixture data — not verified)

| Group | Teams |
|-------|-------|
| A | Mexico, South Africa, South Korea, Czechia |
| B | Canada, Switzerland, Qatar, Bosnia and Herzegovina |
| C | United States, Japan, Nigeria, Serbia |
| D | Brazil, Croatia, Egypt, Australia |
| E | Argentina, Denmark, Ghana, Costa Rica |
| F | France, Morocco, Ecuador, Poland |
| G | England, Iran, Tunisia, Peru |
| H | Spain, Cameroon, Uruguay, Sweden |
| I | Germany, Algeria, Colombia, Scotland |
| J | Portugal, Senegal, United Arab Emirates, Austria |
| K | Netherlands, Côte d'Ivoire, Chile, Norway |
| L | Belgium, Turkey, Paraguay, New Zealand |

These groups reflect the **Dec 2024 FIFA draw** pre-filled in Step 17E. Review each row, set `source` to a verified tag (e.g. `fifa_official_manual`), then fill **kickoff times and venue assignments** from the [FIFA match schedule](https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026) before promotion.

### Sample Players (current — not verified)

65 sample players across 17 teams, tagged `source = sample_to_be_verified`. Teams with sample players include: France (5), England (6), Brazil (5), Argentina (6), Spain (5), Belgium (5), Germany (5), Portugal (6), Uruguay (4), Morocco (3), Netherlands (2), United States (2), Canada (2), Mexico (2), Japan (2), South Korea (3), Croatia (2). All 31 other teams have zero players in the file.

### Historical Training Data

| Metric | Value |
|--------|-------|
| Feature rows | 32,179 |
| Feature columns | 125 (+ ~19 ranking columns in ranking-enhanced dataset) |
| Train rows | 27,719 |
| Test rows | 4,460 |
| Split date | 2022-01-01 (temporal) |
| Data source | Kaggle international results dataset (or sample fallback) |

### official_final status

`official_final_enabled = false` — **9/15** checks pass; promotion blocked until fixture schedule, full squads (1,248 players), and verification tags are complete.

---

## 8. Test Suite

### Overview

| Metric | Value |
|--------|-------|
| Total tests | 308 passing |
| Skipped | 1 (pre-existing; not introduced by the conversation) |
| Failing | 0 new failures |
| Test files | 78 |
| Framework | pytest |

### Run Command

```bash
python -m pytest -q
```

### Test File Coverage by Module

| Area | Test files |
|------|------------|
| Data loading, cleaning, validation | `test_dataset_loading.py`, `test_data_sources.py`, `test_dataset_validation.py`, `test_cleaning_pipeline.py`, `test_shootout_handling.py`, `test_team_name_mapping.py`, `test_team_registry.py` |
| Feature engineering | `test_prepare_step3.py`, `test_prepare_step4.py`, `test_build_features.py`, `test_historical_features.py` |
| Baseline models | `test_train_baseline_models.py`, `test_model_features.py`, `test_split_data.py`, `test_evaluate_model.py`, `test_predict_match.py` |
| Improved models | `test_train_improved_model.py`, `test_advanced_models.py`, `test_calibration.py`, `test_backtesting.py`, `test_improved_prediction.py` |
| Ranking features + model | `test_ranking_features.py`, `test_prepare_ranking_features.py`, `test_train_ranking_enhanced_model.py`, `test_ranking_prediction.py` |
| Future match prediction | `test_future_match_features.py`, `test_future_prediction.py`, `test_future_prediction_scripts.py` |
| Explainability | `test_explain_prediction.py`, `test_explain_scripts.py`, `test_api_explanation.py` |
| Tournament setup | `test_tournament_groups.py`, `test_tournament_fixtures.py`, `test_tournament_knockout.py`, `test_prepare_tournament.py` |
| Group stage simulation | `test_group_stage_simulation.py`, `test_group_stage_tables.py`, `test_prepare_group_stage.py` |
| Knockout simulation | `test_knockout_simulation.py`, `test_knockout_validation.py`, `test_prepare_knockout.py` |
| Full tournament | `test_full_tournament.py`, `test_full_tournament_reports.py`, `test_prepare_full_tournament.py` |
| Monte Carlo | `test_monte_carlo.py`, `test_monte_carlo_reports.py`, `test_prepare_monte_carlo.py`, `test_prediction_cache.py`, `test_monte_carlo_visuals.py`, `test_monte_carlo_report.py`, `test_prepare_monte_carlo_report.py` |
| Official data | `test_prepare_official_data.py`, `test_official_data_contracts.py`, `test_official_data_validators.py`, `test_official_prediction_filter.py` |
| Official squads | `test_prepare_official_squads.py`, `test_squad_validators.py`, `test_squad_contracts.py`, `test_squad_parser.py`, `test_player_registry.py` |
| Awards | `test_prepare_world_cup_awards.py`, `test_player_awards.py`, `test_award_reports.py`, `test_team_awards.py`, `test_team_of_tournament.py`, `test_awards_scripts.py` |
| Population pack (17D) | `test_prepare_population_pack.py`, `test_population_status.py`, `test_population_guide.py`, `test_master_workbook.py`, `test_missing_data.py`, `test_import_diff.py`, `test_official_final_readiness.py`, `test_promotion.py`, `test_population_scripts.py` |

---

## 9. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Temporal train/test split at 2022-01-01 | Prevents data leakage; ensures training data always precedes test data chronologically |
| Fallback to sample data | Pipeline is runnable without real data for development and CI |
| Model preference order: ranking_enhanced → improved → baseline | Uses the best available model at inference; degrades gracefully if artifacts missing |
| XGBoost/LightGBM as optional imports | Avoids hard dependency; HistGB is always available via scikit-learn |
| Sigmoid calibration only | Isotonic requires many samples; sigmoid is safer for smaller datasets |
| Probabilistic outcome sampling in simulation | Taking argmax always produces identical results per team matchup; sampling gives varied, realistic tournament paths |
| Scoreline templates instead of Poisson regression | Avoids a separate goal model in early steps; transparent, easy to inspect |
| `sample_to_be_verified` source tag | Clearly flags data that has not been manually verified; prevents accidental use of fake data in official mode |
| `official_final` promotion gating | Awards predictions are meaningless on incomplete squads; gating prevents misleading outputs |
| No scraping / auto-fetch in official pipeline | Data integrity; all official data must come from a human reviewing verified FIFA sources |
| Snapshot ranking (Step 7 limitation) | Applying latest rankings across all historical rows is a known approximation; date-aware joins are documented as future work |
| Prediction cache in Monte Carlo | The same team matchup may appear in many simulations; caching prevents redundant model calls |
| FastAPI and Streamlit are independent | Streamlit calls `src/` directly; FastAPI is a separate entry point; neither depends on the other running |
| `data_mode` default = official | Forces explicit opt-in to sample mode; catches accidental use of placeholder data |
| `AGENTS.md` for Cursor Cloud agents | Documents Python env, service commands, and test expectations for AI coding agents operating in this repo |

---

## 10. Files Created / Modified per Step

### Steps 1–5 (Foundation)

| Step | Key files created |
|------|-------------------|
| 1 | `main.py`, `config.yaml`, `requirements.txt`, `README.md`, `src/utils/constants.py`, `data/sample/` |
| 2 | `src/data/load_data.py`, `src/data/data_sources.py`, `scripts/download_kaggle_datasets.py`, `scripts/check_datasets.py` |
| 3 | `src/data/clean_data.py`, `src/data/prepare_datasets.py`, `src/data/validate_data.py`, `src/utils/team_name_mapping.py`, `data/processed/canonical_matches.csv` |
| 4 | `src/features/build_features.py`, `src/features/historical_features.py`, `src/features/prepare_features.py`, `data/processed/feature_dataset.csv` |
| 5 | `src/models/train_match_model.py`, `src/models/split_data.py`, `src/models/evaluate_model.py`, `src/models/model_features.py`, `models/baseline/`, `reports/` |

### Steps 6–10 (Model Improvement and Explainability)

| Step | Key files created |
|------|-------------------|
| 6 | `src/models/advanced_models.py`, `src/models/calibration.py`, `src/models/backtesting.py`, `src/models/train_improved_model.py`, `models/improved/` |
| 7 | `src/features/ranking_features.py`, `src/features/prepare_ranking_features.py`, `src/models/train_ranking_enhanced_model.py`, `models/ranking_enhanced/` |
| 8 | `src/features/future_match_features.py`, `src/models/predict_match.py`, `scripts/predict_future_match.py`, `scripts/inspect_future_feature_row.py` |
| 9 | `src/models/prediction_utils.py` (reporting helpers), prediction history CSVs |
| 10 | `src/models/explain_prediction.py`, `scripts/explain_future_match.py`, `scripts/inspect_global_explanation.py`, `app/pages/4_Model_Explanation.py` |

### Steps 11–16 (Simulation)

| Step | Key files created |
|------|-------------------|
| 11 | `src/tournament/groups.py`, `src/tournament/fixtures.py`, `src/tournament/structure.py`, `src/tournament/knockout.py`, `src/tournament/prepare_tournament.py`, `scripts/prepare_tournament_setup.py`, `scripts/inspect_tournament_setup.py`, `app/pages/5_Tournament_Setup.py` |
| 12 | `src/simulation/group_stage.py`, `src/simulation/prepare_group_stage.py`, `scripts/simulate_group_stage.py`, `scripts/inspect_group_stage_results.py`, `app/pages/6_Group_Stage_Simulation.py` |
| 13 | `src/simulation/knockout_stage.py`, `src/simulation/prepare_knockout.py`, `scripts/simulate_knockout_stage.py`, `scripts/inspect_knockout_results.py`, `app/pages/7_Knockout_Simulation.py` |
| 14 | `src/simulation/full_tournament.py`, `src/simulation/prepare_full_tournament.py`, `scripts/simulate_full_tournament.py`, `scripts/inspect_full_tournament_results.py`, `app/pages/8_Full_Tournament_Run.py` |
| 15 | `src/simulation/monte_carlo.py`, `src/models/prediction_cache.py`, `src/simulation/prepare_monte_carlo.py`, `scripts/run_monte_carlo.py`, `scripts/inspect_monte_carlo_results.py`, `app/pages/9_Monte_Carlo_Simulator.py` |
| 16 | `src/reports/monte_carlo_report.py`, `src/reports/monte_carlo_visuals.py`, `src/reports/prepare_monte_carlo_report.py`, `scripts/generate_monte_carlo_report.py`, `scripts/inspect_monte_carlo_report.py` |

### Steps 17A–17D (Official Data Pipeline)

| Step | Key files created |
|------|-------------------|
| 17A | `src/official/prepare_official_data.py`, `src/official/validators.py`, `src/official/official_data_contracts.py`, `src/official/loaders.py`, `data/official/processed/official_teams.csv`, `official_groups.csv`, `official_fixtures.csv`, `official_venues.csv`, `official_match_calendar.csv`, `scripts/prepare_official_worldcup_data.py`, `scripts/inspect_official_worldcup_data.py`, `app/pages/11_Official_Data_Health.py` |
| 17B | `src/official/prepare_squads.py`, `src/official/squad_validators.py`, `src/official/squad_contracts.py`, `src/official/squad_parser.py`, `src/official/squad_loaders.py`, `src/official/player_registry.py`, `src/awards/player_priors.py`, `data/official/processed/official_players.csv`, `official_squads.csv`, `official_team_player_map.csv`, `scripts/prepare_official_squads.py`, `scripts/inspect_official_squads.py`, `app/pages/12_Official_Squads_Health.py` |
| 17C | `src/official/final_readiness.py`, `src/official/missing_data.py`, `src/official/import_diff.py`, `scripts/evaluate_official_final_readiness.py`, `scripts/promote_official_final.py`, `app/pages/13_Official_Final_Readiness.py` |
| 17D | `src/official/prepare_population_pack.py`, …, `app/pages/14_Official_Data_Population.py`, `data/official/population/FILL_DATA_CHECKLIST.md` |
| 17E | `scripts/prefill_known_official_data.py`, `scripts/_gen_knockout_fixtures.py`, applied `official_teams.csv`, `official_groups.csv`, `official_venues.csv`, `official_fixtures.csv` (104 rows), import audit log |

---

## 11. CLI Reference

### Pipeline Commands

```bash
# Run full pipeline (clean → features → train baseline model)
python main.py

# Prepare tournament fixture/group setup
python scripts/prepare_tournament_setup.py
```

### Model Training

```bash
python scripts/train_improved_models.py
python scripts/prepare_ranking_features.py
python scripts/train_ranking_enhanced_model.py
```

### Prediction (CLI — no server needed)

```bash
python scripts/predict_future_match.py \
  --team-a Argentina --team-b France \
  --date 2026-06-11 --tournament "FIFA World Cup" --neutral 1

python scripts/inspect_future_feature_row.py \
  --team-a Argentina --team-b France --date 2026-06-11

python scripts/explain_future_match.py \
  --team-a Argentina --team-b France \
  --date 2026-06-11 --tournament "FIFA World Cup" --neutral 1

python scripts/inspect_global_explanation.py
```

### Simulation

```bash
python scripts/simulate_group_stage.py --seed 42
python scripts/inspect_group_stage_results.py

python scripts/simulate_knockout_stage.py --seed 42
python scripts/inspect_knockout_results.py

python scripts/simulate_full_tournament.py --seed 42
python scripts/inspect_full_tournament_results.py

python scripts/run_monte_carlo.py --simulations 100 --seed 42
python scripts/inspect_monte_carlo_results.py

python scripts/generate_monte_carlo_report.py
python scripts/inspect_monte_carlo_report.py
```

### Official Data Pipeline

```bash
python scripts/prefill_known_official_data.py
python scripts/_gen_knockout_fixtures.py

python scripts/prepare_official_worldcup_data.py
python scripts/inspect_official_worldcup_data.py

python scripts/prepare_official_squads.py
python scripts/inspect_official_squads.py

python scripts/evaluate_official_final_readiness.py

python scripts/generate_official_import_templates.py
python scripts/prepare_official_population_pack.py

python scripts/preview_official_import.py \
  --target teams \
  --file data/official/import_templates/official_teams_import_template.csv

python scripts/apply_official_import.py \
  --target teams \
  --file data/official/import_templates/official_teams_import_template.csv \
  --preview

python scripts/apply_official_import.py \
  --target groups \
  --file data/official/import_templates/official_groups_import_template.csv

python scripts/apply_official_import.py \
  --target venues \
  --file data/official/import_templates/official_venues_import_template.csv

python scripts/apply_official_import.py \
  --target fixtures \
  --file data/official/import_templates/official_fixtures_import_template.csv

python scripts/apply_official_import.py \
  --target players \
  --file data/official/import_templates/official_players_import_template.csv

python scripts/apply_official_import.py \
  --target player_priors \
  --file data/official/import_templates/player_award_priors_import_template.csv

python scripts/promote_official_final.py
python scripts/promote_official_final.py --confirm
```

### Awards (sample mode only — Step 17 precursor)

```bash
python scripts/generate_world_cup_awards.py
python scripts/inspect_world_cup_awards.py
python scripts/generate_golden_ball_predictions.py
python scripts/inspect_golden_ball_predictions.py
```

### Tests

```bash
python -m pytest -q
python -m pytest -q -k "monte_carlo"
```

### Services

```bash
streamlit run app/streamlit_app.py
streamlit run app/streamlit_app.py --server.address 0.0.0.0 --server.port 8501

uvicorn api.main:app --reload
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Quick API smoke test

```bash
curl http://127.0.0.1:8000/

curl -X POST http://127.0.0.1:8000/predict/future-match \
  -H "Content-Type: application/json" \
  -d '{"team_a":"Argentina","team_b":"France","match_date":"2026-06-11"}'
```

---

## 12. Streamlit Dashboard Pages

| Page | File | Content |
|------|------|---------|
| Home | `streamlit_app.py` | Project overview, quick links |
| 1 — Match Predictor | `1_Match_Predictor.py` | Single-match prediction form + probabilities |
| 2 — Tournament Simulator | `2_Tournament_Simulator.py` | Quick tournament simulation controls |
| 4 — Model Explanation | `4_Model_Explanation.py` | SHAP / feature-importance explanation viewer |
| 5 — Tournament Setup | `5_Tournament_Setup.py` | Group and fixture inspection |
| 6 — Group Stage Simulation | `6_Group_Stage_Simulation.py` | Group tables, simulated results |
| 7 — Knockout Simulation | `7_Knockout_Simulation.py` | Knockout bracket viewer |
| 8 — Full Tournament Run | `8_Full_Tournament_Run.py` | Single end-to-end tournament run |
| 9 — Monte Carlo Simulator | `9_Monte_Carlo_Simulator.py` | Champion probabilities, stage heatmap, summary cards, CSV download |
| 10 — World Cup Awards | `10_World_Cup_Awards.py` | Golden Ball, Golden Boot, etc. (sample mode) |
| 11 — Official Data Health | `11_Official_Data_Health.py` | Official teams/groups/venues/fixtures status |
| 12 — Official Squads Health | `12_Official_Squads_Health.py` | Player counts, squad completeness per team |
| 13 — Official Final Readiness | `13_Official_Final_Readiness.py` | 15-point readiness checklist with pass/fail |
| 14 — Official Data Population | `14_Official_Data_Population.py` | Population guide, status tracker, import workflow |

---

## 13. Next Steps

### Step 17E — Teams, Groups, Venues, Fixtures — **structure complete**

**Status:** Pre-fill applied and pushed to GitHub (`step-17e`). **9/15** readiness checks pass.

**Remaining 17E verification (manual):**

1. Review pre-filled teams/groups/venues against official FIFA sources
2. Change `source` from `ai_prefilled_needs_verification` to verified tags where confirmed
3. Fill **fixture kickoff times** (local + UTC) and **venue assignments** for all 104 matches — [FIFA Match Schedule](https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026)
4. Re-run `python scripts/evaluate_official_final_readiness.py`

**Still failing until schedule verified:**

| Check | Blocker |
|-------|---------|
| `fixtures_no_placeholders` | 201 placeholder fields (kickoff/venue TBD) |
| `no_sample_rows` | Fixtures + players not yet manually verified |
| `data_consistency` (fixtures) | Knockout TBD team names until bracket resolves |

### Step 17F — Fill Squads and Player Priors (manual — blocked until fixture schedule verified)

**What needs to be done:**

1. Fill `official_players_import_template.csv` (1,248 rows: 48 teams × 26 players)
2. Fill `player_award_priors_import_template.csv` (1,248 rows: one per official player)
3. Apply: `--target players`, then `--target player_priors`
4. Run `evaluate_official_final_readiness.py`
5. Run `promote_official_final.py --confirm` when all 15 checks pass

**Acceptance criteria:**

| Check | Target |
|-------|--------|
| Total players | 1,248 |
| Players per team | Exactly 26 |
| `sample_to_be_verified` rows | 0 |
| `official_final_enabled` | true |

### Step 18 — FIFA World Cup Awards Predictor (Code step — blocked until official_final = true)

**What will be built:**

- Golden Ball, Silver Ball, Bronze Ball
- Golden Boot (top scorer), Silver Boot, Bronze Boot
- Golden Glove (best goalkeeper)
- Young Player Award (born after 2005-01-01)
- Fair Play Trophy
- Most Entertaining Team
- Predicted Team of the Tournament (XI)
- Player of the Match proxy
- Goal of the Tournament proxy

**Scoring approach:** Base player rating × position-weighted stat priors × team progression probability from Monte Carlo. Position weights defined in `constants.py`.

**Why it is blocked:** Award predictions based on sample/incomplete squads are not trustworthy. The entire awards system must operate on fully verified `official_players.csv` data with `official_final_enabled = true`.

---

## 14. GitHub Repository

**URL:** https://github.com/fzn011/WorldCupPredictionModel  
**Branch:** `main`

**Not committed to Git (generated locally):**

- Model `.joblib` files (`models/*/`)
- Processed datasets (`data/processed/`)
- Reports (`reports/`)

**To regenerate after a fresh clone:**

```bash
python main.py
python scripts/prepare_tournament_setup.py
python scripts/run_monte_carlo.py --simulations 100 --seed 42
python scripts/generate_monte_carlo_report.py
```

---

## Appendix A: Key Constants Quick Reference

| Constant | Value | Meaning |
|----------|-------|---------|
| `WC2026_TOTAL_TEAMS` | 48 | Teams in the tournament |
| `WC2026_TOTAL_GROUP_MATCHES` | 72 | Group-stage fixtures |
| `OFFICIAL_TOTAL_MATCHES` | 104 | Total matches (72 + 32) |
| `OFFICIAL_REQUIRED_PLAYERS_PER_TEAM` | 26 | Squad size per team |
| `OFFICIAL_REQUIRED_TOTAL_PLAYERS` | 1,248 | 48 × 26 |
| `DEFAULT_MONTE_CARLO_SIMULATIONS` | 100 | Default MC run count |
| `DEFAULT_MONTE_CARLO_SEED` | 42 | Default RNG seed |
| `HIGH_CONFIDENCE_THRESHOLD` | 0.60 | Prediction confidence label |
| `MEDIUM_CONFIDENCE_THRESHOLD` | 0.45 | Prediction confidence label |
| `RANDOM_SEED` | 42 | Global RNG seed |
| `DEFAULT_TEST_START_DATE` | 2022-01-01 | Temporal split date |
| `YOUNG_PLAYER_CUTOFF_DATE_2026` | 2005-01-01 | Young Player Award cutoff |
| `MODEL_PREFERENCE_ORDER` | ranking_enhanced, improved, baseline | Inference model priority |
| `DEFAULT_TOURNAMENT_DATA_MODE` | official | Official mode is default |

---

## Appendix B: Result Encoding

All match results are encoded from team_a's perspective:

| Code | Label | Meaning |
|------|-------|---------|
| 0 | `team_a_loss` | Team A lost |
| 1 | `draw` | Match drawn |
| 2 | `team_a_win` | Team A won |

---

*This document was auto-generated from the project source files on 2026-06-10. It is intended as a standalone reference for understanding the full project without reading the build conversation.*
