"""Official FIFA source registry for Step 17E source-assisted population."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import src.utils.constants as C


def _registry_path() -> Path:
    base = C.PROJECT_ROOT / C.OFFICIAL_SOURCE_DATA_DIR
    base.mkdir(parents=True, exist_ok=True)
    return base / C.OFFICIAL_SOURCE_REGISTRY_FILE


def create_default_official_source_registry() -> dict:
    """Return default registry with FIFA source URLs and metadata."""
    now = datetime.now(timezone.utc).isoformat()
    sources = {}
    for name, url in C.OFFICIAL_FIFA_SOURCE_URLS.items():
        sources[name] = {
            "url": url,
            "allowed_domain": urlparse(url).netloc.replace("www.", ""),
            "source_status": "not_started",
            "last_checked_at": "",
            "notes": "Official FIFA source — manual verification required after staging.",
        }
    return {
        "version": "17e",
        "created_at": now,
        "updated_at": now,
        "allowed_domains": list(C.OFFICIAL_SOURCE_ALLOWED_DOMAINS),
        "policy": (
            "Official FIFA sources first; manual templates always available; "
            "no whole-internet scraping."
        ),
        "sources": sources,
    }


def save_official_source_registry(registry: dict, output_path: str | None = None) -> str:
    """Save registry JSON to source_data directory."""
    registry = dict(registry)
    registry["updated_at"] = datetime.now(timezone.utc).isoformat()
    out = Path(output_path) if output_path else _registry_path()
    if not out.is_absolute():
        out = C.PROJECT_ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    return str(out)


def load_official_source_registry(path: str | None = None) -> dict:
    """Load registry or create default if missing."""
    reg_path = Path(path) if path else _registry_path()
    if not reg_path.is_absolute():
        reg_path = C.PROJECT_ROOT / reg_path
    if reg_path.is_file():
        return json.loads(reg_path.read_text(encoding="utf-8"))
    registry = create_default_official_source_registry()
    save_official_source_registry(registry, str(reg_path))
    return registry


def validate_source_url(url: str) -> bool:
    """Return True only if URL domain is in OFFICIAL_SOURCE_ALLOWED_DOMAINS."""
    if not url or not isinstance(url, str):
        return False
    host = urlparse(url.strip()).netloc.lower().replace("www.", "")
    if not host:
        return False
    for domain in C.OFFICIAL_SOURCE_ALLOWED_DOMAINS:
        d = domain.lower().replace("www.", "")
        if host == d or host.endswith("." + d):
            return True
    return False


def update_source_status(source_name: str, status: str, notes: str = "") -> dict:
    """Update a source entry status in the registry and save."""
    registry = load_official_source_registry()
    sources = registry.setdefault("sources", {})
    if source_name not in sources and source_name in C.OFFICIAL_FIFA_SOURCE_URLS:
        sources[source_name] = {
            "url": C.OFFICIAL_FIFA_SOURCE_URLS[source_name],
            "source_status": status,
            "last_checked_at": datetime.now(timezone.utc).isoformat(),
            "notes": notes,
        }
    elif source_name in sources:
        sources[source_name]["source_status"] = status
        sources[source_name]["last_checked_at"] = datetime.now(timezone.utc).isoformat()
        if notes:
            sources[source_name]["notes"] = notes
    else:
        sources[source_name] = {
            "url": "",
            "source_status": status,
            "last_checked_at": datetime.now(timezone.utc).isoformat(),
            "notes": notes or f"Unknown source: {source_name}",
        }
    save_official_source_registry(registry)
    return registry
