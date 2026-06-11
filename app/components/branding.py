"""App branding — CSS-only visuals (no copyrighted logos or external images)."""

from __future__ import annotations

import html

import streamlit as st


def render_sidebar_brand(*, tagline: str = "Analytics Command Center") -> None:
    """Text-only sidebar header with abstract mark (no image files)."""
    st.markdown(
        f"""
<div class="wc-sidebar-brand">
  <div class="wc-sidebar-mark" aria-hidden="true"></div>
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
    """Homepage hero — gradient pitch banner, no external images."""
    st.markdown(
        f"""
<div class="wc-brand-hero wc-brand-hero-css">
  <div class="wc-brand-hero-visual" aria-hidden="true">
    <div class="wc-pitch-line-hero"></div>
    <div class="wc-pitch-line-hero wc-pitch-line-hero-2"></div>
    <div class="wc-pitch-center"></div>
  </div>
  <div class="wc-brand-hero-body">
    <div class="wc-hero-eyebrow">{html.escape(eyebrow)}</div>
    <h1>{html.escape(title)}</h1>
    <p>{html.escape(subtitle)}</p>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )
