"""Downloadable official import pack for Step 17E."""

from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import src.utils.constants as C
from src.official.staging_validation import load_staged_data


def _exports_dir() -> Path:
    p = C.PROJECT_ROOT / C.OFFICIAL_SOURCE_EXPORTS_DIR
    p.mkdir(parents=True, exist_ok=True)
    return p


def create_import_pack_zip(output_path: str | None = None) -> str:
    """Zip staged CSVs, templates, guides, and reports into import pack."""
    if output_path is None:
        output_path = str(_exports_dir() / C.OFFICIAL_DOWNLOADABLE_IMPORT_PACK_FILE)
    out = Path(output_path)
    if not out.is_absolute():
        out = C.PROJECT_ROOT / output_path
    out.parent.mkdir(parents=True, exist_ok=True)

    include_paths: list[Path] = []

    staging = C.PROJECT_ROOT / C.OFFICIAL_SOURCE_STAGING_DIR
    if staging.is_dir():
        include_paths.extend(staging.glob("*.csv"))

    templates = C.PROJECT_ROOT / C.OFFICIAL_IMPORT_TEMPLATES_DIR
    if templates.is_dir():
        include_paths.extend(templates.glob("*.csv"))

    for rel in [
        C.OFFICIAL_POPULATION_DIR + "/" + C.OFFICIAL_POPULATION_GUIDE_FILE,
        C.OFFICIAL_SOURCE_DATA_DIR + "/" + C.OFFICIAL_SOURCE_REGISTRY_FILE,
        C.OFFICIAL_SOURCE_REPORTS_DIR + "/" + C.OFFICIAL_SOURCE_PARSE_REPORT_FILE,
        C.OFFICIAL_SOURCE_REPORTS_DIR + "/" + C.OFFICIAL_STAGING_VALIDATION_REPORT_FILE,
        C.OFFICIAL_SOURCE_REPORTS_DIR + "/" + C.OFFICIAL_SOURCE_COVERAGE_REPORT_FILE,
        C.OFFICIAL_POPULATION_REPORTS_DIR + "/" + C.OFFICIAL_POPULATION_MISSING_DATA_REPORT_FILE,
    ]:
        p = C.PROJECT_ROOT / rel
        if p.is_file():
            include_paths.append(p)

    workbook = C.PROJECT_ROOT / C.OFFICIAL_POPULATION_WORKBOOK_DIR / C.OFFICIAL_MASTER_IMPORT_WORKBOOK_FILE
    if workbook.is_file():
        include_paths.append(workbook)

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in include_paths:
            if path.is_file():
                arcname = path.relative_to(C.PROJECT_ROOT)
                zf.write(path, arcname=str(arcname))

    return str(out)


def create_import_pack_summary() -> dict[str, Any]:
    """Return metadata about the latest import pack."""
    zip_path = _exports_dir() / C.OFFICIAL_DOWNLOADABLE_IMPORT_PACK_FILE
    files_included: list[str] = []
    if zip_path.is_file():
        with zipfile.ZipFile(zip_path, "r") as zf:
            files_included = zf.namelist()

    staged = load_staged_data()
    return {
        "status": "ready" if zip_path.is_file() else "not_created",
        "zip_path": str(zip_path) if zip_path.is_file() else "",
        "files_included": files_included,
        "staged_datasets": list(staged.keys()),
        "created_at": datetime.fromtimestamp(zip_path.stat().st_mtime, tz=timezone.utc).isoformat()
        if zip_path.is_file()
        else "",
    }
