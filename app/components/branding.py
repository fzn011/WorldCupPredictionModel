"""App branding — World Cup 2026 logo and sidebar header."""

from __future__ import annotations

import base64
import html
from pathlib import Path

import streamlit as st

_APP_DIR = Path(__file__).resolve().parents[1]
_IMAGES_DIR = _APP_DIR / "static" / "images"

# Standard repo path (copy your Downloads PNG here as world_cup_logo.png)
LOGO_STANDARD = _IMAGES_DIR / "world_cup_logo.png"
# Original filename from user download (optional copy)
LOGO_ALT_NAME = _IMAGES_DIR / "hd-official-2026-fifa-world-cup-transparent-png.png"


def resolve_logo_path() -> Path | None:
    """Return first existing logo file."""
    for path in (LOGO_STANDARD, LOGO_ALT_NAME):
        if path.is_file():
            return path
    for path in sorted(_IMAGES_DIR.glob("*.png")):
        if path.is_file():
            return path
    return None


def logo_data_uri() -> str | None:
    """Base64 data URI for embedding logo in HTML (works on all hosts)."""
    path = resolve_logo_path()
    if not path:
        return None
    suffix = path.suffix.lower()
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(
        suffix, "image/png"
    )
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def render_sidebar_brand(*, tagline: str = "AI Predictor · Analytics") -> None:
    """Logo + title block at top of sidebar (upper-left branding)."""
    path = resolve_logo_path()
    data_uri = logo_data_uri()
    logo_html = (
        f'<img class="wc-sidebar-logo" src="{data_uri}" alt="FIFA World Cup 2026" />'
        if data_uri
        else '<div class="wc-sidebar-logo-fallback">WC<br>2026</div>'
    )
    st.markdown(
        f"""
<div class="wc-sidebar-brand">
  {logo_html}
  <div class="wc-sidebar-brand-text">
    <div class="wc-sidebar-brand-title">World Cup 2026</div>
    <div class="wc-sidebar-brand-sub">{html.escape(tagline)}</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )
    if path is None:
        st.caption("Add logo: app/static/images/world_cup_logo.png")


def render_branded_hero(
    title: str,
    subtitle: str,
    *,
    eyebrow: str = "Command Center",
) -> None:
    """Main page hero with logo on the left."""
    data_uri = logo_data_uri()
    logo_block = (
        f'<img class="wc-hero-logo" src="{data_uri}" alt="FIFA World Cup 2026" />'
        if data_uri
        else '<div class="wc-hero-logo-fallback">2026</div>'
    )
    st.markdown(
        f"""
<div class="wc-brand-hero">
  <div class="wc-brand-hero-logo">{logo_block}</div>
  <div class="wc-brand-hero-body">
    <div class="wc-hero-eyebrow">{html.escape(eyebrow)}</div>
    <h1>{html.escape(title)}</h1>
    <p>{html.escape(subtitle)}</p>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )
