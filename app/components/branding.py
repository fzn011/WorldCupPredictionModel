"""App branding — World Cup 2026 logo in sidebar and hero."""

from __future__ import annotations

import base64
import html
from pathlib import Path

import streamlit as st

_APP_DIR = Path(__file__).resolve().parents[1]
_IMAGES_DIR = _APP_DIR / "static" / "images"

LOGO_OFFICIAL = _IMAGES_DIR / (
    "hd-official-2026-fifa-world-cup-transparent-png-701751712076865bw3umpw9lk.png"
)
LOGO_STANDARD = _IMAGES_DIR / "world_cup_logo.png"
LOGO_ALT = _IMAGES_DIR / "world_cup_2026_logo.png"
LOGO_LEGACY = _IMAGES_DIR / "hd-official-2026-fifa-world-cup-transparent-png.png"


def resolve_logo_path() -> Path | None:
    for path in (LOGO_OFFICIAL, LOGO_STANDARD, LOGO_ALT, LOGO_LEGACY):
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


def _logo_block(*, css_class: str, alt: str) -> str:
    data_uri = logo_data_uri()
    if data_uri:
        return (
            f'<img class="{css_class}" src="{data_uri}" alt="{html.escape(alt)}" '
            f'loading="lazy" />'
        )
    return ""


def render_sidebar_brand(*, tagline: str = "AI Predictor") -> None:
    """Clean sidebar brand block."""
    logo_html = _logo_block(css_class="wc-sidebar-logo", alt="World Cup 2026")
    logo_slot = logo_html if logo_html else '<div class="wc-sidebar-logo-text">WC</div>'
    st.markdown(
        f"""
<div class="wc-sidebar-brand">
  <div class="wc-sidebar-logo-wrap">{logo_slot}</div>
    <div class="wc-sidebar-brand-text">
    <div class="wc-sidebar-brand-title">World Cup 2026</div>
    <div class="wc-sidebar-brand-sub">{html.escape(tagline)}</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_branded_hero(
    title: str,
    subtitle: str,
    *,
    eyebrow: str = "Command Center",
) -> None:
    logo_block = _logo_block(css_class="wc-hero-logo", alt="World Cup 2026")
    logo_col = (
        f'<div class="wc-brand-hero-logo">{logo_block}</div>' if logo_block else ""
    )
    st.markdown(
        f"""
<div class="wc-brand-hero">
  {logo_col}
  <div class="wc-brand-hero-body">
    <div class="wc-hero-eyebrow wc-page-eyebrow">{html.escape(eyebrow)}</div>
    <h1 class="wc-page-title">{html.escape(title)}</h1>
    <p class="wc-page-subtitle">{html.escape(subtitle)}</p>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )
