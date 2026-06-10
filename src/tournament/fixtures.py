"""Tournament fixture generation, loading, validation, and persistence."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.official.loaders import load_official_fixtures, load_official_teams, load_official_venues
from src.official.validators import validate_official_fixtures
import src.utils.constants as C
from src.tournament.groups import create_group_lookup, load_tournament_groups
from src.utils.team_name_mapping import standardize_team_name

PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")
SAMPLE_DATA_DIR = getattr(C, "SAMPLE_DATA_DIR", Path("data") / "sample")
TOURNAMENT_FIXTURES_FILE = getattr(C, "TOURNAMENT_FIXTURES_FILE", "tournament_fixtures.csv")
TOURNAMENT_STAGE_GROUP = getattr(C, "TOURNAMENT_STAGE_GROUP", "group_stage")
WC2026_GROUPS = getattr(C, "WC2026_GROUPS", ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"])
WC2026_GROUP_MATCHES_PER_GROUP = getattr(C, "WC2026_GROUP_MATCHES_PER_GROUP", 6)
WC2026_TOTAL_GROUP_MATCHES = getattr(C, "WC2026_TOTAL_GROUP_MATCHES", 72)
DATA_MODE_OFFICIAL = getattr(C, "DATA_MODE_OFFICIAL", "official")

REQUIRED_FIXTURE_COLUMNS: list[str] = [
    "match_id",
    "stage",
    "group",
    "matchday",
    "date",
    "venue",
    "city",
    "country",
    "team_a_slot",
    "team_b_slot",
    "team_a",
    "team_b",
]

GROUP_SLOT_PATTERN: list[tuple[int, int, int]] = [
    (1, 1, 2),
    (1, 3, 4),
    (2, 1, 3),
    (2, 4, 2),
    (3, 4, 1),
    (3, 2, 3),
]


def _report_row(check: str, passed: bool, details: str) -> dict[str, object]:
    return {"section": "fixtures", "check": check, "passed": bool(passed), "details": details}


def generate_group_stage_fixtures(groups_df: pd.DataFrame) -> pd.DataFrame:
    """Generate 72 group-stage fixtures from group slot assignments."""
    lookup = create_group_lookup(groups_df)
    base_date = pd.Timestamp("2026-06-11")

    rows: list[dict[str, object]] = []
    for group_index, group in enumerate(WC2026_GROUPS):
        slot_map = lookup.get(group, {})
        for idx, (matchday, slot_a, slot_b) in enumerate(GROUP_SLOT_PATTERN, start=1):
            date_value = (base_date + pd.Timedelta(days=group_index + (matchday - 1) * 5)).date().isoformat()
            rows.append(
                {
                    "match_id": f"G-{group}-{idx:02d}",
                    "stage": TOURNAMENT_STAGE_GROUP,
                    "group": group,
                    "matchday": matchday,
                    "date": date_value,
                    "venue": f"TBD Venue {group}",
                    "city": "TBD City",
                    "country": "TBD Country",
                    "team_a_slot": slot_a,
                    "team_b_slot": slot_b,
                    "team_a": slot_map.get(slot_a, f"{group}{slot_a}"),
                    "team_b": slot_map.get(slot_b, f"{group}{slot_b}"),
                }
            )

    return pd.DataFrame(rows, columns=REQUIRED_FIXTURE_COLUMNS)


def load_tournament_fixtures(path: str | None = None, data_mode: str | None = None) -> pd.DataFrame:
    """Load processed fixtures, sample fixtures, generated fixtures, or official-mode fixtures."""
    if data_mode == DATA_MODE_OFFICIAL and path is None:
        official_df = load_official_fixtures()
        teams_df = load_official_teams()
        venues_df = load_official_venues()
        valid, report_df = validate_official_fixtures(official_df, teams_df=teams_df, venues_df=venues_df)
        failed = report_df[(report_df["passed"] == False) & (report_df["severity"] == "error")]
        if not failed.empty:
            raise ValueError(f"Official tournament fixtures failed validation: {failed.to_dict(orient='records')[:5]}")

        out = pd.DataFrame(
            {
                "match_id": official_df["match_id"],
                "stage": official_df["stage"],
                "group": official_df["group"],
                "matchday": pd.NA,
                "date": official_df["date"],
                "venue": official_df["venue"],
                "city": official_df["city"],
                "country": official_df["country"],
                "team_a_slot": pd.to_numeric(official_df["team_a_group_slot"], errors="coerce").astype("Int64"),
                "team_b_slot": pd.to_numeric(official_df["team_b_group_slot"], errors="coerce").astype("Int64"),
                "team_a": official_df["team_a"].map(standardize_team_name),
                "team_b": official_df["team_b"].map(standardize_team_name),
            }
        )
        return out[REQUIRED_FIXTURE_COLUMNS].copy()

    if path:
        file_path = Path(path)
        if not file_path.is_file():
            raise FileNotFoundError(f"Tournament fixtures file not found at {file_path}")
        df = pd.read_csv(file_path)
    else:
        processed_path = PROCESSED_DATA_DIR / TOURNAMENT_FIXTURES_FILE
        sample_path = SAMPLE_DATA_DIR / "sample_tournament_schedule.csv"
        if processed_path.is_file():
            df = pd.read_csv(processed_path)
        elif sample_path.is_file():
            df = pd.read_csv(sample_path)
        else:
            groups_df = load_tournament_groups()
            df = generate_group_stage_fixtures(groups_df)

    missing = [column for column in REQUIRED_FIXTURE_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Tournament fixtures missing required columns: {missing}")

    out = df.copy()
    out["group"] = out["group"].astype(str).str.upper()
    out["stage"] = out["stage"].astype(str).str.strip()
    out["team_a"] = out["team_a"].map(standardize_team_name)
    out["team_b"] = out["team_b"].map(standardize_team_name)
    out["team_a_slot"] = pd.to_numeric(out["team_a_slot"], errors="coerce").astype("Int64")
    out["team_b_slot"] = pd.to_numeric(out["team_b_slot"], errors="coerce").astype("Int64")
    out["matchday"] = pd.to_numeric(out["matchday"], errors="coerce").astype("Int64")
    return out


def validate_group_stage_fixtures(fixtures_df: pd.DataFrame, groups_df: pd.DataFrame) -> tuple[bool, pd.DataFrame]:
    """Validate group-stage fixtures for structural correctness."""
    rows: list[dict[str, object]] = []

    group_fixtures = fixtures_df.loc[fixtures_df["stage"] == TOURNAMENT_STAGE_GROUP].copy()

    rows.append(
        _report_row(
            "total_group_matches_72",
            len(group_fixtures) == WC2026_TOTAL_GROUP_MATCHES,
            f"expected={WC2026_TOTAL_GROUP_MATCHES}, found={len(group_fixtures)}",
        )
    )

    per_group = group_fixtures.groupby("group")["match_id"].count().to_dict() if not group_fixtures.empty else {}
    per_group_ok = (
        len(per_group) == len(WC2026_GROUPS)
        and all(count == WC2026_GROUP_MATCHES_PER_GROUP for count in per_group.values())
    )
    rows.append(_report_row("matches_per_group_6", per_group_ok, f"counts={per_group}"))

    team_games = pd.concat(
        [
            group_fixtures[["group", "team_a"]].rename(columns={"team_a": "team"}),
            group_fixtures[["group", "team_b"]].rename(columns={"team_b": "team"}),
        ],
        ignore_index=True,
    )
    team_game_counts = team_games.groupby(["group", "team"]).size().to_dict() if not team_games.empty else {}
    plays_three = bool(team_game_counts) and all(count == 3 for count in team_game_counts.values())
    rows.append(_report_row("each_team_plays_3_group_matches", plays_three, f"sample={dict(list(team_game_counts.items())[:8])}"))

    no_self_match = bool((group_fixtures["team_a"] != group_fixtures["team_b"]).all()) if not group_fixtures.empty else False
    rows.append(_report_row("no_team_plays_itself", no_self_match, "team_a != team_b for all fixtures"))

    known_teams = set(groups_df["team"].astype(str).tolist())
    fixture_teams = set(group_fixtures["team_a"].astype(str).tolist()) | set(group_fixtures["team_b"].astype(str).tolist())
    unknown = sorted(fixture_teams - known_teams)
    rows.append(_report_row("all_teams_exist_in_groups", len(unknown) == 0, "all teams mapped" if not unknown else f"unknown={unknown}"))

    unique_match_id = group_fixtures["match_id"].nunique() == len(group_fixtures)
    rows.append(_report_row("match_id_unique", unique_match_id, f"unique={group_fixtures['match_id'].nunique()}, total={len(group_fixtures)}"))

    valid_groups = sorted(group_fixtures["group"].dropna().unique().tolist()) == sorted(WC2026_GROUPS)
    rows.append(_report_row("group_labels_valid", valid_groups, f"found={sorted(group_fixtures['group'].dropna().unique().tolist())}"))

    valid_stage = (group_fixtures["stage"] == TOURNAMENT_STAGE_GROUP).all() if not group_fixtures.empty else False
    rows.append(_report_row("stage_is_group_stage", bool(valid_stage), "stage values checked"))

    report_df = pd.DataFrame(rows)
    return bool(report_df["passed"].all()), report_df


def save_tournament_fixtures(fixtures_df: pd.DataFrame, output_path: str | None = None) -> str:
    """Save fixtures to processed data folder."""
    path = Path(output_path) if output_path else PROCESSED_DATA_DIR / TOURNAMENT_FIXTURES_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    fixtures_df.to_csv(path, index=False)
    return str(path)
