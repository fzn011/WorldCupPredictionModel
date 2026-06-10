"""Safe official FIFA source downloader for Step 17E."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import src.utils.constants as C
from src.official.source_registry import (
    load_official_source_registry,
    save_official_source_registry,
    update_source_status,
    validate_source_url,
)

DEFAULT_USER_AGENT = (
    "WorldCup2026AIPredictor/17E (+https://github.com/fzn011/WorldCupPredictionModel; "
    "official-source-audit-only)"
)
DOWNLOAD_TIMEOUT_SECONDS = 30


def _raw_dir() -> Path:
    return C.PROJECT_ROOT / C.OFFICIAL_SOURCE_RAW_DIR


def ensure_source_dirs() -> dict[str, str]:
    """Create source_data folder tree."""
    paths = {
        "source_data": C.PROJECT_ROOT / C.OFFICIAL_SOURCE_DATA_DIR,
        "raw": _raw_dir(),
        "staging": C.PROJECT_ROOT / C.OFFICIAL_SOURCE_STAGING_DIR,
        "reports": C.PROJECT_ROOT / C.OFFICIAL_SOURCE_REPORTS_DIR,
        "exports": C.PROJECT_ROOT / C.OFFICIAL_SOURCE_EXPORTS_DIR,
    }
    for p in paths.values():
        p.mkdir(parents=True, exist_ok=True)
    return {k: str(v) for k, v in paths.items()}


def _fetch_url(url: str) -> tuple[int, bytes, str | None]:
    """Fetch URL content; returns (status_code, content, error_message)."""
    try:
        import requests

        response = requests.get(
            url,
            timeout=DOWNLOAD_TIMEOUT_SECONDS,
            headers={"User-Agent": DEFAULT_USER_AGENT},
        )
        return response.status_code, response.content, None
    except ImportError:
        pass
    except Exception as exc:
        return 0, b"", str(exc)

    try:
        from urllib.error import HTTPError, URLError
        from urllib.request import Request, urlopen

        req = Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
        with urlopen(req, timeout=DOWNLOAD_TIMEOUT_SECONDS) as resp:
            content = resp.read()
            return getattr(resp, "status", 200), content, None
    except HTTPError as exc:
        return exc.code, b"", str(exc)
    except URLError as exc:
        return 0, b"", str(exc)
    except Exception as exc:
        return 0, b"", str(exc)


def download_official_source(
    source_name: str,
    url: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Download one official source snapshot to raw HTML file."""
    ensure_source_dirs()
    registry = load_official_source_registry()
    source_url = url or C.OFFICIAL_FIFA_SOURCE_URLS.get(source_name, "")
    if not source_url:
        source_url = registry.get("sources", {}).get(source_name, {}).get("url", "")

    result: dict[str, Any] = {
        "source_name": source_name,
        "url": source_url,
        "downloaded_at": "",
        "status_code": 0,
        "content_length": 0,
        "output_path": "",
        "success": False,
        "error_message": "",
        "skipped": False,
    }

    if not validate_source_url(source_url):
        result["error_message"] = f"URL domain not allowed for official sources: {source_url}"
        update_source_status(source_name, "failed", result["error_message"])
        return result

    output_path = _raw_dir() / f"{source_name}.html"
    if output_path.is_file() and not force:
        result["skipped"] = True
        result["success"] = True
        result["output_path"] = str(output_path)
        result["content_length"] = output_path.stat().st_size
        result["downloaded_at"] = datetime.fromtimestamp(
            output_path.stat().st_mtime, tz=timezone.utc
        ).isoformat()
        update_source_status(source_name, "source_downloaded", "Used existing snapshot (not forced).")
        return result

    status_code, content, error = _fetch_url(source_url)
    result["status_code"] = status_code
    result["downloaded_at"] = datetime.now(timezone.utc).isoformat()

    if error:
        result["error_message"] = error
        update_source_status(source_name, "failed", error)
        return result

    if status_code < 200 or status_code >= 400:
        result["error_message"] = f"HTTP {status_code} for {source_url}"
        update_source_status(source_name, "failed", result["error_message"])
        return result

    output_path.write_bytes(content)
    result["output_path"] = str(output_path)
    result["content_length"] = len(content)
    result["success"] = True
    update_source_status(source_name, "source_downloaded", "Snapshot saved for audit/review.")
    return result


def download_all_official_sources(force: bool = False) -> dict[str, Any]:
    """Download all configured FIFA source snapshots."""
    results = {}
    for name in C.OFFICIAL_FIFA_SOURCE_URLS:
        results[name] = download_official_source(name, force=force)
    manifest_path = save_snapshot_manifest(results)
    return {"results": results, "manifest_path": manifest_path}


def save_snapshot_manifest(download_results: dict[str, Any]) -> str:
    """Save download manifest JSON."""
    ensure_source_dirs()
    path = C.PROJECT_ROOT / C.OFFICIAL_SOURCE_DATA_DIR / C.OFFICIAL_SOURCE_SNAPSHOT_MANIFEST_FILE
    payload = {
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "downloads": download_results,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return str(path)
