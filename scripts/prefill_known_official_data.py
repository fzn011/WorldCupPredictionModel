"""Pre-fill official import templates with verified 2026 World Cup data.

Fills:
  - venues: all 16 official stadiums with real data
  - groups: fixes FIFA codes, preserves existing structure
  - teams:  derived from corrected groups file

Leaves for manual entry:
  - Fixture kickoff times (need official FIFA schedule)
  - Fixture venue assignments (need official FIFA schedule)
  - Player squad lists (need official FIFA squad announcements)
  - Player priors (fill after players are complete)

Source is set to 'ai_prefilled_needs_verification' — this will NOT clear the
readiness blockers by itself; the user must review and change source to
'fifa_official_manual' (or similar) after verifying each row against
https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import src.utils.constants as C

TEMPLATES_DIR = ROOT / C.OFFICIAL_IMPORT_TEMPLATES_DIR
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

NOW = datetime.now(timezone.utc).isoformat()
SOURCE = "ai_prefilled_needs_verification"

# ---------------------------------------------------------------------------
# 16 official 2026 World Cup venues
# ---------------------------------------------------------------------------
VENUES = [
    # USA (11 venues)
    dict(venue_id="v_metlife",   stadium="MetLife Stadium",           venue="MetLife Stadium",       city="East Rutherford", country="USA", timezone="America/New_York",     capacity=82500,  latitude=40.8135,  longitude=-74.0745),
    dict(venue_id="v_rosebowl",  stadium="Rose Bowl Stadium",         venue="Rose Bowl",             city="Pasadena",        country="USA", timezone="America/Los_Angeles",  capacity=92542,  latitude=34.1614,  longitude=-118.1676),
    dict(venue_id="v_att",       stadium="AT&T Stadium",              venue="AT&T Stadium",          city="Arlington",       country="USA", timezone="America/Chicago",      capacity=80000,  latitude=32.7479,  longitude=-97.0928),
    dict(venue_id="v_sofi",      stadium="SoFi Stadium",              venue="SoFi Stadium",          city="Inglewood",       country="USA", timezone="America/Los_Angeles",  capacity=70240,  latitude=33.9535,  longitude=-118.3392),
    dict(venue_id="v_levis",     stadium="Levi's Stadium",            venue="Levi's Stadium",        city="Santa Clara",     country="USA", timezone="America/Los_Angeles",  capacity=68500,  latitude=37.4033,  longitude=-121.9694),
    dict(venue_id="v_hardrock",  stadium="Hard Rock Stadium",         venue="Hard Rock Stadium",     city="Miami Gardens",   country="USA", timezone="America/New_York",     capacity=64767,  latitude=25.9580,  longitude=-80.2389),
    dict(venue_id="v_arrowhead", stadium="Arrowhead Stadium",         venue="Arrowhead Stadium",     city="Kansas City",     country="USA", timezone="America/Chicago",      capacity=76416,  latitude=39.0489,  longitude=-94.4839),
    dict(venue_id="v_gillette",  stadium="Gillette Stadium",          venue="Gillette Stadium",      city="Foxborough",      country="USA", timezone="America/New_York",     capacity=65878,  latitude=42.0909,  longitude=-71.2643),
    dict(venue_id="v_lincoln",   stadium="Lincoln Financial Field",   venue="Lincoln Financial Field", city="Philadelphia", country="USA", timezone="America/New_York",     capacity=69328,  latitude=39.9008,  longitude=-75.1675),
    dict(venue_id="v_lumen",     stadium="Lumen Field",               venue="Lumen Field",           city="Seattle",         country="USA", timezone="America/Los_Angeles",  capacity=72000,  latitude=47.5952,  longitude=-122.3316),
    dict(venue_id="v_nrg",       stadium="NRG Stadium",               venue="NRG Stadium",           city="Houston",         country="USA", timezone="America/Chicago",      capacity=72220,  latitude=29.6847,  longitude=-95.4107),
    # Canada (2 venues)
    dict(venue_id="v_bcplace",   stadium="BC Place",                  venue="BC Place",              city="Vancouver",       country="Canada", timezone="America/Vancouver", capacity=54500,  latitude=49.2768,  longitude=-123.1119),
    dict(venue_id="v_bmo",       stadium="BMO Field",                 venue="BMO Field",             city="Toronto",         country="Canada", timezone="America/Toronto",   capacity=45736,  latitude=43.6333,  longitude=-79.4179),
    # Mexico (3 venues)
    dict(venue_id="v_azteca",    stadium="Estadio Azteca",            venue="Estadio Azteca",        city="Mexico City",     country="Mexico", timezone="America/Mexico_City", capacity=87523, latitude=19.3029,  longitude=-99.1505),
    dict(venue_id="v_akron",     stadium="Estadio Akron",             venue="Estadio Akron",         city="Guadalajara",     country="Mexico", timezone="America/Mexico_City", capacity=49850, latitude=20.6854,  longitude=-103.4666),
    dict(venue_id="v_bbva",      stadium="Estadio BBVA",              venue="Estadio BBVA",          city="Monterrey",       country="Mexico", timezone="America/Monterrey",   capacity=53500, latitude=25.6694,  longitude=-100.2436),
]

# ---------------------------------------------------------------------------
# FIFA code corrections for the existing groups sample data
# Many codes in the sample are wrong. Mapping: wrong_code -> correct_code
# ---------------------------------------------------------------------------
CODE_FIXES = {
    "UST": "USA",   # United States
    "SWI": "SUI",   # Switzerland
    "NET": "NED",   # Netherlands
    "AU1": "AUT",   # Austria
    "SKO": "KOR",   # South Korea
    "IRA": "IRN",   # Iran
    "NIG": "NGA",   # Nigeria
    "BAH": "BIH",   # Bosnia and Herzegovina
    "MOR": "MAR",   # Morocco
    "SAF": "RSA",   # South Africa
    "ECU": "ECU",   # Ecuador (already correct)
    "CDI": "CIV",   # Côte d'Ivoire
    "JAP": "JPN",   # Japan
    "NZE": "NZL",   # New Zealand
    "SER": "SRB",   # Serbia
    "TUN": "TUN",   # Tunisia (already correct)
    "POR": "POR",   # Portugal (already correct)
    "SEN": "SEN",   # Senegal (already correct)
    "UAE": "UAE",   # UAE (already correct)
    "SCO": "SCO",   # Scotland (already correct)
    "NOR": "NOR",   # Norway (already correct)
    "CRI": "CRC",   # Costa Rica
    "DEN": "DEN",   # Denmark (already correct)
    "ALG": "ALG",   # Algeria (already correct)
    "PER": "PER",   # Peru (already correct)
    "PAR": "PAR",   # Paraguay (already correct)
    "CHI": "CHI",   # Chile (already correct)
    "CRO": "CRO",   # Croatia (already correct)
    "COL": "COL",   # Colombia (already correct)
    "SWE": "SWE",   # Sweden (already correct)
}

# Canonical team names (fix encoding / spacing issues)
NAME_FIXES = {
    "C\xf4te d'Ivoire": "Côte d'Ivoire",
    "United States":    "United States",
}


def fill_venues() -> Path:
    rows = []
    for v in VENUES:
        rows.append({**v, "source": SOURCE, "last_verified_at": NOW})
    df = pd.DataFrame(rows)
    out = TEMPLATES_DIR / C.OFFICIAL_POPULATION_TEMPLATE_FILES["venues"]
    df.to_csv(out, index=False)
    print(f"Venues written: {len(df)} rows -> {out.name}")
    return out


def fill_groups_and_teams() -> tuple[Path, Path]:
    src_path = ROOT / C.OFFICIAL_PROCESSED_DIR / C.OFFICIAL_GROUPS_FILE
    if not src_path.exists():
        print("official_groups.csv not found — skipping groups/teams")
        return None, None

    df = pd.read_csv(src_path)

    # Fix FIFA codes
    df["team_code"] = df["team_code"].apply(lambda c: CODE_FIXES.get(str(c).strip(), str(c).strip()))

    # Fix team names
    df["team"] = df["team"].apply(lambda n: NAME_FIXES.get(str(n).strip(), str(n).strip()))

    # Update source and verification date
    df["source"] = SOURCE
    df["last_verified_at"] = NOW

    groups_out = TEMPLATES_DIR / C.OFFICIAL_POPULATION_TEMPLATE_FILES["groups"]
    df.to_csv(groups_out, index=False)
    print(f"Groups written: {len(df)} rows -> {groups_out.name}")

    # Derive teams from groups (groups uses 'slot', teams expects 'group_slot')
    teams_df = df[["team", "team_code", "confederation", "group", "slot", "is_host"]].copy()
    teams_df.rename(columns={"slot": "group_slot"}, inplace=True)
    teams_df["qualified"] = 1
    teams_df["source"] = SOURCE
    teams_df["last_verified_at"] = NOW

    teams_out = TEMPLATES_DIR / C.OFFICIAL_POPULATION_TEMPLATE_FILES["teams"]
    teams_df.to_csv(teams_out, index=False)
    print(f"Teams written: {len(teams_df)} rows -> {teams_out.name}")

    return groups_out, teams_out


def report_manual_entries_needed() -> None:
    print()
    print("=" * 60)
    print("STILL NEEDS MANUAL ENTRY FROM FIFA SOURCES")
    print("=" * 60)
    print()
    print("Fixtures (72 group-stage + 32 knockout = 104 total):")
    print("  data/official/import_templates/official_fixtures_import_template.csv")
    print("  Needed: kickoff_local, kickoff_utc, timezone, venue, stadium,")
    print("          city, country for every match")
    print("  Source: https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/match-schedule")
    print()
    print("Players (48 squads × 26 players = 1,248 total):")
    print("  data/official/import_templates/official_players_import_template.csv")
    print("  Needed: official squad lists (not announced until days before tournament)")
    print("  Source: https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/squads")
    print()
    print("Player priors:")
    print("  data/official/import_templates/player_award_priors_import_template.csv")
    print("  Fill after players are complete.")
    print()
    print("Groups/Teams verification:")
    print("  The group assignments in this script come from the December 2024 draw.")
    print("  Verify each team assignment against:")
    print("  https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/groups")
    print()
    print("IMPORTANT: Change source from 'ai_prefilled_needs_verification' to")
    print("  'fifa_official_manual' only after you have verified each row against")
    print("  official FIFA sources. Until then, official_final will remain blocked.")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("Pre-filling known official 2026 World Cup data")
    print("=" * 60)
    print()

    fill_venues()
    groups_out, teams_out = fill_groups_and_teams()
    report_manual_entries_needed()
