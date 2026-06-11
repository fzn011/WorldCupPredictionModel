"""Unified blood-red + black + green Streamlit theme."""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

_SESSION_CSS_KEY = "_worldcup_theme_css_injected"

COLORS: dict[str, str] = {
    "background": "#050505",
    "surface": "#0B0B0B",
    "card": "#111111",
    "card_alt": "#171717",
    "card_border": "#2A2A2A",
    "card_hover": "#171717",
    "primary": "#8B0000",
    "primary_hover": "#A30000",
    "primary_dim": "#4A0000",
    "green": "#16A36A",
    "green_dim": "#0F6B46",
    "white": "#F8F8F8",
    "muted": "#C7C7C7",
    "muted_dark": "#8F8F8F",
    "input_bg": "#161616",
    "input_border": "#8B0000",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "info": "#16A36A",
    "sidebar_bg": "#080808",
    "nav_active": "rgba(139, 0, 0, 0.25)",
    "row_stripe": "#161616",
    # Legacy alias — always blood red, never gold
    "gold": "#8B0000",
    "gold_light": "#A50000",
}

FONT_HEADING = "'Sprintura', 'Segoe UI', sans-serif"
FONT_BODY = "'Roboto', 'Segoe UI', sans-serif"
FONT_MONO = "ui-monospace, 'Cascadia Code', monospace"


def _sprintura_font_src() -> str:
    """Embed Sprintura as data URL so fonts work on every OS without static path issues."""
    fonts_dir = Path(__file__).resolve().parent.parent / "static" / "fonts"
    for name, mime in (
        ("Sprintura-Demo.woff2", "font/woff2"),
        ("Sprintura-Demo.woff", "font/woff"),
    ):
        path = fonts_dir / name
        if path.is_file():
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            return f"url(data:{mime};base64,{encoded}) format('{mime.split('/')[-1]}')"
    return "local('Segoe UI')"


def _inject_raw_html(html: str) -> None:
    """Inject HTML/CSS without rendering as visible page text (Streamlit version-safe)."""
    if hasattr(st, "html"):
        st.html(html, unsafe_allow_javascript=False)
    else:
        st.markdown(html, unsafe_allow_html=True)


