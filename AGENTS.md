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

### Streamlit navigation (custom router)

- Entry point: `app/streamlit_app.py` → `render_app_shell()` in `app/components/layout.py`.
- Page modules live under `app/views/` (not `app/pages/`) and must export `render_page()` only — no top-level Streamlit execution on import.
- Use `navigate_to("Page Name")` via **`on_click`** on buttons. Do **not** call `navigate_to` inside `if st.button(...)` blocks, and never assign `wc_sidebar_nav_radio` after the sidebar `st.radio` renders (causes `StreamlitAPIException`).
- `.streamlit/config.toml` sets `showSidebarNavigation = false` so Streamlit does not auto-discover duplicate sidebar pages.
- Global theme CSS is injected once in `streamlit_app.py` via `inject_worldcup_css()` — individual pages should not rely on per-page theme gates.
- **Tables:** use `render_data_table()` from `app/components/ui.py` (static `st.table` with dark-theme CSS). Avoid raw `st.dataframe()` for preview tables — the canvas grid often renders as a blank black box inside tabs on dark themes.
- **Typography:** Sprintura is for **main page hero titles only** (`.wc-page-title` on home and inner pages). Hero `<h1>` tags also carry inline `SPRINTURA_PAGE_TITLE_STYLE` and render via `render_themed_html()` so the font wins over Streamlit’s global `h1` rules. Sidebar navigation labels use Roboto — do not apply Sprintura to sidebar radio tabs.
- **Monte Carlo page:** Run/report actions use `st.form` + `form_submit_button` (not bare `st.button` inside tabs). Simulation cap is `MAX_MONTE_CARLO_SIMULATIONS` (5000) in `src/utils/constants.py`.
- **Match Predictor & Awards:** Primary actions (predict, generate awards, enrich/regenerate) use `st.form` + `form_submit_button` with session-state feedback — same reliability pattern as Monte Carlo.
- **Official team names:** `load_official_teams()` enriches blank processed rows from `official_groups.csv` / `populated_official_teams.csv` via `src/official/team_name_enrichment.py`. Step 17A calls `repair_official_teams_artifact(persist=True)` before validation. Data Quality shows friendly team columns via `format_official_teams_for_display()`.
- **Team of the Tournament:** use `render_team_formation()` for the 4-3-3 pitch grid (player cards with team/position). Reports summary row uses `render_metric_card()` instead of raw HTML cards.

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

Expect **410+ passed, 1 skipped** after Step 20 UI + manual prior workflow tests. No linter config (ruff/flake8/black) is present in the repo.

### Step 20 UI: Streamlit theme (World Cup command center)

- Theme CSS: `app/styles/worldcup_theme.py` — call `inject_page_theme()` (from `app/components/ui.py`) at the top of each polished page after `st.set_page_config`.
- Reusable widgets: `app/components/ui.py` (metric cards, status badges, download hub cards, podium/formation helpers).
- Homepage (`app/streamlit_app.py`): Command Center / Reports & Downloads / Technical Diagnostics tabs — do not duplicate artifact tables on the command center tab.
- Path constants: still only from `app/streamlit_paths.py` (never assign `PROJECT_ROOT` locally in pages).
- UI tests: `python -m pytest tests/test_worldcup_ui_components.py tests/test_streamlit_paths.py -q`

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

### Streamlit `PROJECT_ROOT` NameError (Windows)

All Streamlit path constants come from **`app/streamlit_paths.py`**. The homepage imports `PROJECT_ROOT`, `OFFICIAL_DATA_DIR`, etc. from that module — **do not** assign them locally in `streamlit_app.py`.

**Wrong (causes NameError):**
```python
OFFICIAL_DATA_DIR = PROJECT_ROOT / "data/official"  # PROJECT_ROOT not defined yet
PROJECT_ROOT = getattr(C, "PROJECT_ROOT", ROOT)       # C may not exist yet
```

**Correct:** import from `streamlit_paths` immediately after adding `app/` to `sys.path`.

Run Streamlit from the **project root** (not `C:\Users\...`):

```powershell
cd "E:\World Cup prediction model\world-cup-2026-ai-predictor"
python -m streamlit run app/streamlit_app.py
```

Verify:

```bash
python -m pytest tests/test_streamlit_paths.py -q
python -m streamlit run app/streamlit_app.py
```

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
