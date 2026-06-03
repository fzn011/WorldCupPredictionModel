"""Match-data cleaning helpers (Step 3)."""

from __future__ import annotations

import hashlib

import pandas as pd

import src.utils.constants as C
from src.utils.team_name_mapping import (
    slugify_team_name,
    standardize_team_name,
)

CANONICAL_MATCH_COLUMNS = getattr(
    C,
    "CANONICAL_MATCH_COLUMNS",
    [
        "match_id",
        "date",
        "year",
        "team_a",
        "team_b",
        "team_a_score",
        "team_b_score",
        "score_difference",
        "total_goals",
        "result",
        "result_label",
        "winner",
        "loser",
        "is_draw",
        "tournament",
        "city",
        "country",
        "neutral",
        "has_shootout",
        "shootout_winner",
        "shootout_loser",
        "progression_winner",
        "data_source",
    ],
)
RESULT_LABELS = getattr(C, "RESULT_LABELS", {0: "team_a_loss", 1: "draw", 2: "team_a_win"})
SHOOTOUT_OUTCOME_COLUMNS = getattr(
    C,
    "SHOOTOUT_OUTCOME_COLUMNS",
    ["date", "team_a", "team_b", "shootout_winner", "shootout_loser"],
)
TEAM_REGISTRY_COLUMNS = getattr(
    C,
    "TEAM_REGISTRY_COLUMNS",
    [
        "team_id",
        "team",
        "team_slug",
        "first_match_date",
        "last_match_date",
        "matches_played",
        "is_world_cup_2026_host",
    ],
)
WORLD_CUP_2026_HOSTS = getattr(C, "WORLD_CUP_2026_HOSTS", ["Canada", "Mexico", "United States"])

# Minimal canonical schema kept for backward compatibility with Step 1/2 code.
BASIC_CANONICAL_COLUMNS: list[str] = [
    "date",
    "team_a",
    "team_b",
    "team_a_score",
    "team_b_score",
    "result",
    "tournament",
    "city",
    "country",
    "neutral",
]


