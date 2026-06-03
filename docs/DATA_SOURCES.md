# Data Sources

This document describes the datasets the **FIFA World Cup 2026 AI Predictor**
relies on, where they should be placed, and how to obtain them.

> **Note:** This project is for sports analytics and education only.
> It is **not** betting or gambling advice.

All real datasets are placed manually by the user. The project does not
scrape any website and does not require any API key. If a real dataset is
missing, a small sample fallback under `data/sample/` is used so the project
still runs end-to-end.

---

## 1. Historical International Football Match Results

- **Purpose:** main training dataset for the match-result model.
- **Expected file:** `data/raw/matches/results.csv`
- **Sample fallback:** `data/sample/sample_results.csv`
- **Suggested source:** the public Kaggle dataset
  *"International football results from 1872 to 2026"* (~49,000 matches).
  Download manually from Kaggle and place `results.csv` in
  `data/raw/matches/`.
- **Optional:** `data/raw/matches/shootouts.csv` for penalty-shootout outcomes.

Expected columns:

```
date, home_team, away_team, home_score, away_score,
tournament, city, country, neutral
```

---

## 2. FIFA Rankings

- **Purpose:** team-strength feature based on official FIFA points.
- **Expected file:** `data/raw/rankings/fifa_rankings.csv`
- **Sample fallback:** `data/sample/sample_fifa_rankings.csv`
- **Source:** the official FIFA men's world ranking. Manually prepare a CSV
  snapshot from the published ranking table.

Expected columns:

```
rank, team, team_code, points, ranking_date
```

---

## 3. World Football Elo Ratings

- **Purpose:** alternate team-strength feature based on Elo.
- **Expected file:** `data/raw/rankings/elo_ratings.csv`
- **Sample fallback:** `data/sample/sample_elo_ratings.csv`
- **Source:** publicly available World Football Elo ratings. Manually
  prepare a CSV snapshot.

Expected columns:

```
rank, team, elo, rating_date
```

---

## 4. FIFA World Cup 2026 — Teams, Groups, Schedule

The 2026 World Cup features **48 teams**, **12 groups of four**, and the
**top two teams from each group plus the eight best third-placed teams**
advance to the Round of 32. Manually prepare CSVs from official FIFA
tournament information.

- `data/raw/world_cup_2026/world_cup_2026_teams.csv`
- `data/raw/world_cup_2026/world_cup_2026_groups.csv`
- `data/raw/world_cup_2026/world_cup_2026_schedule.csv`

Sample fallbacks live under `data/sample/`.

---

## Templates

Empty-with-headers / minimal templates live under `data/external/`:

- `fifa_rankings_template.csv`
- `elo_ratings_template.csv`
- `world_cup_2026_teams_template.csv`
- `world_cup_2026_groups_template.csv`
- `world_cup_2026_schedule_template.csv`

Use these as a starting point when building your own CSVs from official
sources. Values in template and sample files are placeholders that must be
verified and updated from official / current sources before final modeling.

---

## Optional: automatic Kaggle download

The historical results dataset can be downloaded automatically with:

```bash
python scripts/download_kaggle_datasets.py
```

Requirements:

- The `kaggle` Python package (already listed in `requirements.txt`).
- Kaggle credentials at `~/.kaggle/kaggle.json` (Windows:
  `%USERPROFILE%\.kaggle\kaggle.json`) **or** the environment variables
  `KAGGLE_USERNAME` and `KAGGLE_KEY`.

The script never reads, stores, or prints credential contents. It downloads
the dataset `martj42/international-football-results-from-1872-to-2017`
into `data/raw/matches/` and unzips it. If credentials are missing, it
exits with clear instructions and the project continues with the sample
fallback.

> Never commit `kaggle.json` to git. The repo `.gitignore` already excludes
> `kaggle.json`, `.kaggle/`, and `*.zip`.

## Checking dataset availability

Run:

```bash
python scripts/check_datasets.py
```

to see, for each dataset, whether a real file is present in `data/raw/` or
whether the sample fallback will be used.
