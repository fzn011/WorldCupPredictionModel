"""Temporary helper: adds 32 knockout placeholder fixtures to the fixtures import template."""
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

ROOT = Path(__file__).parent.parent
fixtures_path = ROOT / "data/official/processed/official_fixtures.csv"
template_path = ROOT / "data/official/import_templates/official_fixtures_import_template.csv"

df = pd.read_csv(fixtures_path)

NOW = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
SOURCE = "ai_prefilled_needs_verification"

knockouts = []
mn = 73  # continue from match 72


def add_matches(stage, count, start_date_str):
    global mn
    base = datetime.strptime(start_date_str, "%Y-%m-%d")
    for i in range(count):
        day_offset = i // 2
        mid = f"{stage[:3].upper()}-{i+1:02d}"
        knockouts.append({
            "match_id": mid, "match_number": mn, "stage": stage,
            "group": "", "date": (base + timedelta(days=day_offset)).strftime("%Y-%m-%d"),
            "kickoff_local": "TBD", "kickoff_utc": "TBD", "timezone": "TBD",
            "venue": "TBD", "stadium": "TBD", "city": "TBD", "country": "TBD",
            "team_a": f"TBD{2*i+1}", "team_b": f"TBD{2*i+2}",
            "team_a_code": "TBD", "team_b_code": "TBD",
            "team_a_group_slot": "", "team_b_group_slot": "",
            "status": "scheduled", "source": SOURCE, "last_verified_at": NOW,
        })
        mn += 1


add_matches("round_of_32", 16, "2026-07-04")
add_matches("round_of_16", 8,  "2026-07-10")
add_matches("quarter_final", 4, "2026-07-15")
add_matches("semi_final", 2,   "2026-07-18")

# Third-place play-off
knockouts.append({
    "match_id": "3P-01", "match_number": mn, "stage": "third_place",
    "group": "", "date": "2026-07-22",
    "kickoff_local": "TBD", "kickoff_utc": "TBD", "timezone": "TBD",
    "venue": "TBD", "stadium": "TBD", "city": "TBD", "country": "TBD",
    "team_a": "TBD", "team_b": "TBD",
    "team_a_code": "TBD", "team_b_code": "TBD",
    "team_a_group_slot": "", "team_b_group_slot": "",
    "status": "scheduled", "source": SOURCE, "last_verified_at": NOW,
})
mn += 1

# Final
knockouts.append({
    "match_id": "FIN-01", "match_number": mn, "stage": "final",
    "group": "", "date": "2026-07-19",
    "kickoff_local": "TBD", "kickoff_utc": "TBD", "timezone": "TBD",
    "venue": "AT&T Stadium", "stadium": "AT&T Stadium", "city": "Arlington", "country": "USA",
    "team_a": "TBD", "team_b": "TBD",
    "team_a_code": "TBD", "team_b_code": "TBD",
    "team_a_group_slot": "", "team_b_group_slot": "",
    "status": "scheduled", "source": SOURCE, "last_verified_at": NOW,
})

ko_df = pd.DataFrame(knockouts)
merged = pd.concat([df, ko_df], ignore_index=True)
merged.to_csv(template_path, index=False)

print(f"Total fixtures in template: {len(merged)}")
stage_counts = merged["stage"].value_counts().to_dict()
for s, c in stage_counts.items():
    print(f"  {s}: {c}")
