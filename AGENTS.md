# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

Single Python monolith: **FIFA World Cup 2026 AI Predictor** (ML pipeline + Streamlit dashboard + FastAPI). No Docker, database, or Node.js. All interfaces import `src/` directly and read/write local CSV/JSON/joblib artifacts under `data/` and `models/`.

### Python environment

- Use the project venv: `source .venv/bin/activate` (create with `python3 -m venv .venv` if missing).
- Ubuntu images may need `python3.12-venv` installed once via apt before `python3 -m venv` works.
- README mentions Python 3.14; the cloud VM runs **Python 3.12**, which works with current dependencies.

### First-time artifact generation

Model files and processed datasets are **not committed**. After a fresh clone, run:

```bash
python main.py
python scripts/prepare_tournament_setup.py
```

Optional for richer data: place files under `data/raw/` or use `scripts/download_kaggle_datasets.py` (requires Kaggle credentials). Without raw data, the pipeline falls back to `data/sample/`.

### Running services

| Service | Command | Port |
|---------|---------|------|
| Streamlit dashboard | `streamlit run app/streamlit_app.py --server.address 0.0.0.0 --server.port 8501` | 8501 |
| FastAPI | `uvicorn api.main:app --host 0.0.0.0 --port 8000` | 8000 |

Streamlit does **not** call the FastAPI server; they are independent entry points.

### Tests

```bash
python -m pytest -q
```

Expect **405+ passed, 1 skipped** after Step 20 (manual prior workflow tests). No linter config (ruff/flake8/black) is present in the repo.

### Step 19: Prior enrichment + portfolio demo pipeline

Enrich flat player priors before awards demo (official players only — never add non-official IDs):

```bash
python scripts/enrich_player_priors.py
python scripts/enrich_player_priors.py --update-award-candidates
python scripts/generate_world_cup_awards.py --use-enriched
python scripts/prepare_final_project_pack.py
python scripts/run_final_demo_pipeline.py --simulations 10
```

- **No scraping** or paid APIs for priors — heuristics + manual edits only
- Enriched priors must stay within `official_players.csv` player_id set
- Default demo Monte Carlo count: **10** (avoid huge simulations in CI/demo)

### Step 20: Manual star-player prior overrides

Optional manual boosts for official candidates only (no scraping, no new player IDs):

```bash
python scripts/export_player_award_prior_template.py
python scripts/generate_world_cup_awards.py --use-enriched --use-manual-priors
python scripts/run_final_demo_pipeline.py --simulations 10 --use-manual-priors
```

Demo preset: `data/templates/player_award_manual_priors_demo.csv`. Without `--use-manual-priors`, behavior matches Step 19.

### Step 18: World Cup Awards Predictor

Requires `official_final_enabled=true` (promote with `python scripts/promote_official_final.py --confirm`) and Monte Carlo outputs:

```bash
python scripts/run_monte_carlo.py --simulations 10 --seed 42
python scripts/generate_world_cup_awards.py
python scripts/inspect_world_cup_awards.py
```

Awards refuse to run if official final mode is disabled. Streamlit page: **17 World Cup Awards**. Generated award CSVs live under `data/processed/` (gitignored; regenerate after clone).

### Official data pipeline (Steps 17F–17H)

After importing FIFA schedule/squad files under `data/official/imports/`:

```bash
python scripts/cleanup_official_apply_blockers.py --apply
python scripts/prepare_populated_official_data.py --schedule-file data/official/imports/fifa_schedule.xlsx --squad-file data/official/imports/fifa_squads.csv
python scripts/apply_populated_official_data.py --apply
python scripts/evaluate_official_final_readiness.py
python scripts/fix_and_check_future_team_filter.py
```

Step 17H normalizes FIFA **First Stage** → `group_stage`, rebuilds 48 teams from schedule, and separates optional metadata warnings from apply blockers. `official_final_enabled` in config may still be `false` until explicitly promoted even when readiness passes.

### Quick API smoke test

```bash
curl http://127.0.0.1:8000/
curl -X POST http://127.0.0.1:8000/predict/future-match \
  -H "Content-Type: application/json" \
  -d '{"team_a":"Argentina","team_b":"France","match_date":"2026-06-11"}'
```

### CLI prediction (no servers)

```bash
python scripts/predict_future_match.py --team-a Argentina --team-b France --date 2026-06-11 --tournament "FIFA World Cup" --neutral 1
```
