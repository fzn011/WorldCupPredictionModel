"""Standardization of national team names across data sources."""

from __future__ import annotations

import re
import unicodedata

# Canonical aliases. Keys are raw variants, values are the canonical name.
TEAM_NAME_MAPPING: dict[str, str] = {
    # United States
    "USA": "United States",
    "USMNT": "United States",
    "United States of America": "United States",
    "U.S.A.": "United States",
    # South Korea
    "Korea Republic": "South Korea",
    "Republic of Korea": "South Korea",
    "South Korea Republic": "South Korea",
    # Iran
    "IR Iran": "Iran",
    "Iran (Islamic Republic of)": "Iran",
    "Iran Islamic Republic": "Iran",
    # Turkey
    "Türkiye": "Turkey",
    "Turkey": "Turkey",
    # Czechia
    "Czech Republic": "Czechia",
    "Czechia": "Czechia",
    # Côte d'Ivoire
    "Ivory Coast": "Côte d'Ivoire",
    "Cote d'Ivoire": "Côte d'Ivoire",
    "Côte d Ivoire": "Côte d'Ivoire",
    # Russia
    "Russia": "Russia",
    "Russian Federation": "Russia",
    # Vietnam
    "Vietnam": "Vietnam",
    "Viet Nam": "Vietnam",
    # Cabo Verde
    "Cape Verde": "Cabo Verde",
    # North Macedonia
    "North Macedonia": "North Macedonia",
    "Macedonia": "North Macedonia",
    # China
    "China PR": "China",
    "People's Republic of China": "China",
    # Home nations (identity mappings to keep them explicit / stable)
    "England": "England",
    "Scotland": "Scotland",
    "Wales": "Wales",
    "Northern Ireland": "Northern Ireland",
}


def standardize_team_name(team_name: str) -> str:
    """Return a canonical team name.

    Handles ``None`` / NaN safely, strips and normalizes whitespace, then
    applies :data:`TEAM_NAME_MAPPING`. Falls back to the cleaned original.

    Args:
        team_name: Raw team name from a data source.

    Returns:
        Canonical name, or the cleaned original if no mapping exists.
        Empty / missing inputs return an empty string.
    """
    if team_name is None:
        return ""
    # Guard against float NaN without importing pandas here.
    if isinstance(team_name, float):
        return ""
    cleaned = str(team_name).strip()
    if not cleaned or cleaned.lower() == "nan":
        return ""
    # Collapse repeated internal whitespace.
    cleaned = re.sub(r"\s+", " ", cleaned)
    return TEAM_NAME_MAPPING.get(cleaned, cleaned)


def slugify_team_name(team_name: str) -> str:
    """Return a stable URL-safe slug for a team name.

    Standardizes the name, lowercases it, strips accents, removes
    punctuation (except hyphens) and converts spaces to hyphens.

    Examples:
        "United States"  -> "united-states"
        "Côte d'Ivoire"  -> "cote-divoire"
        "South Korea"    -> "south-korea"
    """
    name = standardize_team_name(team_name)
    if not name:
        return ""

    # Strip accents: decompose then drop combining marks.
    decomposed = unicodedata.normalize("NFKD", name)
    ascii_name = "".join(
        ch for ch in decomposed if not unicodedata.combining(ch)
    )

    ascii_name = ascii_name.lower()
    # Remove apostrophes/quotes so "d'ivoire" -> "divoire".
    ascii_name = ascii_name.replace("'", "").replace("\u2019", "")
    # Replace any run of non-alphanumeric chars with a single hyphen.
    ascii_name = re.sub(r"[^a-z0-9]+", "-", ascii_name)
    return ascii_name.strip("-")
