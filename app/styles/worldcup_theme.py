"""Unified blood-red + black + green Streamlit theme (Step 20B)."""

from __future__ import annotations

import streamlit as st

COLORS: dict[str, str] = {
    "background": "#0B0B0B",
    "card": "#0B0B0B",
    "card_elevated": "#121212",
    "card_border": "#2A2A2A",
    "primary": "#8B0000",
    "primary_hover": "#A50000",
    "green": "#16A36A",
    "white": "#F8F8F8",
    "muted": "#C0C0C0",
    "input_bg": "#1F1F1F",
    "input_border": "#8B0000",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "row_stripe": "#141414",
    # Legacy alias used by older component references
    "gold": "#8B0000",
    "info": "#16A36A",
}

FONT_STACK = "'Montserrat', 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"

CARD_RADIUS = "14px"
CARD_PADDING = "1rem 1.1rem"
CARD_SHADOW = "0 8px 24px rgba(0,0,0,0.45)"


def inject_worldcup_css() -> None:
    """Inject global CSS for all Streamlit pages."""
    c = COLORS
    st.markdown(
        f"""
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
/* ---- Base shell ---- */
html, body, [class*="css"] {{
  font-family: {FONT_STACK};
}}
.stApp {{
  background: radial-gradient(900px 500px at 15% -5%, #1a0000 0%, {c['background']} 50%, #050505 100%);
  color: {c['white']};
}}
.block-container {{
  padding-top: 1.25rem;
  padding-bottom: 2rem;
  max-width: 1400px;
}}
h1, h2, h3, h4, h5, h6 {{
  color: {c['white']} !important;
  font-family: {FONT_STACK};
}}
p, label, span, li {{
  color: {c['white']};
}}
small, .stCaption, [data-testid="stCaptionContainer"] {{
  color: {c['muted']} !important;
}}
code {{
  background: {c['input_bg']} !important;
  color: {c['green']} !important;
  border: 1px solid {c['card_border']};
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
}}

/* ---- Metrics ---- */
[data-testid="stMetricValue"] {{
  color: {c['green']} !important;
}}
[data-testid="stMetricLabel"] {{
  color: {c['muted']} !important;
}}
[data-testid="stMetricDelta"] {{
  color: {c['white']} !important;
}}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, #120000 0%, {c['background']} 100%);
  border-right: 1px solid {c['primary']};
}}
section[data-testid="stSidebar"] .block-container {{
  padding-top: 1rem;
}}
section[data-testid="stSidebar"] a {{
  color: {c['white']} !important;
}}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {{
  color: {c['muted']} !important;
}}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {{
  color: {c['white']} !important;
  background: rgba(139,0,0,0.25) !important;
  border-left: 3px solid {c['primary']};
}}

/* ---- Inputs: text, number, date, textarea ---- */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea,
.stDateInput [data-baseweb="input"] input {{
  background-color: {c['input_bg']} !important;
  color: {c['white']} !important;
  border: 1px solid {c['input_border']} !important;
  border-radius: 8px !important;
}}
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {{
  color: {c['muted']} !important;
}}
.stTextInput label,
.stNumberInput label,
.stDateInput label,
.stSelectbox label,
.stSlider label,
.stRadio label,
.stCheckbox label,
.stMultiSelect label {{
  color: {c['white']} !important;
  font-weight: 500;
}}

/* Selectbox / multiselect */
div[data-baseweb="select"] > div,
div[data-baseweb="select"] > div > div {{
  background-color: {c['input_bg']} !important;
  border-color: {c['input_border']} !important;
  color: {c['white']} !important;
}}
div[data-baseweb="select"] span {{
  color: {c['white']} !important;
}}
ul[role="listbox"] {{
  background-color: {c['input_bg']} !important;
  border: 1px solid {c['input_border']} !important;
}}
ul[role="listbox"] li {{
  color: {c['white']} !important;
}}
ul[role="listbox"] li:hover {{
  background-color: rgba(139,0,0,0.35) !important;
}}

/* Slider */
.stSlider [data-baseweb="slider"] div[role="slider"] {{
  background: {c['primary']} !important;
}}
.stSlider [data-baseweb="slider"] div {{
  color: {c['white']} !important;
}}

/* Checkbox / radio */
.stCheckbox span[data-testid="stMarkdownContainer"] p,
.stRadio span[data-testid="stMarkdownContainer"] p {{
  color: {c['white']} !important;
}}

/* ---- Buttons ---- */
.stButton > button[kind="primary"],
.stDownloadButton > button,
.stFormSubmitButton > button {{
  background-color: {c['primary']} !important;
  color: {c['white']} !important;
  border: 1px solid {c['primary']} !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
}}
.stButton > button[kind="primary"]:hover,
.stDownloadButton > button:hover,
.stFormSubmitButton > button:hover {{
  background-color: {c['primary_hover']} !important;
  border-color: {c['primary_hover']} !important;
}}
.stButton > button[kind="secondary"] {{
  background-color: {c['input_bg']} !important;
  color: {c['white']} !important;
  border: 1px solid {c['primary']} !important;
  border-radius: 8px !important;
}}
.stButton > button[kind="secondary"]:hover {{
  border-color: {c['primary_hover']} !important;
  color: {c['white']} !important;
}}

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"] {{
  gap: 0.35rem;
  border-bottom: 1px solid {c['card_border']};
}}
.stTabs [data-baseweb="tab"] {{
  background: {c['card_elevated']} !important;
  border-radius: 8px 8px 0 0;
  border: 1px solid {c['card_border']} !important;
  color: {c['muted']} !important;
}}
.stTabs [aria-selected="true"] {{
  background: rgba(139,0,0,0.2) !important;
  color: {c['white']} !important;
  border-color: {c['primary']} !important;
  border-bottom-color: {c['primary']} !important;
}}

/* ---- Expanders ---- */
[data-testid="stExpander"] details {{
  background: {c['card_elevated']};
  border: 1px solid {c['card_border']};
  border-radius: 10px;
}}
[data-testid="stExpander"] summary {{
  color: {c['white']} !important;
  font-weight: 600;
}}
.wc-expander-green [data-testid="stExpander"] details {{
  border-color: {c['green']} !important;
}}

/* ---- Dataframes / tables ---- */
[data-testid="stDataFrame"] {{
  border: 1px solid {c['primary']};
  border-radius: 10px;
  overflow: hidden;
}}
[data-testid="stDataFrame"] div {{
  background: {c['background']} !important;
}}

/* ---- Native alerts (info / warning / error / success) ---- */
div[data-testid="stAlert"] {{
  border-radius: 10px;
}}
div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span {{
  color: {c['white']} !important;
}}
div[data-baseweb="notification"] {{
  border-radius: 10px !important;
}}

/* ---- Progress ---- */
.stProgress > div > div {{
  background-color: {c['primary']} !important;
}}
.stProgress > div {{
  background-color: {c['input_bg']} !important;
}}

/* ---- Custom components ---- */
.wc-hero {{
  background: linear-gradient(135deg, {c['card_elevated']} 0%, {c['background']} 100%);
  border: 1px solid {c['card_border']};
  border-left: 4px solid {c['primary']};
  border-radius: {CARD_RADIUS};
  padding: 1.5rem 1.75rem;
  margin-bottom: 1rem;
  box-shadow: {CARD_SHADOW};
}}
.wc-hero h1 {{
  margin: 0 0 0.35rem 0;
  font-size: 2rem;
  letter-spacing: 0.02em;
  color: {c['white']} !important;
}}
.wc-hero p {{
  color: {c['muted']};
  margin: 0;
  font-size: 1.02rem;
}}
.wc-hero-eyebrow {{
  color: {c['primary']};
  font-size: 0.8rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-bottom: 0.35rem;
  font-weight: 600;
}}
.wc-card {{
  background: {c['card']};
  border: 1px solid {c['primary']};
  border-radius: {CARD_RADIUS};
  padding: {CARD_PADDING};
  min-height: 110px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
  transition: transform 0.15s ease, border-color 0.15s ease;
}}
.wc-card:hover {{
  transform: translateY(-2px);
  border-color: {c['primary_hover']};
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
.wc-card-value-accent {{
  color: {c['green']};
}}
.wc-card-sub {{
  color: {c['muted']};
  font-size: 0.85rem;
  margin-top: 0.25rem;
}}
.wc-section {{
  margin: 1.25rem 0 0.75rem 0;
  padding-bottom: 0.35rem;
  border-bottom: 2px solid {c['primary']};
}}
.wc-section h3 {{
  margin: 0;
  color: {c['primary']} !important;
  font-size: 1.05rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  font-weight: 700;
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
.wc-badge-warn {{ background: rgba(245,158,11,0.2); color: {c['warning']}; border: 1px solid {c['warning']}; }}
.wc-badge-danger {{ background: rgba(239,68,68,0.2); color: {c['danger']}; border: 1px solid {c['danger']}; }}
.wc-badge-muted {{ background: rgba(192,192,192,0.1); color: {c['muted']}; border: 1px solid {c['card_border']}; }}
.wc-panel-warning {{
  background: {c['warning']};
  border: 1px solid {c['warning']};
  border-radius: 12px;
  padding: 0.85rem 1rem;
  color: #0B0B0B !important;
  font-weight: 500;
}}
.wc-panel-warning * {{
  color: #0B0B0B !important;
}}
.wc-panel-success {{
  background: {c['green']};
  border: 1px solid {c['green']};
  border-radius: 12px;
  padding: 0.85rem 1rem;
  color: {c['white']} !important;
}}
.wc-panel-success * {{
  color: {c['white']} !important;
}}
.wc-panel-error {{
  background: {c['danger']};
  border: 1px solid {c['danger']};
  border-radius: 12px;
  padding: 0.85rem 1rem;
  color: {c['white']} !important;
}}
.wc-panel-error * {{
  color: {c['white']} !important;
}}
.wc-panel-info {{
  background: {c['card_elevated']};
  border: 1px solid {c['green']};
  border-left: 4px solid {c['green']};
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
  background: {c['card_elevated']};
  border: 1px dashed {c['card_border']};
  border-left: 3px solid {c['primary']};
  border-radius: 10px;
  padding: 0.65rem 0.85rem;
  margin-bottom: 0.45rem;
  color: {c['white']};
}}
.wc-step-num {{
  color: {c['green']};
  font-weight: 700;
  margin-right: 0.35rem;
}}
.wc-download-card {{
  background: {c['card_elevated']};
  border: 1px solid {c['primary']};
  border-radius: 12px;
  padding: 0.85rem 1rem;
  margin-bottom: 0.35rem;
}}
.wc-download-card .wc-card-label {{
  color: {c['primary']};
  font-weight: 700;
}}
.wc-formation {{
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  background: {c['card_elevated']};
  border: 1px solid {c['green']};
  border-radius: 12px;
  padding: 1rem;
  color: {c['green']};
  line-height: 1.5;
  text-align: center;
}}
</style>
        """,
        unsafe_allow_html=True,
    )
