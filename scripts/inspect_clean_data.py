"""Inspect the Step 3 processed datasets and print a human-readable report.

Reads the canonical matches (real file preferred, sample fallback), the team
registry, and the shootout outcomes, then prints summary statistics. This is a
read-only inspection helper; it does not modify any data.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

# Make `src` importable when running this script directly.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.constants import (  # noqa: E402
    CANONICAL_MATCHES_FILE,
    CANONICAL_MATCHES_SAMPLE_FILE,
    PROCESSED_DATA_DIR,
    SHOOTOUT_OUTCOMES_FILE,
    TEAM_REGISTRY_FILE,
)


def _resolve_canonical_path() -> Path | None:
    """Return the real canonical file if present, else the sample, else None."""
    real_path = PROCESSED_DATA_DIR / CANONICAL_MATCHES_FILE
    sample_path = PROCESSED_DATA_DIR / CANONICAL_MATCHES_SAMPLE_FILE
    if real_path.is_file():
        return real_path
    if sample_path.is_file():
        return sample_path
    return None


def main() -> None:
    """Print an inspection report for the processed canonical datasets."""
    canonical_path = _resolve_canonical_path()
    if canonical_path is None:
        print(
            "No canonical matches file found. Run `python main.py` first to "
            "generate the Step 3 datasets."
        )
        return

    df = pd.read_csv(canonical_path, parse_dates=["date"])
    print("=" * 60)
    print(f"Canonical matches file: {canonical_path}")
    print("=" * 60)
    print(f"Rows:    {len(df):,}")
    print(f"Columns: {list(df.columns)}")

    if not df.empty:
        print(
            f"Date range: {df['date'].min().date()} -> {df['date'].max().date()}"
        )

    unique_teams = pd.unique(df[["team_a", "team_b"]].values.ravel("K"))
    print(f"Unique teams: {len(unique_teams)}")

    print("\nResult distribution (label -> count):")
    print(df["result_label"].value_counts().to_string())

    print("\nTop 10 tournaments:")
    print(df["tournament"].value_counts().head(10).to_string())

    print("\nTop 10 most-frequent teams:")
    team_counts = pd.Series(
        df[["team_a", "team_b"]].values.ravel("K")
    ).value_counts()
    print(team_counts.head(10).to_string())

    print(f"\nMatches decided/affected by a shootout: {int(df['has_shootout'].sum())}")

    print("\nMissing values per column:")
    print(df.isna().sum().to_string())

    # Team registry -------------------------------------------------------
    registry_path = PROCESSED_DATA_DIR / TEAM_REGISTRY_FILE
    if registry_path.is_file():
        registry = pd.read_csv(registry_path)
        print("\n" + "=" * 60)
        print(f"Team registry: {registry_path}")
        print("=" * 60)
        print(f"Teams: {len(registry)}")
        hosts = registry[registry["is_world_cup_2026_host"] == 1]["team"].tolist()
        print(f"WC2026 hosts present: {hosts}")

    # Shootout outcomes ---------------------------------------------------
    shootouts_path = PROCESSED_DATA_DIR / SHOOTOUT_OUTCOMES_FILE
    if shootouts_path.is_file():
        shootouts = pd.read_csv(shootouts_path)
        print("\n" + "=" * 60)
        print(f"Shootout outcomes: {shootouts_path}")
        print("=" * 60)
        print(f"Shootout records: {len(shootouts)}")


if __name__ == "__main__":
    main()
