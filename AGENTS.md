# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

Single Python monolith: **FIFA World Cup 2026 AI Predictor** (ML pipeline + Streamlit dashboard + FastAPI). No Docker, database, or Node.js. All interfaces import `src/` directly and read/write local CSV/JSON/joblib artifacts under `data/` and `models/`.

For the complete step-by-step roadmap, architecture, CLI reference, and official-data pipeline details, see [docs/PROJECT_REFERENCE.md](docs/PROJECT_REFERENCE.md).

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

Expect ~173 passed, 1 skipped. No linter config (ruff/flake8/black) is present in the repo.

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
