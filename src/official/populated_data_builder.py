"""Build populated official import files from staged/source data (Step 17F)."""

from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

import src.utils.constants as C
from src.awards.player_priors import create_player_award_priors_template
from src.official.fifa_extractors import (
    extract_fixtures_from_fifa_schedule_snapshot,
    extract_players_from_fifa_squad_article_snapshot,
    extract_teams_from_fifa_snapshot,
    make_source_audit_row,
)
from src.official.source_parsers import teams_to_groups_df
from src.official.staging_validation import load_staged_data
from src.utils.team_name_mapping import standardize_team_name


def _populated_dir() -> Path:
    p = C.PROJECT_ROOT / C.OFFICIAL_POPULATED_DATA_DIR
    p.mkdir(parents=True, exist_ok=True)
    return p


def _reports_dir() -> Path:
    p = C.PROJECT_ROOT / C.OFFICIAL_POPULATED_REPORTS_DIR
    p.mkdir(parents=True, exist_ok=True)
    return p


def _exports_dir() -> Path:
    p = C.PROJECT_ROOT / C.OFFICIAL_POPULATED_EXPORTS_DIR
    p.mkdir(parents=True, exist_ok=True)
    return p


def _official_processed() -> Path:
    return C.PROJECT_ROOT / C.OFFICIAL_PROCESSED_DIR


def _read_csv_if_exists(path: Path) -> pd.DataFrame:
    if path.is_file():
        try:
            return pd.read_csv(path)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


def _is_verified_df(df: pd.DataFrame) -> bool:
    """Official rows usable for population unless marked sample_to_be_verified."""
    if df.empty or "source" not in df.columns:
        return False
    sources = df["source"].fillna("").astype(str).str.strip().str.lower()
    return not sources.eq("sample_to_be_verified").any()


def _dedupe_teams(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=C.IMPORT_TEAMS_REQUIRED_COLUMNS)
    out = df.copy()
    out["team"] = out["team"].astype(str).map(standardize_team_name)
    out = out[out["team"].fillna("").astype(str).str.strip().ne("")]
    out = out[out["team"].str.lower().ne("nan")]
    out = out.drop_duplicates(subset=["team"], keep="first")
    return out.reset_index(drop=True)


def _find_fifa_snapshot(name_hint: str) -> str | None:
    raw_dir = C.PROJECT_ROOT / C.OFFICIAL_SOURCE_RAW_DIR
    if not raw_dir.is_dir():
        return None
    for path in sorted(raw_dir.rglob("*.html"), reverse=True):
        if name_hint in path.name.lower():
            return str(path)
    for path in sorted(raw_dir.rglob("*.html"), reverse=True):
        return str(path)
    return None