def clean_match_results(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy of a canonical match-results DataFrame."""
    cleaned = df.copy()

    for col in ("team_a", "team_b"):
        if col in cleaned.columns:
            cleaned[col] = cleaned[col].map(standardize_team_name)

    if "date" in cleaned.columns:
        cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")

    cleaned = cleaned.drop_duplicates().reset_index(drop=True)
    return cleaned


def create_match_result_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add a ``result`` column encoded from team_a's perspective.

    Encoding:
        * 2 — team_a win
        * 1 — draw
        * 0 — team_a loss
    """
    if "team_a_score" not in df.columns or "team_b_score" not in df.columns:
        raise ValueError(
            "DataFrame must contain 'team_a_score' and 'team_b_score' columns."
        )

    out = df.copy()
    a = out["team_a_score"]
    b = out["team_b_score"]
    out["result"] = 1
    out.loc[a > b, "result"] = 2
    out.loc[a < b, "result"] = 0
    return out


# -----------------------------------------------------------------------------
# Step 3: deep cleaning of raw historical results
# -----------------------------------------------------------------------------

def _coerce_neutral(series: pd.Series) -> pd.Series:
    """Convert a neutral-venue column to integer 0/1 (default 0)."""
    mapping = {
        True: 1,
        False: 0,
        "true": 1,
        "false": 0,
        "1": 1,
        "0": 0,
        "yes": 1,
        "no": 0,
    }

    def _map(value: object) -> int:
        if value in mapping:
            return mapping[value]
        return mapping.get(str(value).strip().lower(), 0)

    return series.map(_map).astype(int)


def clean_historical_results(df: pd.DataFrame) -> pd.DataFrame:
    """Deep-clean a raw historical-results DataFrame.

    Expected raw columns:
        date, home_team, away_team, home_score, away_score,
        tournament, city, country, neutral

    Returns a cleaned copy (still in home/away schema) with valid dates,
    numeric non-negative scores, standardized team names, and no duplicates.
    """
    out = df.copy()

    if "date" in out.columns:
        out["date"] = pd.to_datetime(out["date"], errors="coerce")

    for col in ("home_score", "away_score"):
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    for col in ("home_team", "away_team"):
        if col in out.columns:
            out[col] = out[col].map(standardize_team_name)

    for col in ("tournament", "city", "country"):
        if col in out.columns:
            out[col] = out[col].astype("string").str.strip()

    if "neutral" in out.columns:
        out["neutral"] = _coerce_neutral(out["neutral"])

    out = out.dropna(
        subset=["date", "home_team", "away_team", "home_score", "away_score"]
    )
    out = out[(out["home_team"] != "") & (out["away_team"] != "")]
    out = out[out["home_team"] != out["away_team"]]
    out = out[(out["home_score"] >= 0) & (out["away_score"] >= 0)]

    out["home_score"] = out["home_score"].astype(int)
    out["away_score"] = out["away_score"].astype(int)

    out = out.drop_duplicates().reset_index(drop=True)
    return out


def clean_shootouts(df: pd.DataFrame) -> pd.DataFrame:
    """Clean a raw shootouts DataFrame into a standardized schema.

    Expected raw columns:
        date, home_team, away_team, winner

    Output columns:
        date, team_a, team_b, shootout_winner, shootout_loser
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=SHOOTOUT_OUTCOME_COLUMNS)

    out = df.copy().rename(
        columns={"home_team": "team_a", "away_team": "team_b"}
    )

    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out["team_a"] = out["team_a"].map(standardize_team_name)
    out["team_b"] = out["team_b"].map(standardize_team_name)
    out["shootout_winner"] = out["winner"].map(standardize_team_name)

    def _loser(row: pd.Series) -> str:
        winner = row["shootout_winner"]
        if winner == row["team_a"]:
            return row["team_b"]
        if winner == row["team_b"]:
            return row["team_a"]
        return ""

    out["shootout_loser"] = out.apply(_loser, axis=1)

    out = out[out["shootout_loser"] != ""]
    out = out.dropna(subset=["date"])
    out = (
        out[SHOOTOUT_OUTCOME_COLUMNS]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    return out


def _make_match_id(row: pd.Series) -> str:
    """Build a stable short match id from key fields."""
    date_str = ""
    if pd.notna(row.get("date")):
        date_str = pd.Timestamp(row["date"]).strftime("%Y-%m-%d")
    raw = "|".join(
        [
            date_str,
            str(row.get("team_a", "")),
            str(row.get("team_b", "")),
            str(row.get("tournament", "")),
        ]
    )
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]


def convert_historical_results_to_canonical(
    df: pd.DataFrame,
    shootouts_df: "pd.DataFrame | None" = None,
    data_source: str = "unknown",
) -> pd.DataFrame:
    """Convert raw historical results into the full canonical schema.

    Internally cleans the input via :func:`clean_historical_results`, renames
    to ``team_a``/``team_b``, derives result/winner/loser fields, and merges
    shootout outcomes when provided.

    Args:
        df: Raw (or cleaned) historical results in home/away schema.
        shootouts_df: Optional cleaned shootouts (from :func:`clean_shootouts`)
            or raw shootouts; raw will be cleaned automatically.
        data_source: Provenance label stored in the ``data_source`` column.

    Returns:
        DataFrame with :data:`CANONICAL_MATCH_COLUMNS`.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=CANONICAL_MATCH_COLUMNS)

    cleaned = clean_historical_results(df)
    if cleaned.empty:
        return pd.DataFrame(columns=CANONICAL_MATCH_COLUMNS)

    out = cleaned.rename(
        columns={
            "home_team": "team_a",
            "away_team": "team_b",
            "home_score": "team_a_score",
            "away_score": "team_b_score",
        }
    )

    for col in ("tournament", "city", "country", "neutral"):
        if col not in out.columns:
            out[col] = pd.NA
    out["neutral"] = (
        pd.to_numeric(out["neutral"], errors="coerce").fillna(0).astype(int)
    )

    out["year"] = out["date"].dt.year
    out["score_difference"] = out["team_a_score"] - out["team_b_score"]
    out["total_goals"] = out["team_a_score"] + out["team_b_score"]

    out = create_match_result_column(out)
    out["result_label"] = out["result"].map(RESULT_LABELS)
    out["is_draw"] = (out["result"] == 1).astype(int)

    out["winner"] = pd.NA
    out["loser"] = pd.NA
    win_a = out["result"] == 2
    win_b = out["result"] == 0
    out.loc[win_a, "winner"] = out.loc[win_a, "team_a"]
    out.loc[win_a, "loser"] = out.loc[win_a, "team_b"]
    out.loc[win_b, "winner"] = out.loc[win_b, "team_b"]
    out.loc[win_b, "loser"] = out.loc[win_b, "team_a"]

    out["match_id"] = out.apply(_make_match_id, axis=1)
    out["data_source"] = data_source

    # --- Shootout merge ----------------------------------------------------
    out["has_shootout"] = 0
    out["shootout_winner"] = pd.NA
    out["shootout_loser"] = pd.NA

    cleaned_shootouts = shootouts_df
    if cleaned_shootouts is not None and not cleaned_shootouts.empty:
        if "shootout_winner" not in cleaned_shootouts.columns:
            cleaned_shootouts = clean_shootouts(cleaned_shootouts)

    if cleaned_shootouts is not None and not cleaned_shootouts.empty:
        so = cleaned_shootouts.copy()
        so["date"] = pd.to_datetime(so["date"], errors="coerce")
        merged = out.merge(
            so[
                [
                    "date",
                    "team_a",
                    "team_b",
                    "shootout_winner",
                    "shootout_loser",
                ]
            ],
            on=["date", "team_a", "team_b"],
            how="left",
            suffixes=("", "_so"),
        )
        has = merged["shootout_winner_so"].notna()
        merged.loc[has, "has_shootout"] = 1
        merged.loc[has, "shootout_winner"] = merged.loc[has, "shootout_winner_so"]
        merged.loc[has, "shootout_loser"] = merged.loc[has, "shootout_loser_so"]
        merged = merged.drop(
            columns=["shootout_winner_so", "shootout_loser_so"]
        )
        out = merged

    # progression_winner: regular winner, or shootout winner for drawn matches.
    out["progression_winner"] = out["winner"]
    drawn = out["result"] == 1
    out.loc[drawn, "progression_winner"] = out.loc[drawn, "shootout_winner"]

    out = out.drop_duplicates(subset=["match_id"]).reset_index(drop=True)
    return out[CANONICAL_MATCH_COLUMNS]