def inject_worldcup_css(*, force: bool = False) -> None:
    """Inject global CSS every app run so theme survives page transitions."""
    _ = force  # kept for callers; injection is always applied when invoked

    c = COLORS
    sprintura_src = _sprintura_font_src()
    _inject_raw_html(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;600;700&display=swap');
@font-face {{
  font-family: 'Sprintura';
  src: {sprintura_src};
  font-weight: 400 800;
  font-style: normal;
  font-display: swap;
}}

/* ─── Force dark palette (light-mode toggle safe) ─────────── */
:root {{
  color-scheme: dark;
  --background-color: {c['background']};
  --secondary-background-color: {c['input_bg']};
  --text-color: {c['white']};
}}
html, body {{
  background: {c['background']} !important;
  color: {c['white']} !important;
}}

/* ─── Base ─────────────────────────────────────────────────── */
html, body, [class*="css"], .stMarkdown, .stText, label, p, li, span {{
  font-family: {FONT_BODY} !important;
  color: {c['white']};
}}
h1, h2, h4, h5, h6,
.wc-hero h1, .wc-section h3, .wc-hero-eyebrow,
.wc-card-label, .wc-action-title,
[data-testid="stSidebarNavSeparator"] {{
  font-family: {FONT_HEADING} !important;
  letter-spacing: 0.05em;
}}
h1, h2, .wc-hero h1 {{
  text-transform: uppercase;
}}
h3, .wc-section h3 {{
  font-family: {FONT_HEADING} !important;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}}
.stApp {{
  background: {c['background']} !important;
  color: {c['white']} !important;
}}
[data-testid="stAppViewContainer"] {{
  background: {c['background']} !important;
}}
section.main {{
  background: {c['background']} !important;
  color: {c['white']} !important;
}}
header[data-testid="stHeader"] {{
  background: {c['background']} !important;
  border-bottom: 1px solid {c['card_border']} !important;
}}
[data-testid="stHeader"] * {{
  color: {c['white']} !important;
}}
[data-testid="stToolbar"] {{
  background: transparent !important;
}}
[data-testid="stToolbar"] button,
[data-testid="stToolbar"] svg,
[data-testid="stToolbar"] span {{
  color: {c['white']} !important;
  fill: {c['white']} !important;
}}
[data-testid="stDecoration"] {{
  background: {c['background']} !important;
}}
[data-testid="stStatusWidget"] {{
  background: {c['surface']} !important;
  border: 1px solid {c['card_border']} !important;
  color: {c['white']} !important;
}}
.block-container {{
  padding-top: 1.2rem !important;
  padding-bottom: 2.5rem !important;
  max-width: 1400px !important;
  background: transparent !important;
  animation: wcFadeIn 0.12s ease-in-out;
}}
.main .block-container {{
  animation: wcFadeIn 0.12s ease-in-out;
}}
@keyframes wcFadeIn {{
  from {{ opacity: 0.96; transform: translateY(2px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
.page-frame,
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] {{
  min-height: 720px;
  animation: wcFadeIn 0.15s ease-in-out;
}}
section[data-testid="stSidebar"] [data-testid="stRadio"] label,
section[data-testid="stSidebar"] [data-testid="stRadio"] label span,
section[data-testid="stSidebar"] [data-testid="stRadio"] label p {{
  color: {c['white']} !important;
  font-size: 0.98rem !important;
}}
section[data-testid="stSidebar"] [data-testid="stRadio"] input {{
  accent-color: {c['primary']} !important;
}}
section.main .block-container {{
  max-width: 1400px !important;
}}
h1, h2, h3, h4, h5, h6 {{
  color: {c['white']} !important;
  font-weight: 700 !important;
}}
[data-testid="stMetricValue"] {{
  color: {c['primary']} !important;
  font-family: {FONT_HEADING} !important;
  font-weight: 700 !important;
}}
[data-testid="stMetricLabel"] {{
  color: {c['muted']} !important;
}}
[data-testid="stMetricDelta"] {{ color: {c['green']} !important; }}

/* ─── Sidebar ──────────────────────────────────────────────── */
section[data-testid="stSidebar"] {{
  background: {c['sidebar_bg']} !important;
  border-right: 1px solid {c['card_border']} !important;
}}
section[data-testid="stSidebar"] * {{
  color: {c['muted']};
}}
[data-testid="stSidebarNav"] a {{
  color: {c['muted']} !important;
  border-radius: 8px;
  padding: 0.45rem 0.75rem;
  font-size: 0.93rem;
  transition: background 0.15s, color 0.15s;
}}
[data-testid="stSidebarNav"] a:hover {{
  background: rgba(139, 0, 0, 0.12) !important;
  color: {c['white']} !important;
}}
[data-testid="stSidebarNav"] a[aria-current="page"] {{
  background: {c['nav_active']} !important;
  color: {c['white']} !important;
  border-left: 3px solid {c['primary']} !important;
  font-weight: 600 !important;
}}
[data-testid="stSidebarNavSeparator"] {{
  color: {c['primary']} !important;
  font-size: 0.72rem !important;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  font-weight: 700;
}}

/* ─── Hero ─────────────────────────────────────────────────── */
.wc-hero {{
  background: {c['card']};
  border: 1px solid {c['card_border']};
  border-left: 5px solid {c['primary']};
  border-radius: 14px;
  padding: 1.6rem 1.85rem;
  margin-bottom: 1.25rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
}}
.wc-hero-eyebrow {{
  color: {c['primary']};
  font-size: 0.72rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  font-weight: 700;
  margin-bottom: 0.35rem;
}}
.wc-hero h1 {{
  margin: 0 0 0.35rem 0 !important;
  font-size: 2rem !important;
  font-weight: 800 !important;
  color: {c['white']} !important;
}}
.wc-hero p {{
  color: {c['muted']};
  margin: 0;
  font-size: 1rem;
  line-height: 1.55;
}}

/* ─── Brand bar (logo + hero) ───────────────────────────────── */
.wc-brand-hero {{
  display: flex;
  align-items: center;
  gap: 1.5rem;
  background: linear-gradient(135deg, {c['surface']} 0%, {c['card']} 55%, rgba(139,0,0,0.08) 100%);
  border: 1px solid {c['card_border']};
  border-left: 5px solid {c['primary']};
  border-radius: 16px;
  padding: 1.35rem 1.75rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 10px 40px rgba(0,0,0,0.45);
}}
.wc-brand-hero-logo {{
  flex-shrink: 0;
}}
.wc-hero-logo {{
  display: block;
  max-height: 112px;
  max-width: 88px;
  width: auto;
  height: auto;
  object-fit: contain;
  background: transparent !important;
  filter: drop-shadow(0 4px 14px rgba(0, 0, 0, 0.55));
}}
.wc-hero-logo-fallback {{
  width: 96px;
  height: 96px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: {c['primary']};
  border-radius: 14px;
  font-family: {FONT_HEADING};
  font-weight: 800;
  font-size: 1.4rem;
  color: {c['white']};
}}
.wc-brand-hero-body {{
  flex: 1;
  min-width: 0;
}}
.wc-brand-hero-body h1 {{
  margin: 0.25rem 0 0.35rem 0 !important;
}}

/* ─── Sidebar brand (upper-left) ────────────────────────────── */
.wc-sidebar-brand {{
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.85rem 0.65rem 1.1rem 0.65rem;
  margin-bottom: 0.5rem;
  border-bottom: 1px solid {c['card_border']};
}}
.wc-sidebar-logo {{
  display: block;
  max-height: 56px;
  max-width: 44px;
  width: auto;
  height: auto;
  object-fit: contain;
  flex-shrink: 0;
  background: transparent !important;
}}
.wc-sidebar-logo-fallback {{
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: {c['primary']};
  border-radius: 10px;
  font-family: {FONT_HEADING};
  font-weight: 800;
  font-size: 0.65rem;
  line-height: 1.1;
  text-align: center;
  color: {c['white']};
}}
.wc-sidebar-mark {{
  width: 48px;
  height: 48px;
  flex-shrink: 0;
  border-radius: 10px;
  background: linear-gradient(145deg, {c['primary_dim']} 0%, {c['primary']} 100%);
  border: 1px solid {c['primary_hover']};
  position: relative;
  overflow: hidden;
}}
.wc-sidebar-mark::after {{
  content: "";
  position: absolute;
  inset: 8px;
  border: 1px solid rgba(248, 248, 248, 0.25);
  border-radius: 6px;
}}
.wc-brand-hero-visual {{
  width: 120px;
  height: 88px;
  flex-shrink: 0;
  border-radius: 12px;
  background: linear-gradient(160deg, {c['primary_dim']} 0%, {c['surface']} 45%, {c['card_alt']} 100%);
  border: 1px solid {c['card_border']};
  position: relative;
  overflow: hidden;
}}
.wc-pitch-line-hero {{
  position: absolute;
  left: 12%;
  right: 12%;
  top: 50%;
  height: 1px;
  background: rgba(248, 248, 248, 0.2);
}}
.wc-pitch-line-hero-2 {{
  top: 28%;
  opacity: 0.5;
}}
.wc-pitch-center {{
  position: absolute;
  left: 50%;
  top: 50%;
  width: 36px;
  height: 36px;
  margin: -18px 0 0 -18px;
  border: 1px solid rgba(248, 248, 248, 0.25);
  border-radius: 50%;
}}
.wc-sidebar-brand-title {{
  font-family: {FONT_HEADING};
  font-size: 0.95rem;
  font-weight: 800;
  color: {c['white']};
  letter-spacing: 0.04em;
  text-transform: uppercase;
  line-height: 1.15;
}}
.wc-sidebar-brand-sub {{
  font-size: 0.72rem;
  color: {c['muted']};
  margin-top: 0.15rem;
}}

/* ─── Nav grid tiles ────────────────────────────────────────── */
.wc-nav-tile {{
  background: {c['surface']};
  border: 1px solid {c['card_border']};
  border-left: 3px solid {c['primary']};
  border-radius: 12px;
  padding: 1rem 1rem 0.65rem 1rem;
  margin-bottom: 0.35rem;
  min-height: 108px;
  transition: border-color 0.15s, transform 0.15s;
}}
.wc-nav-tile:hover {{
  border-color: {c['primary']};
  transform: translateY(-2px);
}}
.wc-nav-tile-icon {{ font-size: 1.45rem; margin-bottom: 0.35rem; }}
.wc-nav-tile-title {{
  font-family: {FONT_HEADING};
  color: {c['white']};
  font-weight: 700;
  font-size: 0.88rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}}
.wc-nav-tile-hint {{
  color: {c['muted']};
  font-size: 0.76rem;
  line-height: 1.35;
  margin-top: 0.25rem;
}}

/* ─── Dashboard two-column layout ───────────────────────────── */
.wc-dash-panel {{
  background: {c['surface']};
  border: 1px solid {c['card_border']};
  border-radius: 14px;
  padding: 1.1rem 1.25rem;
  height: 100%;
}}
.wc-dash-panel-title {{
  font-family: {FONT_HEADING};
  color: {c['primary']};
  font-size: 0.82rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-weight: 700;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid {c['card_border']};
}}

/* ─── Cards ────────────────────────────────────────────────── */
.wc-card {{
  background: {c['card']};
  border: 1px solid {c['card_border']};
  border-left: 3px solid {c['primary']};
  border-radius: 12px;
  padding: 1rem 1.15rem;
  min-height: 90px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
  transition: border-color 0.15s, transform 0.15s;
  height: 100%;
}}
.wc-card:hover {{
  border-color: {c['primary']};
  transform: translateY(-2px);
}}
.wc-card-label {{
  color: {c['muted']};
  font-size: 0.74rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 600;
  margin-bottom: 0.35rem;
}}
.wc-card-value {{
  color: {c['white']};
  font-size: 1.35rem;
  font-weight: 800;
  line-height: 1.2;
}}
.wc-card-sub {{
  color: {c['muted']};
  font-size: 0.82rem;
  margin-top: 0.3rem;
  line-height: 1.4;
}}
.wc-card-ok   {{ border-left-color: {c['green']}; }}
.wc-card-ok   .wc-card-value {{ color: {c['green']}; }}
.wc-card-warn {{ border-left-color: {c['warning']}; }}
.wc-card-warn .wc-card-value {{ color: {c['warning']}; }}
.wc-card-danger {{ border-left-color: {c['danger']}; }}
.wc-card-danger .wc-card-value {{ color: {c['danger']}; }}
.wc-card-accent {{ border-left-color: {c['primary']}; }}
.wc-card-accent .wc-card-value {{ color: {c['primary']}; }}
.wc-card-gold {{ border-left-color: {c['primary']}; }}
.wc-card-gold .wc-card-value {{ color: {c['primary']}; }}

/* ─── Section headers ──────────────────────────────────────── */
.wc-section {{ margin: 1.4rem 0 0.5rem 0; }}
.wc-section h3 {{
  margin: 0 !important;
  color: {c['primary']} !important;
  font-size: 0.95rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}}
.wc-pitch-line {{
  height: 2px;
  background: linear-gradient(90deg, {c['primary']}, {c['green']}, transparent);
  margin: 0.45rem 0 0.85rem 0;
  border-radius: 2px;
}}

/* ─── Badges ───────────────────────────────────────────────── */
.wc-badge {{
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.04em;
}}
.wc-badge-ok {{
  background: rgba(22, 163, 106, 0.2);
  color: {c['green']};
  border: 1px solid {c['green']};
}}
.wc-badge-warn {{
  background: rgba(245, 158, 11, 0.2);
  color: {c['warning']};
  border: 1px solid {c['warning']};
}}
.wc-badge-danger {{
  background: rgba(239, 68, 68, 0.2);
  color: {c['danger']};
  border: 1px solid {c['danger']};
}}
.wc-badge-muted {{
  background: {c['surface']};
  color: {c['muted']};
  border: 1px solid {c['card_border']};
}}
.wc-badge-gold, .wc-badge-accent {{
  background: rgba(139, 0, 0, 0.2);
  color: {c['primary']};
  border: 1px solid {c['primary']};
}}

/* ─── Panels ───────────────────────────────────────────────── */
.wc-panel-success {{
  background: {c['green']};
  border: 1px solid {c['green']};
  border-left: 4px solid {c['green_dim']};
  border-radius: 10px;
  padding: 0.85rem 1rem;
  color: {c['white']};
  font-size: 0.92rem;
  line-height: 1.5;
  margin: 0.5rem 0;
}}
.wc-panel-warning {{
  background: {c['warning']};
  border: 1px solid {c['warning']};
  border-left: 4px solid #d97706;
  border-radius: 10px;
  padding: 0.85rem 1rem;
  color: #0B0B0B;
  font-weight: 500;
  font-size: 0.92rem;
  line-height: 1.5;
  margin: 0.5rem 0;
}}
.wc-panel-error {{
  background: {c['danger']};
  border: 1px solid {c['danger']};
  border-left: 4px solid #b91c1c;
  border-radius: 10px;
  padding: 0.85rem 1rem;
  color: {c['white']};
  font-size: 0.92rem;
  line-height: 1.5;
  margin: 0.5rem 0;
}}
.wc-panel-info {{
  background: {c['input_bg']};
  border: 1px solid {c['green']};
  border-left: 4px solid {c['green']};
  border-radius: 10px;
  padding: 0.85rem 1rem;
  color: {c['white']};
  font-size: 0.92rem;
  line-height: 1.5;
  margin: 0.5rem 0;
}}

/* ─── Progress ─────────────────────────────────────────────── */
.wc-progress-wrap {{
  background: {c['surface']};
  border: 1px solid {c['card_border']};
  border-radius: 999px;
  height: 10px;
  overflow: hidden;
  margin: 0.45rem 0 0.2rem 0;
}}
.wc-progress-fill {{
  height: 100%;
  border-radius: 999px;
}}
.wc-progress-fill-ok {{ background: linear-gradient(90deg, {c['green_dim']}, {c['green']}); }}
.wc-progress-fill-warn {{ background: linear-gradient(90deg, #d97706, {c['warning']}); }}
.wc-progress-fill-danger {{ background: linear-gradient(90deg, #b91c1c, {c['danger']}); }}
.wc-progress-fill-gold, .wc-progress-fill-accent {{
  background: linear-gradient(90deg, {c['primary_dim']}, {c['primary']});
}}

/* ─── Checklist rows ───────────────────────────────────────── */
.wc-check-row {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.55rem 0.8rem;
  border-radius: 8px;
  margin-bottom: 4px;
  background: {c['surface']};
  border: 1px solid {c['card_border']};
}}
.wc-check-row-pass {{ border-left: 3px solid {c['green']}; }}
.wc-check-row-fail {{ border-left: 3px solid {c['danger']}; }}
.wc-check-row-warn {{ border-left: 3px solid {c['warning']}; }}
.wc-check-label {{ font-size: 0.88rem; color: {c['white']}; flex: 1; }}
.wc-check-detail {{ font-size: 0.78rem; color: {c['muted']}; }}

/* ─── Download / action cards ──────────────────────────────── */
.wc-download-card {{
  background: {c['card']};
  border: 1px solid {c['card_border']};
  border-top: 3px solid {c['primary']};
  border-radius: 10px;
  padding: 0.85rem 1rem 0.4rem 1rem;
  margin-bottom: 0.25rem;
}}
.wc-action-card {{
  background: {c['card']};
  border: 1px solid {c['card_border']};
  border-left: 3px solid {c['primary']};
  border-radius: 12px;
  padding: 1rem;
  text-align: center;
  transition: border-color 0.15s, transform 0.15s;
}}
.wc-action-card:hover {{
  border-color: {c['primary']};
  transform: translateY(-2px);
}}
.wc-action-icon {{ font-size: 1.5rem; margin-bottom: 0.25rem; }}
.wc-action-title {{ color: {c['white']}; font-weight: 700; font-size: 0.92rem; }}
.wc-action-hint {{ color: {c['muted']}; font-size: 0.76rem; line-height: 1.35; }}
.wc-filename-muted {{
  color: {c['muted_dark']};
  font-size: 0.68rem;
  margin-top: 0.35rem;
  font-family: {FONT_MONO};
}}
.wc-empty-state {{
  background: {c['card']};
  border: 1px dashed {c['card_border']};
  border-radius: 12px;
  padding: 1.25rem 1rem;
  text-align: center;
  margin: 0.5rem 0;
}}

/* ─── Formation / podium ───────────────────────────────────── */
.wc-formation {{
  font-family: ui-monospace, monospace;
  background: {c['input_bg']};
  border: 1px solid {c['green']};
  border-radius: 12px;
  padding: 1.1rem;
  color: {c['green']};
  line-height: 2;
  text-align: center;
  font-size: 0.9rem;
}}
.wc-podium-1 {{ border-top: 3px solid {c['primary']}; }}
.wc-podium-2 {{ border-top: 3px solid {c['muted']}; }}
.wc-podium-3 {{ border-top: 3px solid {c['primary_dim']}; }}

.wc-step {{
  display: flex;
  gap: 0.75rem;
  background: {c['surface']};
  border: 1px solid {c['card_border']};
  border-left: 3px solid {c['primary']};
  border-radius: 10px;
  padding: 0.65rem 0.85rem;
  margin-bottom: 0.4rem;
}}
.wc-step-num {{ color: {c['primary']}; font-weight: 800; min-width: 1.2rem; }}

.wc-dot {{
  display: inline-block;
  width: 8px; height: 8px;
  border-radius: 50%;
  margin-right: 6px;
  vertical-align: middle;
}}
.wc-dot-ok {{ background: {c['green']}; }}
.wc-dot-warn {{ background: {c['warning']}; }}
.wc-dot-danger {{ background: {c['danger']}; }}
.wc-dot-muted {{ background: {c['muted']}; }}

/* ─── Streamlit widgets: inputs ────────────────────────────── */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea,
.stDateInput [data-baseweb="input"] input,
.stNumberInput [data-baseweb="input"] input {{
  background-color: {c['input_bg']} !important;
  color: {c['white']} !important;
  border: 1px solid {c['input_border']} !important;
  border-radius: 8px !important;
  caret-color: {c['white']} !important;
}}
.stTextInput input:focus,
.stNumberInput input:focus,
.stDateInput input:focus,
.stTextArea textarea:focus,
.stTextInput input:focus-visible,
.stNumberInput input:focus-visible {{
  border-color: {c['green']} !important;
  box-shadow: 0 0 0 1px {c['green']} !important;
  outline: none !important;
}}
.stTextInput input:disabled,
.stNumberInput input:disabled,
.stTextArea textarea:disabled {{
  opacity: 0.65 !important;
  color: {c['muted']} !important;
}}
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {{
  color: {c['muted']} !important;
}}
.stTextInput label, .stNumberInput label, .stSelectbox label,
.stDateInput label, .stCheckbox label, .stRadio label,
.stSlider label, .stMultiSelect label {{
  color: {c['white']} !important;
  font-weight: 500 !important;
}}

/* Selectbox / multiselect */
[data-baseweb="select"] > div,
[data-testid="stSelectbox"] [data-baseweb="select"] > div {{
  background-color: {c['input_bg']} !important;
  border: 1px solid {c['input_border']} !important;
  color: {c['white']} !important;
  border-radius: 8px !important;
}}
[data-baseweb="select"] span,
[data-baseweb="select"] div[value] {{
  color: {c['white']} !important;
}}
[data-baseweb="select"] svg {{ fill: {c['muted']} !important; }}
[data-baseweb="popover"] {{
  background: {c['surface']} !important;
  border: 1px solid {c['input_border']} !important;
}}
[data-baseweb="popover"] li {{
  color: {c['white']} !important;
  background: {c['surface']} !important;
}}
[data-baseweb="popover"] li:hover {{
  background: rgba(139, 0, 0, 0.25) !important;
}}
[data-baseweb="menu"] {{
  background: {c['card']} !important;
  border: 1px solid {c['card_border']} !important;
}}
[data-baseweb="menu"] li,
[data-baseweb="menu"] div[role="option"] {{
  color: {c['white']} !important;
  background: {c['card']} !important;
}}
[data-baseweb="menu"] li:hover,
[data-baseweb="menu"] div[role="option"]:hover {{
  background: rgba(139, 0, 0, 0.2) !important;
}}
div[role="listbox"],
div[role="listbox"] li,
div[role="listbox"] div[role="option"] {{
  background-color: {c['card']} !important;
  color: {c['white']} !important;
}}
input,
textarea,
select,
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"],
.stMultiSelect div[data-baseweb="select"] {{
  background-color: {c['input_bg']} !important;
  color: {c['white']} !important;
}}

/* Hide broken Material icon / keyboard text leaks (sidebar only) */
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"],
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"],
section[data-testid="stSidebar"] [data-testid="collapsedControl"],
section[data-testid="stSidebar"] [data-testid="stIconMaterial"],
section[data-testid="stSidebar"] span[data-testid="stIconMaterial"],
section[data-testid="stSidebar"] span.material-icons,
section[data-testid="stSidebar"] span.material-symbols-rounded,
section[data-testid="stSidebar"] span[class*="MaterialIcon"] {{
  display: none !important;
  visibility: hidden !important;
  width: 0 !important;
  height: 0 !important;
  overflow: hidden !important;
  font-size: 0 !important;
  line-height: 0 !important;
  opacity: 0 !important;
  pointer-events: none !important;
}}
[data-testid="stSidebarNav"] a,
[data-testid="stPageLink-NavLink"] a {{
  gap: 0 !important;
  font-size: 0.98rem !important;
  padding: 0.55rem 0.85rem !important;
}}

/* Expander — hide broken arrow/material labels */
[data-testid="stExpander"] summary {{
  list-style: none !important;
  font-size: 1rem !important;
  font-weight: 600 !important;
  color: {c['white']} !important;
}}
[data-testid="stExpander"] summary::-webkit-details-marker {{
  display: none !important;
}}
[data-testid="stExpander"] summary svg,
[data-testid="stExpander"] summary [data-testid="stIconMaterial"],
[data-testid="stExpander"] summary span[class*="material"] {{
  display: none !important;
}}
[data-testid="stExpander"] summary::before {{
  content: "▸ ";
  color: {c['primary']};
  margin-right: 0.35rem;
}}
details[open] > summary::before {{
  content: "▾ ";
}}

/* Tabs — larger, readable */
.stTabs [data-baseweb="tab-list"] {{
  gap: 0.35rem !important;
  border-bottom: 1px solid {c['card_border']} !important;
}}
.stTabs [data-baseweb="tab"] {{
  font-size: 0.95rem !important;
  font-weight: 600 !important;
  padding: 0.65rem 1.1rem !important;
  color: {c['muted']} !important;
  background: transparent !important;
  border-radius: 8px 8px 0 0 !important;
}}
.stTabs [aria-selected="true"] {{
  color: {c['white']} !important;
  background: rgba(139, 0, 0, 0.18) !important;
  border-bottom: 2px solid {c['primary']} !important;
}}

/* Softer default input borders; green on focus only */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea,
[data-baseweb="select"] > div {{
  border-color: {c['card_border']} !important;
}}
.stTextInput input:focus,
.stNumberInput input:focus,
.stDateInput input:focus,
.stTextArea textarea:focus {{
  border-color: {c['green']} !important;
  box-shadow: 0 0 0 1px {c['green']} !important;
}}

/* Number input — compact steppers */
.stNumberInput {{
  max-width: 280px;
}}
.stNumberInput button {{
  border-color: {c['card_border']} !important;
}}

/* Download buttons — secondary, not full-width red bars */
.stDownloadButton > button {{
  background: {c['surface']} !important;
  border: 1px solid {c['card_border']} !important;
  color: {c['white']} !important;
  font-weight: 600 !important;
  width: auto !important;
  min-width: 120px;
  padding: 0.45rem 1rem !important;
  box-shadow: none !important;
}}
.stDownloadButton > button:hover {{
  border-color: {c['primary']} !important;
  color: {c['white']} !important;
}}

/* Primary page-link CTAs on homepage */
[data-testid="stPageLink-NavLink"] a {{
  background: linear-gradient(135deg, {c['primary_dim']} 0%, {c['primary']} 100%) !important;
  border: 1px solid {c['primary']} !important;
  border-radius: 10px !important;
  padding: 0.65rem 1rem !important;
  text-align: center;
  display: block;
}}
[data-testid="stPageLink-NavLink"] a:hover {{
  background: {c['primary_hover']} !important;
}}

.wc-sidebar-logo-wrap {{
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
}}
.wc-sidebar-logo-text {{
  font-family: {FONT_HEADING};
  font-weight: 800;
  font-size: 0.85rem;
  color: {c['primary']};
}}
.wc-sidebar-advanced {{
  margin-top: 1.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid {c['card_border']};
  font-size: 0.82rem;
}}
.wc-card {{
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.35);
  min-height: 96px;
}}
.wc-action-card {{
  min-height: 120px;
  padding: 1.1rem 1rem;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.3);
}}
.wc-disclaimer-sm {{
  color: {c['muted_dark']};
  font-size: 0.78rem;
  margin: 0.5rem 0 1rem 0;
  line-height: 1.4;
}}

/* Slider */
.stSlider [data-baseweb="slider"] div {{
  color: {c['white']} !important;
}}
.stSlider [data-testid="stThumbValue"] {{
  color: {c['white']} !important;
  background: {c['input_bg']} !important;
  border: 1px solid {c['input_border']} !important;
}}

/* Radio / checkbox */
.stRadio div[role="radiogroup"] label,
.stCheckbox label {{
  color: {c['white']} !important;
}}

/* ─── Buttons ──────────────────────────────────────────────── */
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {{
  background: linear-gradient(135deg, {c['primary_dim']} 0%, {c['primary']} 100%) !important;
  border: 1px solid {c['primary']} !important;
  color: {c['white']} !important;
  font-weight: 700 !important;
  border-radius: 10px !important;
  box-shadow: 0 4px 14px rgba(139, 0, 0, 0.35) !important;
}}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {{
  background: {c['primary_hover']} !important;
  border-color: {c['primary_hover']} !important;
}}
.stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]) {{
  background: {c['surface']} !important;
  border: 1px solid {c['card_border']} !important;
  color: {c['white']} !important;
  border-radius: 10px !important;
}}
.stButton > button:not([kind="primary"]):hover {{
  border-color: {c['primary']} !important;
  color: {c['white']} !important;
}}

/* ─── Tabs (secondary block) ─────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
  border-bottom: 2px solid {c['card_border']};
  gap: 0.25rem;
}}
.stTabs [data-baseweb="tab"] {{
  color: {c['muted']} !important;
  background: transparent !important;
  border-radius: 8px 8px 0 0;
  font-weight: 500;
}}
.stTabs [data-baseweb="tab"]:hover {{
  color: {c['white']} !important;
  background: {c['surface']} !important;
}}
.stTabs [aria-selected="true"] {{
  color: {c['white']} !important;
  background: rgba(139, 0, 0, 0.15) !important;
  border-bottom: 2px solid {c['primary']} !important;
  font-weight: 700 !important;
}}

/* ─── Expanders ────────────────────────────────────────────── */
[data-testid="stExpander"] {{
  background: {c['surface']} !important;
  border: 1px solid {c['card_border']} !important;
  border-left: 3px solid {c['green']} !important;
  border-radius: 10px !important;
}}
[data-testid="stExpander"] summary {{
  color: {c['white']} !important;
  font-weight: 600 !important;
}}
[data-testid="stExpander"] summary:hover {{
  color: {c['green']} !important;
}}

/* ─── Dataframes / tables ──────────────────────────────────── */
[data-testid="stDataFrame"] {{
  border: 1px solid {c['primary']} !important;
  border-radius: 10px !important;
  overflow: hidden;
}}
[data-testid="stDataFrame"] div[data-testid="glideDataEditor"] {{
  background: {c['card']} !important;
}}
.dvn-scroller {{ background: {c['card']} !important; }}

/* ─── Native Streamlit alerts ──────────────────────────────── */
[data-testid="stAlert"] {{
  border-radius: 10px !important;
}}
div[data-testid="stNotification"] {{
  background: {c['input_bg']} !important;
  border: 1px solid {c['card_border']} !important;
  color: {c['white']} !important;
}}
[data-baseweb="notification"][kind="info"] {{
  background: {c['input_bg']} !important;
  border: 1px solid {c['green']} !important;
  color: {c['white']} !important;
}}
[data-baseweb="notification"][kind="positive"] {{
  background: rgba(22, 163, 106, 0.15) !important;
  border: 1px solid {c['green']} !important;
  color: {c['white']} !important;
}}
[data-baseweb="notification"][kind="warning"] {{
  background: rgba(245, 158, 11, 0.15) !important;
  border: 1px solid {c['warning']} !important;
  color: {c['white']} !important;
}}
[data-baseweb="notification"][kind="negative"] {{
  background: rgba(239, 68, 68, 0.15) !important;
  border: 1px solid {c['danger']} !important;
  color: {c['white']} !important;
}}

.stCaption, small {{
  color: {c['muted']} !important;
}}
hr {{
  border-color: {c['card_border']} !important;
  opacity: 0.6;
}}

/* Number input stepper buttons */
.stNumberInput button {{
  background: {c['surface']} !important;
  color: {c['white']} !important;
  border: 1px solid {c['input_border']} !important;
}}
.stNumberInput [data-testid="stNumberInputContainer"] {{
  background: {c['input_bg']} !important;
  border: 1px solid {c['input_border']} !important;
  border-radius: 8px !important;
}}

/* JSON / code blocks */
.stJson, pre, code {{
  background: {c['input_bg']} !important;
  color: {c['green']} !important;
  border: 1px solid {c['card_border']} !important;
  border-radius: 8px !important;
  font-family: {FONT_MONO} !important;
}}

/* ─── Light theme override (Streamlit settings toggle) ─────── */
html[data-theme="light"] .stApp,
html[data-theme="light"] section.main,
html[data-theme="light"] [data-testid="stAppViewContainer"],
html[data-theme="light"] header[data-testid="stHeader"],
html[data-theme="light"] [data-testid="stDecoration"] {{
  background: {c['background']} !important;
  color: {c['white']} !important;
}}
html[data-theme="light"] .stApp *:not(.wc-panel-warning):not(.wc-panel-warning *) {{
  color: inherit;
}}
html[data-theme="light"] h1,
html[data-theme="light"] h2,
html[data-theme="light"] h3,
html[data-theme="light"] h4,
html[data-theme="light"] label,
html[data-theme="light"] p,
html[data-theme="light"] .stMarkdown,
html[data-theme="light"] [data-testid="stSidebarNav"] a {{
  color: {c['white']} !important;
}}
html[data-theme="light"] header[data-testid="stHeader"],
html[data-theme="light"] [data-testid="stToolbar"] button {{
  color: {c['white']} !important;
  background: transparent !important;
}}
html[data-theme="light"] .stTextInput input,
html[data-theme="light"] .stNumberInput input,
html[data-theme="light"] [data-baseweb="select"] > div {{
  background-color: {c['input_bg']} !important;
  color: {c['white']} !important;
  border-color: {c['input_border']} !important;
}}

/* Page links */
[data-testid="stPageLink-NavLink"] a {{
  color: {c['primary']} !important;
  font-weight: 600;
}}
</style>
        """
    )


inject_worldcup_theme = inject_worldcup_css
