# Official World Cup 2026 Master Import Workbook

## Purpose

This workbook (or CSV template pack fallback) supports **manual** entry of verified FIFA
World Cup 2026 data. The application does not fetch or auto-fill official data.

## Sheets

| Sheet | Required rows | Description |
|-------|---------------|-------------|
| Teams | 48 | Qualified teams with group assignments |
| Groups | 48 | Group compositions (12×4) |
| Fixtures | 104 | Full schedule including knockouts |
| Venues | 16+ | Stadium details |
| Players | 1248 | Squad lists (26 per team) |
| Player_Priors | 1248 | Editable priors for official players |
| Validation_Rules | — | Row counts and field rules |

## Workflow

1. Fill each sheet from official FIFA sources
2. Export individual sheets to CSV matching import template column headers
3. Preview: `python scripts/preview_official_import.py --target <type> --file <csv>`
4. Apply: `python scripts/apply_official_import.py --type <type> <csv>`
5. Re-run readiness: `python scripts/evaluate_official_final_readiness.py`

## Verification fields

When filling data, include where possible: source, last_verified_at, verified_by, verification_notes

Do **not** use `sample_to_be_verified` as a source value for production data.
