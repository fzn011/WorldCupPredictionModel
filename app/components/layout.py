"""App shell, stable sidebar navigation, and page frame for consistent routing."""

from __future__ import annotations

import importlib.util
import sys
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path

import streamlit as st

_APP_DIR = Path(__file__).resolve().parents[1]
_REPO_ROOT = _APP_DIR.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

MAIN_PAGES: list[str] = [
    "Home",
    "Match Predictor",
    "Tournament Forecast",
    "World Cup Awards",
    "Reports",
    "Data Quality",
]

ADMIN_PAGES: list[str] = [
    "Quick Simulation",
    "Official Data Health",
    "Squads Health",
    "Data Import Tools",
    "Source Import Tools",
    "Import Completion",
    "Tournament Setup",
    "Group Stage Simulation",
    "Knockout Simulation",
    "Full Tournament Run",
    "Model Explanation",
]

PAGE_FILES: dict[str, str] = {
    "Match Predictor": "views/1_Match_Predictor.py",
    "Tournament Forecast": "views/9_Monte_Carlo_Simulator.py",
    "World Cup Awards": "views/17_World_Cup_Awards.py",
    "Reports": "views/4_Reports_Downloads.py",
    "Data Quality": "views/3_Data_Health.py",
    "Quick Simulation": "views/2_Tournament_Simulator.py",
    "Official Data Health": "views/_dev/11_Official_Data_Health.py",
    "Squads Health": "views/_dev/12_Official_Squads_Health.py",
    "Data Import Tools": "views/_dev/14_Official_Data_Population.py",
    "Source Import Tools": "views/_dev/15_Source_Assisted_Population.py",
    "Import Completion": "views/_dev/16_Official_Data_Population_Completion.py",
    "Tournament Setup": "views/_dev/5_Tournament_Setup.py",
    "Group Stage Simulation": "views/_dev/6_Group_Stage_Simulation.py",
    "Knockout Simulation": "views/_dev/7_Knockout_Simulation.py",
    "Full Tournament Run": "views/_dev/8_Full_Tournament_Run.py",
    "Model Explanation": "views/_dev/4_Model_Explanation.py",
}

_SESSION_ACTIVE = "active_page"
_SESSION_ADVANCED = "show_advanced_tools"
_NAV_RADIO_KEY = "wc_sidebar_nav_radio"
_RENDERER_CACHE: dict[str, tuple[int, Callable[[], None]]] = {}


def _init_session() -> None:
    if _SESSION_ACTIVE not in st.session_state:
        st.session_state[_SESSION_ACTIVE] = "Home"
    if _SESSION_ADVANCED not in st.session_state:
        st.session_state[_SESSION_ADVANCED] = False
    if _NAV_RADIO_KEY not in st.session_state:
        st.session_state[_NAV_RADIO_KEY] = "Home"


def _nav_options() -> list[str]:
    options = list(MAIN_PAGES)
    if st.session_state.get(_SESSION_ADVANCED):
        options.extend(ADMIN_PAGES)
    return options


def _normalize_page(page: str, options: list[str]) -> str:
    return page if page in options else "Home"


def _prepare_nav_state(page: str) -> str:
    """Update nav state before widgets render (safe to touch widget keys)."""
    _init_session()
    options = _nav_options()
    page = _normalize_page(page, options)
    st.session_state[_SESSION_ACTIVE] = page
    st.session_state[_NAV_RADIO_KEY] = page
    return page


def navigate_to(page: str) -> None:
    """Switch active page and rerun — use via on_click callbacks."""
    _init_session()
    if page not in MAIN_PAGES and page not in ADMIN_PAGES:
        st.warning(f"Unknown page: {page}")
        return
    if page in ADMIN_PAGES and not st.session_state[_SESSION_ADVANCED]:
        st.warning("Enable Advanced tools in the sidebar to open this page.")
        return
    if st.session_state[_SESSION_ACTIVE] == page:
        return
    _prepare_nav_state(page)
    st.rerun()


@contextmanager
def open_page_frame() -> Iterator[None]:
    """Stable min-height container to prevent blank layout during reruns."""
    with st.container():
        yield


def render_page_frame(title: str, subtitle: str | None = None):
    """Back-compat alias for open_page_frame()."""
    return open_page_frame()


def _load_renderer(page_name: str) -> Callable[[], None]:
    rel = PAGE_FILES.get(page_name)
    if not rel:
        raise KeyError(f"No page file registered for {page_name!r}")

    path = _APP_DIR / rel
    mtime_ns = path.stat().st_mtime_ns if path.is_file() else 0
    cached = _RENDERER_CACHE.get(page_name)
    if cached is not None and cached[0] == mtime_ns:
        return cached[1]

    mod_name = f"wc_page_{page_name.replace(' ', '_').lower()}"
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load page module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    renderer = getattr(module, "render_page", None)
    if renderer is None or not callable(renderer):
        raise AttributeError(f"{path} must define render_page()")
    _RENDERER_CACHE[page_name] = (mtime_ns, renderer)
    return renderer


def render_sidebar_navigation(*, home_renderer: Callable[[], None] | None = None) -> str:
    """Sidebar radio navigation; returns finalized active page name."""
    _init_session()
    try:
        from app.components.branding import render_sidebar_brand
    except ModuleNotFoundError:
        from components.branding import render_sidebar_brand

    render_sidebar_brand(tagline="AI Predictor")

    show_advanced = st.checkbox(
        "Advanced tools",
        value=bool(st.session_state[_SESSION_ADVANCED]),
        help="Show developer and diagnostic pages.",
        key="wc_advanced_tools_toggle",
    )
    st.session_state[_SESSION_ADVANCED] = show_advanced

    options = _nav_options()
    active = _normalize_page(st.session_state[_SESSION_ACTIVE], options)

    if active != st.session_state[_SESSION_ACTIVE]:
        _prepare_nav_state(active)
    elif st.session_state.get(_NAV_RADIO_KEY) not in options:
        _prepare_nav_state(active)

    selected = st.radio(
        "Navigation",
        options=options,
        label_visibility="collapsed",
        key=_NAV_RADIO_KEY,
    )

    # After the radio exists, only update active_page — never the widget key.
    if selected != st.session_state[_SESSION_ACTIVE]:
        st.session_state[_SESSION_ACTIVE] = _normalize_page(selected, options)
        st.rerun()

    return st.session_state[_SESSION_ACTIVE]


def render_app_shell(home_renderer: Callable[[], None]) -> None:
    """Full app: sidebar navigation + main content (no mixed routing)."""
    with st.sidebar:
        active = render_sidebar_navigation()
    try:
        if active == "Home":
            with open_page_frame():
                home_renderer()
        else:
            renderer = _load_renderer(active)
            with open_page_frame():
                renderer()
    except Exception as exc:
        st.error(f"Unable to load {active!r}. Check the terminal for details.")
        st.exception(exc)


# Back-compat alias used in tests
def _set_active_page(page: str) -> str:
    return _prepare_nav_state(page)