def build_populated_teams_from_sources() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Merge teams from staged, FIFA snapshot, verified official, or filled template."""
    audits: list[dict] = []
    candidates: list[pd.DataFrame] = []

    staged = load_staged_data().get("teams", pd.DataFrame())
    if not staged.empty:
        candidates.append(staged)
        audits.append(make_source_audit_row("teams", "staged_official_teams", "parsed", len(staged)))

    snap = _find_fifa_snapshot("teams")
    if snap:
        parsed, snap_audit = extract_teams_from_fifa_snapshot(snap)
        if not parsed.empty:
            candidates.append(parsed)
        audits.extend(snap_audit.to_dict("records"))

    official = _read_csv_if_exists(_official_processed() / C.OFFICIAL_TEAMS_FILE)
    if _is_verified_df(official):
        imp = official.copy()
        for col in C.IMPORT_TEAMS_REQUIRED_COLUMNS:
            if col not in imp.columns:
                imp[col] = official.get(col, "")
        candidates.append(imp[C.IMPORT_TEAMS_REQUIRED_COLUMNS])
        audits.append(make_source_audit_row("teams", "official_teams_verified", "parsed", len(imp)))

    template = _read_csv_if_exists(
        C.PROJECT_ROOT / C.OFFICIAL_IMPORT_TEMPLATES_DIR / "official_teams_import_template.csv"
    )
    if not template.empty and _is_verified_df(template):
        candidates.append(template)
        audits.append(make_source_audit_row("teams", "manual_import_template", "parsed", len(template)))

    populated = _read_csv_if_exists(_populated_dir() / C.POPULATED_OFFICIAL_TEAMS_FILE)
    if not populated.empty:
        candidates.insert(0, populated)

    merged = pd.DataFrame(columns=C.IMPORT_TEAMS_REQUIRED_COLUMNS)
    for df in candidates:
        if df.empty:
            continue
        part = df.copy()
        for col in C.IMPORT_TEAMS_REQUIRED_COLUMNS:
            if col not in part.columns:
                part[col] = ""
        part = part[C.IMPORT_TEAMS_REQUIRED_COLUMNS]
        if merged.empty:
            merged = part
        else:
            merged = pd.concat([merged, part], ignore_index=True)
        merged = _dedupe_teams(merged)

    status = "parsed" if len(merged) >= C.OFFICIAL_REQUIRED_TEAM_COUNT else "partial"
    if not any(a.get("dataset") == "teams" for a in audits):
        audits.append(make_source_audit_row("teams", "build_populated_teams", status, len(merged)))
    return merged, pd.DataFrame(audits)


def build_populated_groups_from_sources(teams_df: pd.DataFrame | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build groups from staged, schedule, verified official, or teams."""
    audits: list[dict] = []
    candidates: list[pd.DataFrame] = []

    staged = load_staged_data().get("groups", pd.DataFrame())
    if not staged.empty:
        candidates.append(staged)
        audits.append(make_source_audit_row("groups", "staged_official_groups", "parsed", len(staged)))

    official = _read_csv_if_exists(_official_processed() / C.OFFICIAL_GROUPS_FILE)
    if _is_verified_df(official):
        imp = official.copy()
        for col in C.IMPORT_GROUPS_REQUIRED_COLUMNS:
            if col not in imp.columns:
                imp[col] = ""
        candidates.append(imp[C.IMPORT_GROUPS_REQUIRED_COLUMNS])
        audits.append(make_source_audit_row("groups", "official_groups_verified", "parsed", len(imp)))

    populated = _read_csv_if_exists(_populated_dir() / C.POPULATED_OFFICIAL_GROUPS_FILE)
    if not populated.empty:
        candidates.insert(0, populated)

    if teams_df is None or teams_df.empty:
        teams_df, _ = build_populated_teams_from_sources()
    if not teams_df.empty:
        derived = teams_to_groups_df(teams_df)
        if not derived.empty:
            candidates.append(derived)

    merged = pd.DataFrame(columns=C.IMPORT_GROUPS_REQUIRED_COLUMNS)
    for df in candidates:
        if df.empty:
            continue
        part = df.copy()
        for col in C.IMPORT_GROUPS_REQUIRED_COLUMNS:
            if col not in part.columns:
                part[col] = ""
        part = part[C.IMPORT_GROUPS_REQUIRED_COLUMNS]
        merged = pd.concat([merged, part], ignore_index=True) if not merged.empty else part
        merged = merged.drop_duplicates(subset=["group", "slot", "team"], keep="first")

    status = "parsed" if len(merged) >= C.OFFICIAL_REQUIRED_TEAM_COUNT else "partial"
    audits.append(make_source_audit_row("groups", "build_populated_groups", status, len(merged)))
    return merged, pd.DataFrame(audits)


