# FIFA World Cup 2026 AI Predictor — Demo Script (5–7 minutes)

## 1. Intro (30s)

"This project forecasts World Cup 2026 match and tournament outcomes using ML plus Monte Carlo simulation. Award outputs are explainable analytics, not official FIFA predictions."

## 2. Official data readiness (60s)

- Open **13 Official Final Readiness** or homepage status cards
- Show `official_final_enabled=true`, 104 fixtures, 1,248 players
- Mention awards refuse to run without official final mode

## 3. Match predictor (60s)

- Open future match prediction page / API example
- Show probability outputs and explainability note

## 4. Monte Carlo simulation (90s)

- Open **9 Monte Carlo Simulator**
- Show champion probabilities and stage heatmap/report
- Note simulation count affects stability

## 5. Player prior enrichment (60s)

```bash
python scripts/enrich_player_priors.py --update-award-candidates
```

- Explain priors are heuristic unless manually edited
- Show prior quality report path

## 6. Awards predictor (90s)

- Open **17 World Cup Awards**
- Show Golden Ball / Boot / Glove podium and candidate source
- Highlight disclaimer banner

## 7. Reports & downloads (30s)

- Download CSV/MD reports from Streamlit or `data/processed/`

## 8. Limitations & closing (30s)

"No betting use. Uncertainty remains. Priors can be improved by editing official player prior files."
