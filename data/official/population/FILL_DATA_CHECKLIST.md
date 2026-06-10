# Official Data Population Checklist

Fill templates in **this exact order** — each file depends on the ones above it.

---

## Current status

Run this to get up-to-date numbers at any time:

```bash
python scripts/prepare_official_population_pack.py
python scripts/evaluate_official_final_readiness.py
```

---

## Step 17E: Teams, Groups, Venues, Fixtures

### 1. Teams — `official_teams_import_template.csv`

Required: **48 rows**, zero `sample_to_be_verified`.

| Column | Notes |
|--------|-------|
| `team` | Full official FIFA name |
| `team_code` | FIFA 3-letter code (e.g. BRA, FRA) |
| `confederation` | CONMEBOL / UEFA / CONCACAF / CAF / AFC / OFC |
| `group` | A through L |
| `group_slot` | 1, 2, 3, or 4 within the group |
| `is_host` | 1 for USA, Canada, Mexico; 0 otherwise |
| `qualified` | 1 for all 48 teams |
| `source` | e.g. `fifa_official_manual` — **never** `sample_to_be_verified` |

- [ ] 48 rows filled
- [ ] No `TBD`, `Unknown`, or `sample_to_be_verified` values

Apply:
```bash
python scripts/apply_official_import.py --target teams --file data/official/import_templates/official_teams_import_template.csv --preview
python scripts/apply_official_import.py --target teams --file data/official/import_templates/official_teams_import_template.csv
```

---

### 2. Groups — `official_groups_import_template.csv`

Required: **48 rows** (12 groups × 4 teams). Team names must match `official_teams.csv` exactly.

| Column | Notes |
|--------|-------|
| `group` | A–L |
| `slot` | 1–4 within the group |
| `team` | Must match `team` column in teams file |
| `team_code` | Must match `team_code` in teams file |
| `confederation` | Same as teams |
| `is_host` | Same as teams |
| `source` | e.g. `fifa_official_manual` |

- [ ] 48 rows filled (12 × 4)
- [ ] Every team name matches teams file exactly
- [ ] Each group has exactly 4 slots (1–4)

Apply:
```bash
python scripts/apply_official_import.py --target groups --file data/official/import_templates/official_groups_import_template.csv
```

---

### 3. Venues — `official_venues_import_template.csv`

Required: **16+ rows**.

| Column | Notes |
|--------|-------|
| `venue_id` | Short identifier, e.g. `venue_001` |
| `stadium` | Full official stadium name |
| `venue` | Nickname / short name used in fixtures |
| `city` | Host city |
| `country` | USA, Canada, or Mexico |
| `timezone` | IANA timezone, e.g. `America/New_York` |
| `capacity` | Seating capacity |
| `latitude` | Decimal degrees |
| `longitude` | Decimal degrees |
| `source` | e.g. `fifa_official_manual` |

- [ ] All 16 stadiums filled
- [ ] Timezones verified (critical for kickoff_utc calculation)

Apply:
```bash
python scripts/apply_official_import.py --target venues --file data/official/import_templates/official_venues_import_template.csv
```

---

### 4. Fixtures — `official_fixtures_import_template.csv`

Required: **104 rows** (72 group-stage + 32 knockout).

| Column | Notes |
|--------|-------|
| `match_id` | Unique ID, e.g. `WC2026_001` |
| `match_number` | Sequential 1–104 |
| `stage` | `group_stage`, `round_of_32`, `round_of_16`, `quarter_final`, `semi_final`, `third_place`, `final` |
| `group` | A–L for group stage; blank for knockouts |
| `date` | YYYY-MM-DD |
| `kickoff_local` | HH:MM in local venue time |
| `kickoff_utc` | ISO datetime, e.g. `2026-06-11T20:00:00Z` |
| `timezone` | IANA timezone matching the venue |
| `venue` | Must match `venue` column in venues file |
| `stadium` | Must match venues file |
| `city` | Must match venues file |
| `country` | USA / Canada / Mexico |
| `team_a` | Team name (group stage) or placeholder (knockout) |
| `team_b` | Team name (group stage) or placeholder (knockout) |
| `team_a_code` | FIFA code or TBD for knockouts |
| `team_b_code` | FIFA code or TBD for knockouts |
| `team_a_group_slot` | e.g. `A1` |
| `team_b_group_slot` | e.g. `B2` |
| `status` | `scheduled` |
| `source` | e.g. `fifa_official_manual` |

- [ ] 72 group-stage fixtures (6 per group × 12 groups)
- [ ] 32 knockout fixtures/placeholders
- [ ] All `kickoff_local` and `kickoff_utc` verified
- [ ] All `timezone` values verified against venues

Apply:
```bash
python scripts/apply_official_import.py --target fixtures --file data/official/import_templates/official_fixtures_import_template.csv
```

After all four: re-run readiness:
```bash
python scripts/evaluate_official_final_readiness.py
```

---

## Step 17F: Players and Priors

> Fill only after Step 17E passes (teams, groups, venues, fixtures all verified).

### 5. Players — `official_players_import_template.csv`

Required: **1,248 rows** (48 teams × 26 players).

| Column | Notes |
|--------|-------|
| `player_id` | Unique, e.g. `BRA_001` |
| `team` | Must match teams file exactly |
| `team_code` | Must match teams file exactly |
| `shirt_number` | 1–99 |
| `position_code` | GK / DF / MF / FW |
| `position` | goalkeeper / defender / midfielder / forward |
| `player_name` | Full name |
| `first_names` | Given names |
| `last_names` | Family name |
| `name_on_shirt` | As printed on shirt |
| `date_of_birth` | YYYY-MM-DD |
| `age_at_tournament_start` | Integer age on 2026-06-11 |
| `club` | Current club |
| `club_country` | Country of the club |
| `height_cm` | Integer |
| `source` | e.g. `fifa_official_manual` |

- [ ] Exactly 26 players per team
- [ ] All 48 teams represented
- [ ] 1,248 total rows
- [ ] No `sample_to_be_verified` players

Apply:
```bash
python scripts/apply_official_import.py --target players --file data/official/import_templates/official_players_import_template.csv --preview
python scripts/apply_official_import.py --target players --file data/official/import_templates/official_players_import_template.csv
```

---

### 6. Player priors — `player_award_priors_import_template.csv`

Required: **1,248 rows** (one row per official squad player).

| Column | Notes |
|--------|-------|
| `player` | Must match `player_name` in players file |
| `team` | Must match teams file |
| `base_player_rating` | 0.0–1.0 (e.g. 0.85 for world-class) |
| `expected_minutes_share` | 0.0–1.0 fraction of team minutes expected |
| `goals_prior` | Expected goals in tournament |
| `assists_prior` | Expected assists |
| `chance_creation_prior` | 0.0–1.0 |
| `defensive_actions_prior` | 0.0–1.0 |
| `goalkeeper_actions_prior` | 0.0–1.0 (non-GK set to 0) |
| `discipline_risk` | 0.0–1.0 |
| `star_role_score` | 0.0–1.0 |
| `flair_score` | 0.0–1.0 |
| `notes` | Free text |
| `source` | e.g. `manual_estimate` |

- [ ] 1,248 rows, one per official player
- [ ] Ratings are reasonable (0–1 scale)

Apply:
```bash
python scripts/apply_official_import.py --target player_priors --file data/official/import_templates/player_award_priors_import_template.csv
```

---

## Final promotion

Once all six datasets are verified:

```bash
python scripts/evaluate_official_final_readiness.py
python scripts/promote_official_final.py --confirm
```

Promotion only succeeds when **all** of the following are true:

| Check | Target |
|-------|--------|
| Teams | 48 / 48 |
| Groups | 12 groups × 4 teams |
| Venues | 16+ verified |
| Fixtures | 104 / 104 |
| Players | 1,248 / 1,248 |
| Teams with 26 players | 48 / 48 |
| `sample_to_be_verified` rows | 0 |
| Blocking placeholders | 0 |
| Data consistency | Pass |

---

## After promotion: Step 18

Only when `official_final_enabled = true` should you implement the awards predictor.  
Awards based on incomplete squads are not trustworthy.

---

*No scraping. No OCR. No automatic data fetch. Fill from verified official FIFA sources only.*
