"""World Cup inspired dark premium theme for Streamlit (no copyrighted FIFA assets)."""

from __future__ import annotations

import streamlit as st

COLORS: dict[str, str] = {
    "background": "#07111F",
    "card": "#0E1B2A",
    "card_border": "#1E3A5F",
    "gold": "#D6A84F",
    "green": "#16A36A",
    "white": "#F8FAFC",
    "muted": "#94A3B8",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "info": "#38BDF8",
}


def inject_worldcup_css() -> None:
    """Inject global CSS once per page render."""
    c = COLORS
    st.markdown(
        f"""
<style>
/* App shell */
.stApp {{
  background: radial-gradient(1200px 600px at 20% -10%, #0f2844 0%, {c['background']} 45%, #040a14 100%);
  color: {c['white']};
}}
.block-container {{
  padding-top: 1.25rem;
  padding-bottom: 2rem;
}}
h1, h2, h3, h4, h5, h6, p, label, span {{
  color: {c['white']};
}}
[data-testid="stMetricValue"] {{
  color: {c['gold']} !important;
}}
[data-testid="stMetricLabel"] {{
  color: {c['muted']} !important;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, #0a1628 0%, {c['background']} 100%);
  border-right: 1px solid {c['card_border']};
}}
section[data-testid="stSidebar"] .block-container {{
  padding-top: 1rem;
}}

/* Glass cards */
.wc-hero {{
  background: linear-gradient(135deg, rgba(14,27,42,0.95) 0%, rgba(10,22,40,0.85) 100%);
  border: 1px solid {c['card_border']};
  border-left: 4px solid {c['gold']};
  border-radius: 16px;
  padding: 1.5rem 1.75rem;
  margin-bottom: 1rem;
  box-shadow: 0 12px 40px rgba(0,0,0,0.35);
}}
.wc-hero h1 {{
  margin: 0 0 0.35rem 0;
  font-size: 2rem;
  letter-spacing: 0.02em;
}}
.wc-hero p {{
  color: {c['muted']};
  margin: 0;
  font-size: 1.02rem;
}}
.wc-card {{
  background: rgba(14,27,42,0.92);
  border: 1px solid {c['card_border']};
  border-radius: 14px;
  padding: 1rem 1.1rem;
  min-height: 110px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
  transition: transform 0.15s ease, border-color 0.15s ease;
}}
.wc-card:hover {{
  transform: translateY(-2px);
  border-color: {c['gold']};
}}
.wc-card-label {{
  color: {c['muted']};
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 0.35rem;
}}
.wc-card-value {{
  color: {c['white']};
  font-size: 1.35rem;
  font-weight: 700;
}}
.wc-card-sub {{
  color: {c['muted']};
  font-size: 0.85rem;
  margin-top: 0.25rem;
}}
.wc-section {{
  margin: 1.25rem 0 0.75rem 0;
  padding-bottom: 0.35rem;
  border-bottom: 1px solid rgba(22,163,106,0.35);
}}
.wc-section h3 {{
  margin: 0;
  color: {c['gold']};
  font-size: 1.05rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}}
.wc-badge {{
  display: inline-block;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.04em;
}}
.wc-badge-ok {{ background: rgba(22,163,106,0.2); color: {c['green']}; border: 1px solid {c['green']}; }}
.wc-badge-warn {{ background: rgba(245,158,11,0.15); color: {c['warning']}; border: 1px solid {c['warning']}; }}
.wc-badge-danger {{ background: rgba(239,68,68,0.15); color: {c['danger']}; border: 1px solid {c['danger']}; }}
.wc-badge-muted {{ background: rgba(148,163,184,0.12); color: {c['muted']}; border: 1px solid {c['card_border']}; }}
.wc-panel-warning {{
  background: rgba(245,158,11,0.08);
  border: 1px solid rgba(245,158,11,0.35);
  border-radius: 12px;
  padding: 0.85rem 1rem;
  color: {c['white']};
}}
.wc-panel-success {{
  background: rgba(22,163,106,0.08);
  border: 1px solid rgba(22,163,106,0.35);
  border-radius: 12px;
  padding: 0.85rem 1rem;
  color: {c['white']};
}}
.wc-pitch-line {{
  height: 2px;
  background: linear-gradient(90deg, transparent, {c['green']}, transparent);
  margin: 0.75rem 0 1rem 0;
}}
.wc-step {{
  background: rgba(14,27,42,0.75);
  border: 1px dashed {c['card_border']};
  border-radius: 10px;
  padding: 0.65rem 0.85rem;
  margin-bottom: 0.45rem;
}}
.wc-step-num {{
  color: {c['gold']};
  font-weight: 700;
  margin-right: 0.35rem;
}}
.wc-download-card {{
  background: rgba(14,27,42,0.88);
  border: 1px solid {c['card_border']};
  border-radius: 12px;
  padding: 0.85rem 1rem;
}}
.wc-formation {{
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  background: rgba(7,17,31,0.9);
  border: 1px solid {c['card_border']};
  border-radius: 12px;
  padding: 1rem;
  color: {c['green']};
  line-height: 1.5;
  text-align: center;
}}
/* Dataframes */
[data-testid="stDataFrame"] {{
  border: 1px solid {c['card_border']};
  border-radius: 10px;
}}
/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
  gap: 0.35rem;
}}
.stTabs [data-baseweb="tab"] {{
  background: rgba(14,27,42,0.6);
  border-radius: 10px 10px 0 0;
  border: 1px solid {c['card_border']};
  color: {c['muted']};
}}
.stTabs [aria-selected="true"] {{
  background: rgba(214,168,79,0.12) !important;
  color: {c['gold']} !important;
  border-color: {c['gold']} !important;
}}
</style>
        """,
        unsafe_allow_html=True,
    )
