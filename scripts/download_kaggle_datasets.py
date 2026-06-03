"""Optional Kaggle dataset downloader.

Downloads the historical international football results dataset from Kaggle
into ``data/raw/matches/`` when Kaggle credentials are available.

Authentication is **never** hardcoded. The Kaggle Python client auto-loads
credentials from one of:

* ``~/.kaggle/kaggle.json`` (Windows: ``%USERPROFILE%\\.kaggle\\kaggle.json``)
* environment variables ``KAGGLE_USERNAME`` / ``KAGGLE_KEY``

If credentials or the ``kaggle`` package are missing, the script exits with
code 1 and prints clear setup instructions. The project still works via the
sample fallback under ``data/sample/``.

Usage::

    python scripts/download_kaggle_datasets.py
"""

from __future__ import annotations

import os
import shutil
import sys
import zipfile
from pathlib import Path

# Make `src` importable when running this script directly.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.constants import RAW_MATCHES_DIR  # noqa: E402

DATASET_SLUG = "martj42/international-football-results-from-1872-to-2017"
EXPECTED_FILES = ("results.csv", "shootouts.csv")


def _kaggle_credentials_available() -> bool:
    """Return True if Kaggle credentials look configured.

    Checks both standard locations without reading or printing any secret.
    """
    if os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY"):
        return True
    default_path = Path.home() / ".kaggle" / "kaggle.json"
    return default_path.is_file()


def _print_setup_instructions() -> None:
    print(
        "\nKaggle credentials were not found. To enable automatic download:\n"
        "  1. Sign in at https://www.kaggle.com and open Settings -> API.\n"
        "  2. Click 'Create New API Token' to download kaggle.json.\n"
        "  3. Place it at:\n"
        "       Windows:  %USERPROFILE%\\.kaggle\\kaggle.json\n"
        "       macOS/Linux: ~/.kaggle/kaggle.json\n"
        "     OR set environment variables KAGGLE_USERNAME and KAGGLE_KEY.\n"
        "  4. Do NOT place kaggle.json inside this project folder.\n"
        "\n"
        "Until credentials are configured, the project will keep using\n"
        "sample fallback data under data/sample/."
    )


def _unzip_if_needed(target_dir: Path) -> None:
    for zip_path in target_dir.glob("*.zip"):
        try:
            with zipfile.ZipFile(zip_path) as zf:
                zf.extractall(target_dir)
            zip_path.unlink()
            print(f"Unzipped and removed: {zip_path.name}")
        except zipfile.BadZipFile:
            print(f"Skipping bad zip: {zip_path.name}")


def main() -> int:
    """Download the Kaggle dataset into ``data/raw/matches/``."""
    try:
        # Imported lazily so the script can give a clean message if missing.
        from kaggle.api.kaggle_api_extended import KaggleApi
    except Exception:
        print(
            "The 'kaggle' Python package is not installed.\n"
            "Install it with:  pip install kaggle"
        )
        return 1

    if not _kaggle_credentials_available():
        print("Kaggle credentials not detected.")
        _print_setup_instructions()
        return 1

    RAW_MATCHES_DIR.mkdir(parents=True, exist_ok=True)

    try:
        api = KaggleApi()
        api.authenticate()
    except Exception as exc:
        # Intentionally do not print the exception payload \u2014 it can include
        # tokens in some failure modes.
        print(f"Kaggle authentication failed: {type(exc).__name__}")
        _print_setup_instructions()
        return 1

    print(f"Downloading dataset '{DATASET_SLUG}' -> {RAW_MATCHES_DIR}")
    try:
        api.dataset_download_files(
            DATASET_SLUG,
            path=str(RAW_MATCHES_DIR),
            unzip=True,
            quiet=False,
        )
    except Exception as exc:
        print(f"Kaggle download failed: {type(exc).__name__}: {exc}")
        return 1

    # Some Kaggle client versions leave a .zip even when unzip=True.
    _unzip_if_needed(RAW_MATCHES_DIR)

    found = [f for f in EXPECTED_FILES if (RAW_MATCHES_DIR / f).is_file()]
    missing = [f for f in EXPECTED_FILES if f not in found]

    print("\nDownload complete.")
    if found:
        print(f"  Found:   {found}")
    if missing:
        print(f"  Missing: {missing} (dataset structure may have changed)")

    # Best-effort cleanup of stray zips.
    for zip_path in RAW_MATCHES_DIR.glob("*.zip"):
        try:
            zip_path.unlink()
        except OSError:
            pass

    return 0 if (RAW_MATCHES_DIR / "results.csv").is_file() else 1


if __name__ == "__main__":
    raise SystemExit(main())
