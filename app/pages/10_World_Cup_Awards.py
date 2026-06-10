"""Legacy Streamlit page — forwards to Step 18 World Cup Awards (page 17)."""

from __future__ import annotations

import streamlit as st

try:
    st.switch_page("pages/17_World_Cup_Awards.py")
except Exception:
    st.warning(
        "This page has moved to **17 World Cup Awards** (Step 18). "
        "Use the sidebar to open the updated awards page."
    )
    st.page_link("pages/17_World_Cup_Awards.py", label="Open Step 18 World Cup Awards", icon="🏆")