def build_populated_fixtures_and_venues_from_sources() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Build fixtures and venues from staged, schedule import, snapshot, or official."""
    audits: list[dict] = []
    fixtures_candidates: list[pd.DataFrame] = []
    venues_candidates: list[pd.DataFrame] = []

    populated_f = _read_csv_if_exists(_populated_dir() / C.POPULATED_OFFICIAL_FIXTURES_FILE)
    populated_v = _read_csv_if_exists(_populated_dir() / C.POPULATED_OFFICIAL_VENUES_FILE)
    if not populated_f.empty:
        fixtures_candidates.append(populated_f)
    if not populated_v.empty:
        venues_candidates.append(populated_v)

    staged = load_staged_data()
    if not staged.get("fixtures", pd.DataFrame()).empty:
        fixtures_candidates.append(staged["fixtures"])
        audits.append(
            make_source_audit_row("fixtures", "staged_official_fixtures", "parsed", len(staged["fixtures"]))
        )
    if not staged.get("venues", pd.DataFrame()).empty:
        venues_candidates.append(staged["venues"])
        audits.append(make_source_audit_row("venues", "staged_official_venues", "parsed", len(staged["venues"])))

    snap = _find_fifa_snapshot("schedule") or _find_fifa_snapshot("scores")
    if snap:
        fdf, vdf, snap_audit = extract_fixtures_from_fifa_schedule_snapshot(snap)
        if not fdf.empty:
            fixtures_candidates.append(fdf)
        if not vdf.empty:
            venues_candidates.append(vdf)
        audits.extend(snap_audit.to_dict("records"))

    for target, file_key, cols in (
        (fixtures_candidates, C.OFFICIAL_FIXTURES_FILE, C.IMPORT_FIXTURES_REQUIRED_COLUMNS),
        (venues_candidates, C.OFFICIAL_VENUES_FILE, C.IMPORT_VENUES_REQUIRED_COLUMNS),
    ):
        official = _read_csv_if_exists(_official_processed() / file_key)
        if _is_verified_df(official):
            imp = official.copy()
            for col in cols:
                if col not in imp.columns:
                    imp[col] = ""
            target.append(imp[cols])

    def _merge_frames(candidates: list[pd.DataFrame], cols: list[str], key: str) -> pd.DataFrame:
        merged = pd.DataFrame(columns=cols)
        for df in candidates:
            if df.empty:
                continue
            part = df.copy()
            for col in cols:
                if col not in part.columns:
                    part[col] = ""
            part = part[cols]
            merged = pd.concat([merged, part], ignore_index=True) if not merged.empty else part
            merged = merged.drop_duplicates(subset=[key], keep="first")
        return merged

    fixtures_df = _merge_frames(fixtures_candidates, C.IMPORT_FIXTURES_REQUIRED_COLUMNS, "match_id")
    venues_df = _merge_frames(venues_candidates, C.IMPORT_VENUES_REQUIRED_COLUMNS, "venue_id")

    status = "parsed" if len(fixtures_df) >= C.OFFICIAL_TOTAL_MATCHES else "partial"
    audits.append(make_source_audit_row("fixtures", "build_populated_fixtures", status, len(fixtures_df)))
    audits.append(make_source_audit_row("venues", "build_populated_venues", "partial", len(venues_df)))
    return fixtures_df, venues_df, pd.DataFrame(audits)


def build_populated_players_from_sources() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build players from staged, squad import, squad articles, or verified official."""
    audits: list[dict] = []
    candidates: list[pd.DataFrame] = []

    populated = _read_csv_if_exists(_populated_dir() / C.POPULATED_OFFICIAL_PLAYERS_FILE)
    if not populated.empty:
        candidates.append(populated)

    staged = load_staged_data().get("players", pd.DataFrame())
    if not staged.empty:
        candidates.append(staged)
        audits.append(make_source_audit_row("players", "staged_official_players", "parsed", len(staged)))

    official = _read_csv_if_exists(_official_processed() / C.OFFICIAL_PLAYERS_FILE)
    if _is_verified_df(official):
        imp = official.copy()
        for col in C.IMPORT_PLAYERS_REQUIRED_COLUMNS:
            if col not in imp.columns:
                imp[col] = ""
        candidates.append(imp[C.IMPORT_PLAYERS_REQUIRED_COLUMNS])
        audits.append(make_source_audit_row("players", "official_players_verified", "parsed", len(imp)))

    raw_dir = C.PROJECT_ROOT / C.OFFICIAL_SOURCE_RAW_DIR
    if raw_dir.is_dir():
        for path in raw_dir.rglob("*squad*.html"):
            team = path.stem.replace("_", " ").replace("-", " ")
            pdf, part_audit = extract_players_from_fifa_squad_article_snapshot(str(path), team)
            if not pdf.empty:
                candidates.append(pdf)
            audits.extend(part_audit.to_dict("records"))

    merged = pd.DataFrame(columns=C.IMPORT_PLAYERS_REQUIRED_COLUMNS)
    for df in candidates:
        if df.empty:
            continue
        part = df.copy()
        for col in C.IMPORT_PLAYERS_REQUIRED_COLUMNS:
            if col not in part.columns:
                part[col] = ""
        part = part[C.IMPORT_PLAYERS_REQUIRED_COLUMNS]
        merged = pd.concat([merged, part], ignore_index=True) if not merged.empty else part
        if "player_id" in merged.columns and merged["player_id"].notna().any():
            merged = merged.drop_duplicates(subset=["player_id"], keep="first")
        else:
            merged = merged.drop_duplicates(subset=["team", "player_name"], keep="first")

    status = "parsed" if len(merged) >= C.OFFICIAL_REQUIRED_TOTAL_PLAYERS else "partial"
    audits.append(make_source_audit_row("players", "build_populated_players", status, len(merged)))
    return merged, pd.DataFrame(audits)


