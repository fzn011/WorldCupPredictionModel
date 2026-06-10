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

Expect **373 passed, 1 skipped** (includes Step 17F–17H official-data tests). No linter config (ruff/flake8/black) is present in the repo.

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
