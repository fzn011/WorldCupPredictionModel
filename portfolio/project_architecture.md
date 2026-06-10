# Project Architecture

## Layers

| Layer | Components |
|-------|------------|
| Data ingestion | Raw/sample match files, Kaggle helpers, manual official imports |
| Official data | Teams, fixtures, squads, priors, readiness, `official_final` gate |
| Feature engineering | Leakage-safe pre-match features, ranking/Elo merge |
| Model training | Baseline, improved, ranking-enhanced joblib artifacts |
| Prediction | Future match API/UI, explainability reports |
| Simulation | Group stage, knockout, full tournament orchestrator |
| Monte Carlo | Repeated simulations → stage/champion probabilities |
| Awards | Official candidates + priors + progression → award estimates |
| Reporting | Markdown/CSV summaries, Streamlit dashboards, portfolio pack |

## Data flow (awards)

```
official_players.csv + player_award_priors.csv
        ↓
official_award_candidates.csv
        ↓ (Step 19 enrich)
enriched_official_award_candidates.csv
        ↓
Monte Carlo team stage probabilities
        ↓
world_cup_awards_predictions.csv + reports
```

## Entry points

- `python main.py` — core ML pipeline
- `python scripts/run_monte_carlo.py` — tournament simulation batch
- `python scripts/generate_world_cup_awards.py --use-enriched` — awards
- `python -m streamlit run app/streamlit_app.py` — dashboard