def build_populated_player_priors(players_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Merge existing priors for official players; add conservative defaults for gaps."""
    if players_df.empty:
        empty = pd.DataFrame(columns=C.PLAYER_PRIOR_REQUIRED_COLUMNS)
        return empty, pd.DataFrame(columns=["player", "team", "reason"])

    official_keys = set(
        zip(
            players_df["player_name"].astype(str).str.strip(),
            players_df["team"].astype(str).str.strip(),
        )
    )

    priors_path = C.PROJECT_ROOT / C.PROCESSED_DATA_DIR / C.PLAYER_AWARD_PRIORS_FILE
    sample_path = C.PROJECT_ROOT / C.SAMPLE_DATA_DIR / C.SAMPLE_PLAYER_AWARD_PRIORS_FILE
    existing = _read_csv_if_exists(priors_path)
    if existing.empty:
        existing = _read_csv_if_exists(sample_path)

    matched_rows: list[dict] = []
    unmatched_rows: list[dict] = []

    if not existing.empty and {"player", "team"}.issubset(existing.columns):
        for _, row in existing.iterrows():
            key = (str(row["player"]).strip(), str(row["team"]).strip())
            if key in official_keys:
                matched_rows.append(row.to_dict())
            else:
                unmatched_rows.append({"player": row["player"], "team": row["team"], "reason": "non_official_player"})

    matched_df = pd.DataFrame(matched_rows) if matched_rows else pd.DataFrame(columns=C.PLAYER_PRIOR_REQUIRED_COLUMNS)
    if not matched_df.empty:
        matched_df = matched_df[C.PLAYER_PRIOR_REQUIRED_COLUMNS]

    covered = set(
        zip(matched_df["player"].astype(str), matched_df["team"].astype(str))
    ) if not matched_df.empty else set()

    missing_players = players_df[
        ~players_df.apply(
            lambda r: (str(r["player_name"]).strip(), str(r["team"]).strip()) in covered,
            axis=1,
        )
    ]
    if not missing_players.empty:
        defaults = create_player_award_priors_template(missing_players)
        matched_df = pd.concat([matched_df, defaults], ignore_index=True)

    unmatched_report = pd.DataFrame(unmatched_rows)
    audit = pd.DataFrame(
        [
            make_source_audit_row(
                "player_priors",
                "build_populated_player_priors",
                "parsed" if len(matched_df) >= len(players_df) else "partial",
                len(matched_df),
                notes=f"Excluded {len(unmatched_rows)} non-official priors",
            )
        ]
    )
    if not matched_df.empty:
        matched_df = matched_df[C.PLAYER_PRIOR_REQUIRED_COLUMNS]
    return matched_df, unmatched_report


def _append_audit(audit_df: pd.DataFrame) -> None:
    path = _reports_dir() / C.OFFICIAL_POPULATION_SOURCE_AUDIT_FILE
    if path.is_file() and not audit_df.empty:
        audit_df = pd.concat([pd.read_csv(path), audit_df], ignore_index=True)
    if not audit_df.empty:
        audit_df.to_csv(path, index=False)


def _save_populated_csv(df: pd.DataFrame, filename: str) -> str:
    path = _populated_dir() / filename
    df.to_csv(path, index=False)
    return str(path)


def create_official_ready_import_pack() -> str:
    """Zip populated CSVs and reports into official-ready import pack."""
    out = _exports_dir() / C.OFFICIAL_READY_IMPORT_PACK_FILE
    include = [
        _populated_dir() / C.POPULATED_OFFICIAL_TEAMS_FILE,
        _populated_dir() / C.POPULATED_OFFICIAL_GROUPS_FILE,
        _populated_dir() / C.POPULATED_OFFICIAL_FIXTURES_FILE,
        _populated_dir() / C.POPULATED_OFFICIAL_VENUES_FILE,
        _populated_dir() / C.POPULATED_OFFICIAL_PLAYERS_FILE,
        _populated_dir() / C.POPULATED_PLAYER_AWARD_PRIORS_FILE,
        _reports_dir() / C.OFFICIAL_POPULATION_COMPLETENESS_REPORT_FILE,
        _reports_dir() / C.OFFICIAL_POPULATION_SOURCE_AUDIT_FILE,
    ]
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in include:
            if path.is_file():
                zf.write(path, arcname=str(path.relative_to(C.PROJECT_ROOT)))
    return str(out)


def build_all_populated_official_data() -> dict[str, Any]:
    """Build and save all populated outputs."""
    teams_df, teams_audit = build_populated_teams_from_sources()
    groups_df, groups_audit = build_populated_groups_from_sources(teams_df)
    fixtures_df, venues_df, fv_audit = build_populated_fixtures_and_venues_from_sources()
    players_df, players_audit = build_populated_players_from_sources()
    priors_df, _unmatched = build_populated_player_priors(players_df)

    paths = {
        "teams": _save_populated_csv(teams_df, C.POPULATED_OFFICIAL_TEAMS_FILE),
        "groups": _save_populated_csv(groups_df, C.POPULATED_OFFICIAL_GROUPS_FILE),
        "fixtures": _save_populated_csv(fixtures_df, C.POPULATED_OFFICIAL_FIXTURES_FILE),
        "venues": _save_populated_csv(venues_df, C.POPULATED_OFFICIAL_VENUES_FILE),
        "players": _save_populated_csv(players_df, C.POPULATED_OFFICIAL_PLAYERS_FILE),
        "player_priors": _save_populated_csv(priors_df, C.POPULATED_PLAYER_AWARD_PRIORS_FILE),
    }

    audit = pd.concat(
        [teams_audit, groups_audit, fv_audit, players_audit],
        ignore_index=True,
    )
    _append_audit(audit)

    manifest_path = _official_processed() / C.OFFICIAL_SOURCE_MANIFEST_FILE
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            manifest = {}
    else:
        manifest = {}
    manifest["step17f_populated_at"] = datetime.now(timezone.utc).isoformat()
    manifest["population_sources"] = C.OFFICIAL_SOURCE_PRIORITY
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return {
        "paths": paths,
        "teams_count": len(teams_df),
        "groups_count": groups_df["group"].nunique() if not groups_df.empty and "group" in groups_df.columns else 0,
        "fixtures_count": len(fixtures_df),
        "venues_count": len(venues_df),
        "players_count": len(players_df),
        "audit_path": str(_reports_dir() / C.OFFICIAL_POPULATION_SOURCE_AUDIT_FILE),
    }
