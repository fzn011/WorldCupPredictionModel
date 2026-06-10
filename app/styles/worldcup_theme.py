"""Unified blood-red + black + green Streamlit theme (Step 20B)."""

from __future__ import annotations

import streamlit as st

COLORS: dict[str, str] = {
    "background": "#0B0B0B",
    "card": "#0B0B0B",
    "card_border": "#2A2A2A",
    "card_hover": "#1A1A1A",
    "primary": "#8B0000",
    "primary_hover": "#A50000",
    "gold": "#8B0000",
    "gold_light": "#A50000",
    "green": "#16A36A",
    "green_dim": "#0d7a50",
    "white": "#F8F8F8",
    "muted": "#C0C0C0",
    "muted_dark": "#909090",
    "input_bg": "#1F1F1F",
    "input_border": "#8B0000",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "info": "#16A36A",
    "sidebar_bg": "#080808",
    "nav_active": "rgba(139,0,0,0.2)",
}


def inject_worldcup_css() -> None:
    """Inject global CSS once per page render."""
    c = COLORS
    st.markdown(
        f"""
<style>
/* ─── App shell ─────────────────────────────────────────── */
.stApp {{
  background: radial-gradient(ellipse 140% 80% at 15% -5%,
              #0f2844 0%, {c['background']} 50%, #030c18 100%);
  color: {c['white']};
}}
.block-container {{
  padding-top: 1.5rem !important;
  padding-bottom: 3rem !important;
  max-width: 1400px !important;
}}
/* Global text */
h1, h2, h3, h4, h5, h6 {{ color: {c['white']} !important; }}
p, li, span, label, div {{ color: {c['white']}; }}
[data-testid="stMetricValue"] {{ color: {c['gold']} !important; font-weight: 700 !important; }}
[data-testid="stMetricLabel"] {{ color: {c['muted']} !important; font-size: 0.82rem !important; }}
[data-testid="stMetricDelta"] {{ font-size: 0.8rem !important; }}

/* ─── Sidebar ─────────────────────────────────────────────── */
section[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, {c['sidebar_bg']} 0%, #08121f 100%);
  border-right: 1px solid {c['card_border']};
}}
section[data-testid="stSidebar"] .block-container {{
  padding-top: 0.5rem !important;
}}
/* Nav items */
[data-testid="stSidebarNav"] li {{
  margin: 2px 0;
}}
[data-testid="stSidebarNav"] a {{
  color: {c['muted']} !important;
  border-radius: 8px;
  padding: 0.45rem 0.75rem;
  transition: all 0.15s ease;
  font-size: 0.93rem;
}}
[data-testid="stSidebarNav"] a:hover {{
  background: rgba(214,168,79,0.08) !important;
  color: {c['gold']} !important;
}}
[data-testid="stSidebarNav"] a[aria-current="page"] {{
  background: {c['nav_active']} !important;
  color: {c['gold']} !important;
  border-left: 3px solid {c['gold']};
  font-weight: 600;
}}
/* Nav section labels */
[data-testid="stSidebarNavSeparator"] {{
  color: {c['muted_dark']} !important;
  font-size: 0.72rem !important;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 0.75rem 0.75rem 0.2rem 0.75rem;
}}

/* ─── Hero banner ─────────────────────────────────────────── */
.wc-hero {{
  background: linear-gradient(135deg,
    rgba(14,27,42,0.97) 0%,
    rgba(10,22,40,0.90) 60%,
    rgba(22,163,106,0.08) 100%);
  border: 1px solid {c['card_border']};
  border-left: 5px solid {c['gold']};
  border-radius: 18px;
  padding: 1.75rem 2rem;
  margin-bottom: 1.25rem;
  box-shadow: 0 16px 48px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.04);
  position: relative;
  overflow: hidden;
}}
.wc-hero::before {{
  content: "";
  position: absolute;
  top: -60px; right: -60px;
  width: 220px; height: 220px;
  background: radial-gradient(circle, rgba(214,168,79,0.08) 0%, transparent 70%);
  pointer-events: none;
}}
.wc-hero-eyebrow {{
  color: {c['gold']};
  font-size: 0.75rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  font-weight: 600;
  margin-bottom: 0.4rem;
}}
.wc-hero h1 {{
  margin: 0 0 0.4rem 0 !important;
  font-size: 2.1rem !important;
  font-weight: 800 !important;
  letter-spacing: 0.01em;
  line-height: 1.18;
  color: {c['white']} !important;
}}
.wc-hero p {{
  color: {c['muted']};
  margin: 0;
  font-size: 1.05rem;
  line-height: 1.55;
}}

/* ─── Metric / status cards ───────────────────────────────── */
.wc-card {{
  background: rgba(14,27,42,0.94);
  border: 1px solid {c['card_border']};
  border-radius: 14px;
  padding: 1.1rem 1.2rem;
  min-height: 100px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.25),
              inset 0 1px 0 rgba(255,255,255,0.04);
  transition: transform 0.15s ease, border-color 0.2s ease, box-shadow 0.2s ease;
  height: 100%;
}}
.wc-card:hover {{
  transform: translateY(-3px);
  border-color: {c['gold']};
  box-shadow: 0 8px 28px rgba(0,0,0,0.35), 0 0 0 1px rgba(214,168,79,0.15);
}}
.wc-card-label {{
  color: {c['muted']};
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.09em;
  margin-bottom: 0.4rem;
  font-weight: 600;
}}
.wc-card-value {{
  color: {c['white']};
  font-size: 1.4rem;
  font-weight: 800;
  line-height: 1.2;
}}
.wc-card-sub {{
  color: {c['muted']};
  font-size: 0.83rem;
  margin-top: 0.3rem;
  line-height: 1.4;
}}
.wc-card-ok   .wc-card-value {{ color: {c['green']}; }}
.wc-card-warn .wc-card-value {{ color: {c['warning']}; }}
.wc-card-danger .wc-card-value {{ color: {c['danger']}; }}
.wc-card-gold   .wc-card-value {{ color: {c['gold']}; }}

/* ─── Section header ──────────────────────────────────────── */
.wc-section {{
  margin: 1.5rem 0 0.65rem 0;
}}
.wc-section h3 {{
  margin: 0 0 0.45rem 0 !important;
  color: {c['gold']} !important;
  font-size: 0.88rem !important;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  font-weight: 700;
}}
.wc-pitch-line {{
  height: 1px;
  background: linear-gradient(90deg, {c['green_dim']}, rgba(22,163,106,0.15), transparent);
  margin-bottom: 0.75rem;
}}

/* ─── Badges ──────────────────────────────────────────────── */
.wc-badge {{
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.22rem 0.65rem;
  border-radius: 999px;
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  white-space: nowrap;
}}
.wc-badge-ok     {{ background:rgba(22,163,106,0.18); color:{c['green']};   border:1px solid rgba(22,163,106,0.5); }}
.wc-badge-warn   {{ background:rgba(245,158,11,0.15); color:{c['warning']}; border:1px solid rgba(245,158,11,0.4); }}
.wc-badge-danger {{ background:rgba(239,68,68,0.14);  color:{c['danger']};  border:1px solid rgba(239,68,68,0.4); }}
.wc-badge-muted  {{ background:rgba(148,163,184,0.1); color:{c['muted']};   border:1px solid {c['card_border']}; }}
.wc-badge-gold   {{ background:rgba(214,168,79,0.15); color:{c['gold']};    border:1px solid rgba(214,168,79,0.4); }}

/* ─── Panels ──────────────────────────────────────────────── */
.wc-panel-warning {{
  background: rgba(245,158,11,0.07);
  border: 1px solid rgba(245,158,11,0.3);
  border-left: 4px solid {c['warning']};
  border-radius: 12px;
  padding: 0.9rem 1.1rem;
  color: {c['white']};
  font-size: 0.93rem;
  line-height: 1.5;
}}
.wc-panel-success {{
  background: rgba(22,163,106,0.07);
  border: 1px solid rgba(22,163,106,0.3);
  border-left: 4px solid {c['green']};
  border-radius: 12px;
  padding: 0.9rem 1.1rem;
  color: {c['white']};
  font-size: 0.93rem;
  line-height: 1.5;
}}
.wc-panel-info {{
  background: rgba(56,189,248,0.07);
  border: 1px solid rgba(56,189,248,0.3);
  border-left: 4px solid {c['info']};
  border-radius: 12px;
  padding: 0.9rem 1.1rem;
  color: {c['white']};
  font-size: 0.93rem;
  line-height: 1.5;
}}

/* ─── Steps / pipeline ────────────────────────────────────── */
.wc-step {{
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  background: rgba(14,27,42,0.7);
  border: 1px solid {c['card_border']};
  border-radius: 10px;
  padding: 0.7rem 0.9rem;
  margin-bottom: 0.45rem;
}}
.wc-step-num {{
  color: {c['gold']};
  font-weight: 800;
  font-size: 1.1rem;
  min-width: 1.4rem;
  line-height: 1.35;
}}

/* ─── Download cards ──────────────────────────────────────── */
.wc-download-card {{
  background: rgba(14,27,42,0.9);
  border: 1px solid {c['card_border']};
  border-radius: 12px;
  padding: 0.85rem 1rem 0.5rem 1rem;
  margin-bottom: 0.1rem;
}}
.wc-download-card .wc-card-label {{ margin-bottom: 0.15rem; }}

/* ─── Formation diagram ───────────────────────────────────── */
.wc-formation {{
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  background: rgba(7,17,31,0.9);
  border: 1px solid {c['card_border']};
  border-radius: 14px;
  padding: 1.25rem 1rem;
  color: {c['green']};
  line-height: 2.2;
  text-align: center;
  font-size: 0.95rem;
  letter-spacing: 0.03em;
}}

/* ─── Podium cards ────────────────────────────────────────── */
.wc-podium-1 {{ border-top: 3px solid {c['gold']}; }}
.wc-podium-2 {{ border-top: 3px solid #9CA3AF; }}
.wc-podium-3 {{ border-top: 3px solid #92400E; }}

/* ─── Progress bar ────────────────────────────────────────── */
.wc-progress-wrap {{
  background: rgba(30,58,95,0.4);
  border-radius: 999px;
  height: 8px;
  overflow: hidden;
  margin: 0.5rem 0 0.25rem 0;
}}
.wc-progress-fill {{
  height: 100%;
  border-radius: 999px;
  transition: width 0.4s ease;
}}
.wc-progress-fill-ok     {{ background: linear-gradient(90deg, {c['green_dim']}, {c['green']}); }}
.wc-progress-fill-warn   {{ background: linear-gradient(90deg, #d97706, {c['warning']}); }}
.wc-progress-fill-danger {{ background: linear-gradient(90deg, #b91c1c, {c['danger']}); }}
.wc-progress-fill-gold   {{ background: linear-gradient(90deg, #b5832a, {c['gold']}); }}

/* ─── Readiness checklist row ─────────────────────────────── */
.wc-check-row {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  margin-bottom: 4px;
  background: rgba(14,27,42,0.5);
  border: 1px solid transparent;
}}
.wc-check-row:hover {{ border-color: {c['card_border']}; }}
.wc-check-row-pass {{ border-left: 3px solid {c['green']}; }}
.wc-check-row-fail {{ border-left: 3px solid {c['danger']}; }}
.wc-check-row-warn {{ border-left: 3px solid {c['warning']}; }}
.wc-check-label {{ font-size: 0.88rem; color: {c['white']}; flex: 1; }}
.wc-check-detail {{ font-size: 0.8rem; color: {c['muted']}; margin-left: 1rem; }}

/* ─── Dataframes ──────────────────────────────────────────── */
[data-testid="stDataFrame"] {{
  border: 1px solid {c['card_border']} !important;
  border-radius: 12px !important;
  overflow: hidden;
}}
.dvn-scroller {{ background: {c['card']} !important; }}

/* ─── Tabs ────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
  gap: 0.3rem;
  background: transparent;
  border-bottom: 1px solid {c['card_border']};
  padding-bottom: 0;
}}
.stTabs [data-baseweb="tab"] {{
  background: transparent;
  border-radius: 10px 10px 0 0;
  border: 1px solid transparent;
  border-bottom: none;
  color: {c['muted']};
  font-size: 0.9rem;
  padding: 0.5rem 1rem;
  transition: all 0.15s;
}}
.stTabs [data-baseweb="tab"]:hover {{
  color: {c['white']};
  background: rgba(14,27,42,0.5);
}}
.stTabs [aria-selected="true"] {{
  background: rgba(214,168,79,0.1) !important;
  color: {c['gold']} !important;
  border-color: {c['card_border']} !important;
  border-bottom: 2px solid {c['gold']} !important;
  font-weight: 600 !important;
}}

/* ─── Buttons ─────────────────────────────────────────────── */
.stButton > button[kind="primary"] {{
  background: linear-gradient(135deg, #b5832a 0%, {c['gold']} 100%) !important;
  border: none !important;
  color: #07111F !important;
  font-weight: 700 !important;
  border-radius: 10px !important;
  padding: 0.5rem 1.4rem !important;
  letter-spacing: 0.03em;
  box-shadow: 0 4px 14px rgba(214,168,79,0.3);
  transition: all 0.2s ease;
}}
.stButton > button[kind="primary"]:hover {{
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(214,168,79,0.4) !important;
}}
.stButton > button:not([kind="primary"]) {{
  background: rgba(14,27,42,0.9) !important;
  border: 1px solid {c['card_border']} !important;
  color: {c['white']} !important;
  border-radius: 10px !important;
  transition: all 0.15s;
}}
.stButton > button:not([kind="primary"]):hover {{
  border-color: {c['gold']} !important;
  color: {c['gold']} !important;
}}
/* Download buttons */
.stDownloadButton > button {{
  background: rgba(22,163,106,0.12) !important;
  border: 1px solid rgba(22,163,106,0.4) !important;
  color: {c['green']} !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  font-size: 0.86rem !important;
}}
.stDownloadButton > button:hover {{
  background: rgba(22,163,106,0.22) !important;
  border-color: {c['green']} !important;
}}

/* ─── Select / input ──────────────────────────────────────── */
[data-baseweb="select"] > div,
[data-baseweb="input"] > div {{
  background: rgba(14,27,42,0.9) !important;
  border-color: {c['card_border']} !important;
  color: {c['white']} !important;
  border-radius: 8px !important;
}}
[data-baseweb="select"] svg {{ fill: {c['muted']} !important; }}

/* ─── Expanders ────────────────────────────────────────────── */
[data-testid="stExpander"] {{
  background: rgba(14,27,42,0.7);
  border: 1px solid {c['card_border']} !important;
  border-radius: 10px !important;
}}
[data-testid="stExpander"] summary {{
  color: {c['muted']} !important;
  font-size: 0.9rem !important;
}}
[data-testid="stExpander"] summary:hover {{
  color: {c['gold']} !important;
}}

/* ─── Alerts ──────────────────────────────────────────────── */
[data-testid="stAlert"] {{
  border-radius: 10px !important;
}}
[data-baseweb="notification"][kind="positive"] {{
  background: rgba(22,163,106,0.1) !important;
  border-color: rgba(22,163,106,0.35) !important;
}}
[data-baseweb="notification"][kind="warning"] {{
  background: rgba(245,158,11,0.08) !important;
  border-color: rgba(245,158,11,0.3) !important;
}}
[data-baseweb="notification"][kind="negative"] {{
  background: rgba(239,68,68,0.08) !important;
  border-color: rgba(239,68,68,0.3) !important;
}}

/* ─── Caption / small text ────────────────────────────────── */
.stCaption, .st-emotion-cache-0, small {{
  color: {c['muted_dark']} !important;
  font-size: 0.8rem !important;
}}

/* ─── Action card (homepage) ──────────────────────────────── */
.wc-action-card {{
  background: rgba(14,27,42,0.94);
  border: 1px solid {c['card_border']};
  border-radius: 14px;
  padding: 1.1rem 1.1rem 0.8rem 1.1rem;
  text-align: center;
  transition: transform 0.15s, border-color 0.15s;
  cursor: default;
}}
.wc-action-card:hover {{
  transform: translateY(-3px);
  border-color: {c['gold']};
}}
.wc-action-icon {{ font-size: 1.6rem; margin-bottom: 0.3rem; }}
.wc-action-title {{
  color: {c['white']};
  font-weight: 700;
  font-size: 0.95rem;
  margin-bottom: 0.2rem;
}}
.wc-action-hint {{
  color: {c['muted']};
  font-size: 0.78rem;
  line-height: 1.4;
}}

/* ─── Status dot ──────────────────────────────────────────── */
.wc-dot {{
  display: inline-block;
  width: 8px; height: 8px;
  border-radius: 50%;
  margin-right: 6px;
  vertical-align: middle;
}}
.wc-dot-ok     {{ background: {c['green']}; box-shadow: 0 0 6px {c['green']}; }}
.wc-dot-warn   {{ background: {c['warning']}; }}
.wc-dot-danger {{ background: {c['danger']}; }}
.wc-dot-muted  {{ background: {c['muted']}; }}


/* ─── Inputs (readable contrast) ─────────────────────────── */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea,
.stDateInput [data-baseweb="input"] input {{
  background-color: #1F1F1F !important;
  color: #F8F8F8 !important;
  border: 1px solid #8B0000 !important;
  border-radius: 8px !important;
}}
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {{
  color: #C0C0C0 !important;
}}
.stButton > button[kind="primary"] {{
  background: linear-gradient(135deg, #6d0000 0%, #8B0000 100%) !important;
  border: none !important;
  color: #F8F8F8 !important;
  box-shadow: 0 4px 14px rgba(139,0,0,0.35);
}}
.stButton > button[kind="primary"]:hover {{
  background: #A50000 !important;
  box-shadow: 0 8px 20px rgba(165,0,0,0.45) !important;
}}
.stDownloadButton > button {{
  background: #8B0000 !important;
  border: 1px solid #8B0000 !important;
  color: #F8F8F8 !important;
}}
.stDownloadButton > button:hover {{
  background: #A50000 !important;
  border-color: #A50000 !important;
}}
.wc-panel-warning {{
  background: #F59E0B !important;
  border: 1px solid #F59E0B !important;
  border-left: 4px solid #F59E0B !important;
  color: #0B0B0B !important;
}}
.wc-panel-success {{
  background: #16A36A !important;
  border: 1px solid #16A36A !important;
  border-left: 4px solid #16A36A !important;
  color: #F8F8F8 !important;
}}
.wc-panel-info {{
  background: #1F1F1F !important;
  border: 1px solid #16A36A !important;
  border-left: 4px solid #16A36A !important;
}}

/* ─── Divider ─────────────────────────────────────────────── */
hr {{ border-color: {c['card_border']} !important; opacity: 0.5; }}
</style>
        """,
        unsafe_allow_html=True,
    )
