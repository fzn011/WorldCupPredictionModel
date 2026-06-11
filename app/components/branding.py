"""App branding — World Cup 2026 logo in sidebar and hero."""

from __future__ import annotations

import base64
import html
from pathlib import Path

import streamlit as st

_APP_DIR = Path(__file__).resolve().parents[1]
_IMAGES_DIR = _APP_DIR / "static" / "images"

LOGO_STANDARD = _IMAGES_DIR / "world_cup_logo.png"
LOGO_ALT = _IMAGES_DIR / "world_cup_2026_logo.png"
LOGO_LEGACY = _IMAGES_DIR / "hd-official-2026-fifa-world-cup-transparent-png.png"


def resolve_logo_path() -> Path | None:
    """Return first existing logo under app/static/images/."""
    for path in (LOGO_STANDARD, LOGO_ALT, LOGO_LEGACY):
        if path.is_file():
            return path
    for path in sorted(_IMAGES_DIR.glob("*.png")):
        if path.is_file():
            return path
    for path in sorted(_IMAGES_DIR.glob("*.webp")):
        if path.is_file():
            return path
    return None


def logo_data_uri() -> str | None:
    """Base64 data URI for embedding logo in HTML."""
    path = resolve_logo_path()
    if not path:
        return None
    suffix = path.suffix.lower()
    mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(suffix, "image/png")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _logo_block(*, css_class: str, alt: str, fallback_inner: str) -> str:
    data_uri = logo_data_uri()
    if data_uri:
        return (
            f'<img class="{css_class}" src="{data_uri}" alt="{html.escape(alt)}" '
            f'loading="lazy" />'
        )
    return f'<div class="{css_class}-fallback">{fallback_inner}</div>'


def render_sidebar_brand(*, tagline: str = "Analytics Command Center") -> None:
    """Logo + title at top of sidebar."""
    logo_html = _logo_block(
        css_class="wc-sidebar-logo",
        alt="World Cup 2026",
        fallback_inner="WC<br>26",
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
    if resolve_logo_path() is None:
        st.caption("Add logo: app/static/images/world_cup_logo.png")


def render_branded_hero(
    title: str,
    subtitle: str,
    *,
    eyebrow: str = "Command Center",
) -> None:
    """Homepage hero with logo on the left."""
    logo_block = _logo_block(
        css_class="wc-hero-logo",
        alt="World Cup 2026",
        fallback_inner="2026",
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
