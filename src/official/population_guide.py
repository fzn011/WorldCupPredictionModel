"""User-facing guide generation for official data population (Step 17D)."""

from __future__ import annotations

from pathlib import Path

import src.utils.constants as C


def generate_population_guide_markdown() -> str:
    """Generate a detailed markdown guide for manual official data population."""
    return f"""# Official World Cup 2026 Data Population Guide

## 1. Overview

This guide explains how to manually populate verified FIFA World Cup 2026 data into the
predictor system. **The application does not scrape websites, use OCR, or call paid APIs.**
You must copy data from official FIFA sources and enter it into the import templates yourself.

Population pack artifacts live under `{C.OFFICIAL_POPULATION_DIR}/`.

## 2. Data modes

| Mode | Description |
|------|-------------|
| **sample** | Uses bundled sample/fallback data for development and demos |
| **official_draft** | Official file structure with partially filled or template data |
| **official_final** | All readiness checks pass; promotion flag enabled only after verification |

`official_final` remains **blocked** until every readiness check passes. Do not mark data as
verified unless you have confirmed it against FIFA sources.

## 3. Required files

| Dataset | Target rows | Output file |
|---------|-------------|-------------|
| Teams | 48 | `official_teams.csv` |
| Groups | 48 (12×4) | `official_groups.csv` |
| Fixtures | 104 (72 group + 32 knockout) | `official_fixtures.csv` |
| Venues | 16+ | `official_venues.csv` |
| Players | 1,248 (48×26) | `official_players.csv` |
| Player priors | 1,248 | `player_award_priors.csv` |

Import templates are generated under `{C.OFFICIAL_IMPORT_TEMPLATES_DIR}/`.

## 4. Teams template instructions

Fill `official_teams_import_template.csv` with all 48 qualified teams.

Required columns: {", ".join(C.IMPORT_TEAMS_REQUIRED_COLUMNS)}

- Use official FIFA team names and three-letter codes
- Set `group` (A–L) and `group_slot` (1–4) from the official draw
- Set `is_host` to 1 for USA, Canada, Mexico hosts
- Set `source` to a descriptive value (e.g. `fifa_official_manual`) — **not** `sample_to_be_verified`

## 5. Groups template instructions

Fill `official_groups_import_template.csv` with 48 rows (4 teams per group, 12 groups).

Required columns: {", ".join(C.IMPORT_GROUPS_REQUIRED_COLUMNS)}

- Each group must have exactly 4 teams
- `slot` values should be 1–4 within each group

## 6. Fixtures template instructions

Fill `official_fixtures_import_template.csv` with all 104 matches.

Required columns: {", ".join(C.IMPORT_FIXTURES_REQUIRED_COLUMNS)}

- 72 group-stage fixtures (6 per group)
- 32 knockout fixtures/placeholders through the final
- Verify `kickoff_local`, `kickoff_utc`, and `timezone` for every row
- Verify `city`, `country`, and `venue`/`stadium` against FIFA schedule

## 7. Venues template instructions

Fill `official_venues_import_template.csv` with all tournament stadiums.

Required columns: {", ".join(C.IMPORT_VENUES_REQUIRED_COLUMNS)}

- Include capacity, city, country, timezone, and coordinates when available

## 8. Players template instructions

Fill `official_players_import_template.csv` with 1,248 players (26 per team).

Required columns: {", ".join(C.IMPORT_PLAYERS_REQUIRED_COLUMNS)}

- One row per squad player with unique `player_id`
- Use official squad lists from FIFA when published

## 9. Player priors template instructions

Fill `player_award_priors_import_template.csv` after players are registered.

Required columns: {", ".join(C.IMPORT_PLAYER_PRIORS_REQUIRED_COLUMNS)}

- Priors are editable estimates used later for awards (Step 18)
- **Awards predictions must wait** until `official_players.csv` is complete
- Only official squad players should appear in priors

## 10. Applying imports

```bash
# Step 1: preview diff (always preview first)
python scripts/preview_official_import.py --target players --file data/official/import_templates/official_players_import_template.csv
python scripts/apply_official_import.py --target players --file data/official/import_templates/official_players_import_template.csv --preview

# Step 2: apply for real (creates automatic backup)
python scripts/apply_official_import.py --target players --file data/official/import_templates/official_players_import_template.csv
```

Apply in dependency order — teams before groups, groups before fixtures, players before priors:

```bash
python scripts/apply_official_import.py --target teams         --file data/official/import_templates/official_teams_import_template.csv
python scripts/apply_official_import.py --target groups        --file data/official/import_templates/official_groups_import_template.csv
python scripts/apply_official_import.py --target venues        --file data/official/import_templates/official_venues_import_template.csv
python scripts/apply_official_import.py --target fixtures      --file data/official/import_templates/official_fixtures_import_template.csv
python scripts/apply_official_import.py --target players       --file data/official/import_templates/official_players_import_template.csv
python scripts/apply_official_import.py --target player_priors --file data/official/import_templates/player_award_priors_import_template.csv
```

See `data/official/population/FILL_DATA_CHECKLIST.md` for column-by-column instructions.

After each import, re-run readiness:

```bash
python scripts/evaluate_official_final_readiness.py
```

## 11. Running readiness checks

```bash
python scripts/evaluate_official_final_readiness.py --save
python scripts/prepare_official_population_pack.py
```

The readiness report checks 15 items including row counts, placeholders, sample rows,
and cross-dataset consistency.

## 12. Promoting to official_final

Promotion requires explicit confirmation **and** full readiness:

```bash
python scripts/promote_official_final.py          # shows status, requires --confirm
python scripts/promote_official_final.py --confirm  # only succeeds when final_ready is true
python scripts/promote_official_final.py --demote --reason "Data needs review"
```

Do **not** promote until all blockers are resolved.

## 13. Troubleshooting

| Issue | Resolution |
|-------|------------|
| Wrong row count | Ensure templates have exact required rows before applying |
| Placeholder values detected | Replace `TBD`, `Unknown`, `sample_to_be_verified` with real values |
| Groups/teams mismatch | Re-check group draw against teams file |
| Import validation failed | Compare your CSV columns to the template headers |
| Promotion blocked | Run missing-data report and fix all blockers first |

## 14. Final checklist

- [ ] 48 teams verified
- [ ] 12 groups × 4 teams
- [ ] 104 fixtures with kickoff times and venues
- [ ] All venues/stadiums verified
- [ ] 48 squads × 26 players = 1,248 players
- [ ] Player priors filled for official players
- [ ] Zero `sample_to_be_verified` rows
- [ ] Zero blocking placeholders
- [ ] Final readiness evaluation passes
- [ ] Promotion to `official_final` confirmed

---

*Generated by Step 17D Official Data Population Pack. No automatic data fetching is performed.*
"""


def save_population_guide(output_path: str | None = None) -> str:
    """Save the population guide markdown file."""
    if output_path is None:
        output_path = str(
            C.PROJECT_ROOT / C.OFFICIAL_POPULATION_DIR / C.OFFICIAL_POPULATION_GUIDE_FILE
        )
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(generate_population_guide_markdown(), encoding="utf-8")
    return str(path)