# -----------------------------------------------------------------------------
# Step 3: team registry
# -----------------------------------------------------------------------------

def build_team_registry(canonical_df: pd.DataFrame) -> pd.DataFrame:
    """Build a unique team registry from canonical matches.

    Columns:
        team_id, team, team_slug, first_match_date, last_match_date,
        matches_played, is_world_cup_2026_host
    """
    if canonical_df is None or canonical_df.empty:
        return pd.DataFrame(columns=TEAM_REGISTRY_COLUMNS)

    df = canonical_df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    a = df[["team_a", "date"]].rename(columns={"team_a": "team"})
    b = df[["team_b", "date"]].rename(columns={"team_b": "team"})
    long = pd.concat([a, b], ignore_index=True)
    long = long[long["team"].astype(str).str.strip() != ""]

    grouped = (
        long.groupby("team")
        .agg(
            first_match_date=("date", "min"),
            last_match_date=("date", "max"),
            matches_played=("date", "count"),
        )
        .reset_index()
        .sort_values("team")
        .reset_index(drop=True)
    )

    grouped["team_slug"] = grouped["team"].map(slugify_team_name)
    hosts = {standardize_team_name(h) for h in WORLD_CUP_2026_HOSTS}
    grouped["is_world_cup_2026_host"] = grouped["team"].isin(hosts).astype(int)
    grouped.insert(0, "team_id", range(1, len(grouped) + 1))

    return grouped[TEAM_REGISTRY_COLUMNS]

