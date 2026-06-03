"""Data loading utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Union

import pandas as pd

from src.data.data_sources import DATA_SOURCES


def load_csv(file_path: Union[str, Path]) -> pd.DataFrame:
    """Load a CSV file into a pandas DataFrame.

    Args:
        file_path: Path to a CSV file.

    Returns:
        The loaded DataFrame.

    Raises:
        FileNotFoundError: If ``file_path`` does not exist.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(
            f"CSV file not found: {path}. "
            "Place the file at this location or update the path in config.yaml."
        )
    return pd.read_csv(path)


def load_sample_matches() -> pd.DataFrame:
    """Return a small in-memory sample of international match results.

    Kept for backward compatibility with Step 1. Returns the canonical
    ``team_a / team_b / team_a_score / team_b_score`` schema directly.
    """
    sample = [
        ("2022-12-18", "Argentina",   "France",      3, 3, "FIFA World Cup",      True),
        ("2022-12-14", "France",      "Morocco",     2, 0, "FIFA World Cup",      True),
        ("2022-12-13", "Argentina",   "Croatia",     3, 0, "FIFA World Cup",      True),
        ("2024-07-14", "Spain",       "England",     2, 1, "UEFA Euro",           True),
        ("2024-06-15", "Germany",     "Scotland",    5, 1, "UEFA Euro",           False),
        ("2024-03-26", "Brazil",      "Spain",       3, 3, "Friendly",            True),
        ("2023-09-12", "Portugal",    "Luxembourg",  9, 0, "Euro Qualifiers",     False),
        ("2023-10-13", "Netherlands", "France",      1, 2, "Euro Qualifiers",     False),
    ]
    columns = [
        "date",
        "team_a",
        "team_b",
        "team_a_score",
        "team_b_score",
        "tournament",
        "neutral",
    ]
    return pd.DataFrame(sample, columns=columns)


def load_dataset_with_fallback(source_key: str) -> pd.DataFrame:
    """Load a registered dataset, falling back to its sample copy if needed.

    Looks up ``source_key`` in :data:`DATA_SOURCES`. If the real expected
    file exists on disk it is loaded; otherwise the bundled sample CSV is
    loaded and a notice is printed.
    """
    if source_key not in DATA_SOURCES:
        raise KeyError(
            f"Unknown data source '{source_key}'. "
            f"Known sources: {sorted(DATA_SOURCES)}"
        )

    cfg = DATA_SOURCES[source_key]
    if cfg.expected_path.is_file():
        print(f"[load] {cfg.name}: real file -> {cfg.expected_path}")
        return pd.read_csv(cfg.expected_path)

    if not cfg.sample_path.is_file():
        raise FileNotFoundError(
            f"Neither real file ({cfg.expected_path}) nor sample file "
            f"({cfg.sample_path}) exists for '{source_key}'."
        )

    print(
        f"[load] {cfg.name}: real file missing, using sample -> {cfg.sample_path}"
    )
    return pd.read_csv(cfg.sample_path)


def load_historical_results() -> pd.DataFrame:
    """Load historical international match results (real or sample)."""
    return load_dataset_with_fallback("historical_results")


def load_fifa_rankings() -> pd.DataFrame:
    """Load FIFA rankings snapshot (real or sample)."""
    return load_dataset_with_fallback("fifa_rankings")


def load_elo_ratings() -> pd.DataFrame:
    """Load Elo ratings snapshot (real or sample)."""
    return load_dataset_with_fallback("elo_ratings")


def load_wc2026_teams() -> pd.DataFrame:
    """Load FIFA World Cup 2026 qualified teams (real or sample)."""
    return load_dataset_with_fallback("wc2026_teams")


def load_wc2026_groups() -> pd.DataFrame:
    """Load FIFA World Cup 2026 group draw (real or sample)."""
    return load_dataset_with_fallback("wc2026_groups")


def load_wc2026_schedule() -> pd.DataFrame:
    """Load FIFA World Cup 2026 match schedule (real or sample)."""
    return load_dataset_with_fallback("wc2026_schedule")


def real_file_exists(source_key: str) -> bool:
    """Return True if the real expected file for ``source_key`` exists."""
    return DATA_SOURCES[source_key].expected_path.is_file()


def dataset_uses_real_file(source_key: str) -> bool:
    """Return True if the registered real file for ``source_key`` exists.

    Thin alias over :func:`real_file_exists` with a more descriptive name
    used by the Step 3 cleaning pipeline.
    """
    return real_file_exists(source_key)


def load_shootouts() -> pd.DataFrame:
    """Load the raw shootouts dataset if present.

    Looks for ``data/raw/matches/shootouts.csv``. If it is missing, returns
    an empty DataFrame with the expected raw columns instead of failing.
    """
    from src.utils.constants import RAW_MATCHES_DIR, SHOOTOUTS_FILE

    expected_columns = ["date", "home_team", "away_team", "winner"]
    path = RAW_MATCHES_DIR / SHOOTOUTS_FILE
    if path.is_file():
        print(f"[load] Shootouts: real file -> {path}")
        return pd.read_csv(path)

    print(
        f"[load] Shootouts: file missing ({path}); "
        "continuing without shootout data."
    )
    return pd.DataFrame(columns=expected_columns)
