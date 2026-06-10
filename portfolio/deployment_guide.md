# Deployment Guide

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Streamlit

```bash
python -m streamlit run app/streamlit_app.py --server.port 8501
```

## Environment notes

- Python 3.12+ recommended (see README)
- Model/joblib artifacts generated locally — not all committed
- Official data under `data/official/` — promote `official_final` only after readiness passes

## Kaggle credentials

If using `scripts/download_kaggle_datasets.py`, store `kaggle.json` outside the repo and never commit credentials.

## Streamlit Community Cloud (optional)

- Deploy from GitHub with `requirements.txt`
- Exclude secrets and large raw files via `.gitignore`
- Run `main.py` or ship pre-built artifacts as release assets for faster demos
- Set startup command: `streamlit run app/streamlit_app.py`

## Demo pipeline

```bash
python scripts/run_final_demo_pipeline.py --simulations 10
```
