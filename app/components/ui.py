"""Reusable Streamlit UI components — World Cup analytics command center."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Literal

import pandas as pd
import streamlit as st

try:
    from app.styles.worldcup_theme import COLORS, SPRINTURA_PAGE_TITLE_STYLE, inject_worldcup_css, render_themed_html
except ModuleNotFoundError:
    from styles.worldcup_theme import COLORS, SPRINTURA_PAGE_TITLE_STYLE, inject_worldcup_css, render_themed_html

BadgeKind = Literal["ok", "warn", "danger", "muted", "gold"]


def _esc(text: Any) -> str:
    return html.escape(str(text))


# ─── Theme injection ───────────────────────────────────────────────────────────

def inject_page_theme() -> None:
    """Apply global World Cup theme CSS to the current page."""
    inject_worldcup_css()


# ─── Hero ──────────────────────────────────────────────────────────────────────

def render_hero(
    title: str,
    subtitle: str,
    *,
    eyebrow: str = "FIFA World Cup 2026 Analytics",
) -> None:
    render_themed_html(
        f"""
<div class="wc-hero">
  <div class="wc-hero-eyebrow wc-page-eyebrow">{_esc(eyebrow)}</div>
  <h1 class="wc-page-title" style="{SPRINTURA_PAGE_TITLE_STYLE}">{_esc(title)}</h1>
  <p class="wc-page-subtitle">{_esc(subtitle)}</p>
</div>
        """
    )


# ─── Section header ────────────────────────────────────────────────────────────

def render_section_header(title: str, *, subtitle: str | None = None) -> None:
    st.markdown(
        f'<div class="wc-section"><h3 class="wc-section-title">{_esc(title)}</h3></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="wc-pitch-line"></div>', unsafe_allow_html=True)
    if subtitle:
        st.caption(subtitle)


# ─── Status badge ──────────────────────────────────────────────────────────────

def render_status_badge(label: str, kind: BadgeKind = "muted") -> str:
    """Return an HTML badge string (unsafe_allow_html caller's responsibility)."""
    return f'<span class="wc-badge wc-badge-{kind}">{_esc(label)}</span>'


# ─── Status dot ────────────────────────────────────────────────────────────────

def render_dot(kind: BadgeKind = "muted") -> str:
    return f'<span class="wc-dot wc-dot-{kind}"></span>'


# ─── Metric card ───────────────────────────────────────────────────────────────

def render_metric_card(
    label: str,
    value: str,
    *,
    sub: str | None = None,
    variant: str = "",
) -> None:
    """A dark glass card with label, bold value, and optional sub-text.

    variant can be 'ok', 'warn', 'danger', 'gold' or '' (default white).
    """
    if variant in ("gold", "accent"):
        variant = "accent"
    cls = f"wc-card wc-card-{variant}" if variant else "wc-card"
    sub_html = f'<div class="wc-card-sub">{_esc(sub)}</div>' if sub else ""
    st.markdown(
        f"""
<div class="{cls}">
  <div class="wc-card-label">{_esc(label)}</div>
  <div class="wc-card-value">{_esc(value)}</div>
  {sub_html}
</div>
        """,
        unsafe_allow_html=True,
    )


# ─── Status card ───────────────────────────────────────────────────────────────

def render_status_card(
    label: str,
    value: str,
    *,
    sub: str | None = None,
    badge: BadgeKind | None = None,
) -> None:
    badge_html = ""
    if badge:
        badge_html = (
            f'<div style="margin-top:0.5rem;">'
            f'{render_status_badge(value, badge)}'
            f'</div>'
        )
    st.markdown(
        f"""
<div class="wc-card">
  <div class="wc-card-label">{label}</div>
  <div class="wc-card-value">{value}</div>
  {f'<div class="wc-card-sub">{sub}</div>' if sub else ''}
  {badge_html}
</div>
        """,
        unsafe_allow_html=True,
    )


# ─── Progress bar ──────────────────────────────────────────────────────────────

def render_progress_bar(
    value: float,
    *,
    label: str = "",
    kind: BadgeKind = "gold",
) -> None:
    """Render a styled progress bar. value is 0.0–1.0."""
    pct = max(0, min(100, int(value * 100)))
    label_html = f'<div class="wc-card-label">{label}</div>' if label else ""
    st.markdown(
        f"""
{label_html}
<div class="wc-progress-wrap">
  <div class="wc-progress-fill wc-progress-fill-{kind}" style="width:{pct}%;"></div>
</div>
<div class="wc-card-sub" style="text-align:right;margin-top:0;">{pct}%</div>
        """,
        unsafe_allow_html=True,
    )


# ─── Data quality card ─────────────────────────────────────────────────────────

def render_data_quality_card(
    title: str,
    passed: bool,
    *,
    detail: str = "",
    progress: float | None = None,
) -> None:
    kind: BadgeKind = "ok" if passed else "warn"
    badge = render_status_badge("Ready" if passed else "Needs review", kind)
    prog_html = ""
    if progress is not None:
        pct = int(max(0, min(100, progress * 100)))
        fill_kind = "ok" if pct >= 90 else ("warn" if pct >= 50 else "danger")
        prog_html = f"""
<div class="wc-progress-wrap">
  <div class="wc-progress-fill wc-progress-fill-{fill_kind}" style="width:{pct}%;"></div>
</div>
<div class="wc-card-sub" style="text-align:right;margin-top:0;">{pct}%</div>"""
    st.markdown(
        f"""
<div class="wc-card">
  <div class="wc-card-label">{title}</div>
  <div style="margin:0.35rem 0;">{badge}</div>
  {prog_html}
  {f'<div class="wc-card-sub">{detail}</div>' if detail else ''}
</div>
        """,
        unsafe_allow_html=True,
    )


# ─── Readiness checklist row ───────────────────────────────────────────────────

def render_readiness_item(
    label: str,
    passed: bool,
    *,
    detail: str = "",
    warn: bool = False,
) -> None:
    """One horizontal row in a readiness checklist."""
    if passed:
        row_cls, icon_html = "wc-check-row-pass", render_status_badge("Pass", "ok")
    elif warn:
        row_cls, icon_html = "wc-check-row-warn", render_status_badge("Warning", "warn")
    else:
        row_cls, icon_html = "wc-check-row-fail", render_status_badge("Fail", "danger")
    detail_html = f'<span class="wc-check-detail">{detail}</span>' if detail else ""
    st.markdown(
        f"""
<div class="wc-check-row {row_cls}">
  <span class="wc-check-label">{label}</span>
  {detail_html}
  {icon_html}
</div>
        """,
        unsafe_allow_html=True,
    )


# ─── Warning / success panels ──────────────────────────────────────────────────

def render_warning_panel(message: str) -> None:
    st.markdown(f'<div class="wc-panel-warning">{message}</div>', unsafe_allow_html=True)


def render_success_panel(message: str) -> None:
    st.markdown(f'<div class="wc-panel-success">{message}</div>', unsafe_allow_html=True)


def render_info_panel(message: str) -> None:
    st.markdown(f'<div class="wc-panel-info">{message}</div>', unsafe_allow_html=True)


def render_error_panel(message: str) -> None:
    st.markdown(f'<div class="wc-panel-error">{message}</div>', unsafe_allow_html=True)


# ─── Pipeline stepper ──────────────────────────────────────────────────────────

def render_pipeline_stepper(steps: list[tuple[str, str, str]]) -> None:
    """Render numbered demo flow steps: (number, title, description)."""
    for num, title, desc in steps:
        st.markdown(
            f"""
<div class="wc-step">
  <span class="wc-step-num">{num}</span>
  <span><strong style="color:{COLORS['white']}">{title}</strong>
  <span style="color:{COLORS['muted']}"> — {desc}</span></span>
</div>
            """,
            unsafe_allow_html=True,
        )


def render_quick_nav_grid(items: list[dict[str, str]]) -> None:
    """Product action cards with clear CTA buttons (no emoji icons)."""
    render_action_grid(items)


def render_action_grid(items: list[dict[str, str]]) -> None:
    """Dashboard action cards — title, description, page link button."""
    cols = st.columns(min(len(items), 3))
    for idx, item in enumerate(items):
        with cols[idx % len(cols)]:
            render_action_card(
                item.get("title", ""),
                item.get("hint", ""),
                button_label=item.get("button") or f"Open {item.get('title', 'page')}",
                page=item.get("page"),
            )


def render_action_card(
    title: str,
    description: str,
    *,
    button_label: str | None = None,
    page: str | None = None,
    status: str = "neutral",
) -> None:
    """Single clickable-style dashboard card with optional navigation button."""
    status_cls = f" wc-card-{status}" if status in ("ok", "warn", "danger", "accent") else ""
    st.markdown(
        f"""
<div class="wc-action-card{status_cls}">
  <div class="wc-action-title">{_esc(title)}</div>
  <div class="wc-action-hint">{_esc(description)}</div>
</div>
        """,
        unsafe_allow_html=True,
    )
    if page and button_label:
        try:
            from app.components.layout import navigate_to as _navigate_to
        except ModuleNotFoundError:
            from components.layout import navigate_to as _navigate_to
        st.button(
            button_label,
            use_container_width=True,
            key=f"nav_{page}_{title}",
            on_click=_navigate_to,
            kwargs={"page": page},
        )


# ─── Quick nav cards (legacy) ──────────────────────────────────────────────────

def render_quick_nav_cards(items: list[dict[str, str]]) -> None:
    """Quick-link action cards. Each item: title, hint, page (sidebar link)."""
    icons = ["⚽", "📊", "🏆", "🥇", "📋", "✓"]
    cols = st.columns(min(len(items), 3))
    for idx, item in enumerate(items):
        with cols[idx % len(cols)]:
            icon = item.get("icon", icons[idx % len(icons)])
            st.markdown(
                f"""
<div class="wc-action-card">
  <div class="wc-action-icon">{icon}</div>
  <div class="wc-action-title">{item.get('title', '')}</div>
  <div class="wc-action-hint">{item.get('hint', '')}</div>
</div>
                """,
                unsafe_allow_html=True,
            )
            if item.get("page"):
                page_name = item["page"]
                if page_name.startswith("pages/"):
                    legacy = {
                        "pages/1_Match_Predictor.py": "Match Predictor",
                        "pages/9_Monte_Carlo_Simulator.py": "Tournament Forecast",
                        "pages/17_World_Cup_Awards.py": "World Cup Awards",
                        "pages/4_Reports_Downloads.py": "Reports",
                        "pages/3_Data_Health.py": "Data Quality",
                    }
                    page_name = legacy.get(page_name, page_name)
                try:
                    from app.components.layout import navigate_to as _navigate_to
                except ModuleNotFoundError:
                    from components.layout import navigate_to as _navigate_to
                st.button(
                    f"Open {item.get('title', 'page')}",
                    use_container_width=True,
                    key=f"legacy_nav_{idx}",
                    on_click=_navigate_to,
                    kwargs={"page": page_name},
                )


# ─── Data table ────────────────────────────────────────────────────────────────

def _default_table_height(row_count: int, *, row_height: int = 35, header: int = 38, cap: int = 640) -> int:
    return min(cap, header + row_height * max(row_count, 1) + 8)


def render_data_table(
    df: pd.DataFrame,
    *,
    height: int | None = None,
    hide_index: bool = True,
    interactive: bool = False,
    max_static_rows: int = 500,
    **kwargs: Any,
) -> None:
    """Render tabular data with readable dark-theme styling.

    Uses static ``st.table`` by default (reliable in tabs). Falls back to
    ``st.dataframe`` only for large or explicitly interactive tables.
    """
    _ = kwargs  # absorb legacy st.dataframe kwargs (use_container_width, etc.)
    if df.empty:
        st.info("No data available.")
        return

    display = df.reset_index(drop=True) if hide_index else df

    if not interactive and len(display) <= max_static_rows:
        st.table(display)
        return

    table_height = height if height is not None else _default_table_height(len(display))
    st.dataframe(display, use_container_width=True, hide_index=hide_index, height=table_height)


# ─── Download card ─────────────────────────────────────────────────────────────

def render_download_card(
    title: str,
    description: str,
    path: Path,
    *,
    file_name: str | None = None,
    mime: str = "text/csv",
) -> None:
    fname = file_name or path.name
    st.markdown(
        f"""
<div class="wc-download-card">
  <div class="wc-card-label">{_esc(title)}</div>
  <div class="wc-card-sub">{_esc(description)}</div>
  <div class="wc-filename-muted">{_esc(fname)}</div>
</div>
        """,
        unsafe_allow_html=True,
    )
    if path.is_file():
        st.download_button(
            label="Download",
            data=path.read_bytes(),
            file_name=fname,
            mime=mime,
            use_container_width=False,
            type="secondary",
            key=f"dl_{abs(hash(title + str(path)))}",
        )
    else:
        st.caption("Not available yet")


# ─── Formation diagram ─────────────────────────────────────────────────────────

_FORMATION_ROWS: tuple[tuple[str, int], ...] = (
    ("FWD", 3),
    ("MID", 3),
    ("DEF", 4),
    ("GK", 1),
)


def _clean_display_token(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    token = str(value).strip()
    if not token or token.lower() in {"nan", "none", "nat"}:
        return ""
    return token


def _formation_player_payload(row: pd.Series, name_col: str) -> dict[str, str]:
    name = ""
    for col in (name_col, "player_name", "player"):
        name = _clean_display_token(row.get(col))
        if name:
            break
    if not name:
        name = "—"

    team = _clean_display_token(row.get("team"))
    position = _clean_display_token(row.get("position_code")) or _clean_display_token(row.get("position"))
    if position and len(position) > 3:
        position = position.title()
    meta = " · ".join(part for part in (team, position) if part)
    slot = _clean_display_token(row.get("formation_slot"))
    return {"name": name, "meta": meta, "slot": slot}


def _pitch_lines_from_slots(players_df: pd.DataFrame, name_col: str) -> list[list[dict[str, str]]]:
    if players_df.empty or "formation_slot" not in players_df.columns:
        return []

    slot_map = {
        str(row["formation_slot"]): _formation_player_payload(row, name_col)
        for _, row in players_df.iterrows()
        if _clean_display_token(row.get("formation_slot"))
    }
    if not slot_map:
        return []

    lines: list[list[dict[str, str]]] = []
    for prefix, count in _FORMATION_ROWS:
        line: list[dict[str, str]] = []
        for index in range(1, count + 1):
            slot_key = f"{prefix}{index}"
            line.append(slot_map.get(slot_key, {"name": "—", "meta": "", "slot": slot_key}))
        lines.append(line)
    return lines


def _pitch_lines_from_positions(players_df: pd.DataFrame, name_col: str) -> list[list[dict[str, str]]]:
    buckets: dict[str, list[dict[str, str]]] = {"FWD": [], "MID": [], "DEF": [], "GK": []}
    for _, row in players_df.iterrows():
        payload = _formation_player_payload(row, name_col)
        group = _clean_display_token(row.get("position_group")).lower()
        position = _clean_display_token(row.get("position")).lower()
        code = _clean_display_token(row.get("position_code")).upper()
        if "forward" in group or position.startswith("forward") or code.startswith("FW"):
            buckets["FWD"].append(payload)
        elif "mid" in group or "midfield" in position or code.startswith("MF"):
            buckets["MID"].append(payload)
        elif "goal" in group or "keeper" in position or code == "GK":
            buckets["GK"].append(payload)
        else:
            buckets["DEF"].append(payload)

    return [buckets["FWD"], buckets["MID"], buckets["DEF"], buckets["GK"]]


def _render_pitch_player_card(player: dict[str, str]) -> str:
    slot = player.get("slot", "")
    badge = ""
    if slot:
        badge_label = slot.replace("FWD", "FW").replace("DEF", "DF").replace("MID", "MF")
        badge = f'<span class="wc-pitch-player-badge">{_esc(badge_label)}</span>'
    meta_html = (
        f'<div class="wc-pitch-player-meta">{_esc(player.get("meta", ""))}</div>'
        if player.get("meta")
        else ""
    )
    return (
        f'<div class="wc-pitch-player">{badge}'
        f'<div class="wc-pitch-player-name">{_esc(player.get("name", "—"))}</div>'
        f"{meta_html}</div>"
    )


def render_formation_pitch(players_by_line: list[list[dict[str, str]]]) -> None:
    """Render a 4-3-3 lineup as player cards on a stylized pitch."""
    if not players_by_line:
        render_empty_state("Formation", "Team lineup not available yet.")
        return

    rows_html = "".join(
        f'<div class="wc-pitch-row">{"".join(_render_pitch_player_card(player) for player in line)}</div>'
        for line in players_by_line
        if line
    )
    if not rows_html:
        render_empty_state("Formation", "Team lineup not available yet.")
        return

    render_themed_html(
        f"""
<div class="wc-pitch">
  <div class="wc-pitch-header">4-3-3 formation</div>
  {rows_html}
</div>
        """
    )


def render_formation_diagram(players_by_line: list[list[str]]) -> None:
    """Backward-compatible string lineup renderer (plain text fallback)."""
    if not players_by_line:
        render_empty_state("Formation", "Team lineup not available yet.")
        return
    rich_lines = [
        [{"name": name, "meta": "", "slot": ""} for name in row]
        for row in players_by_line
    ]
    render_formation_pitch(rich_lines)


def render_team_formation(players_df: pd.DataFrame, *, name_col: str = "player_name") -> None:
    """Render Team of the Tournament XI on a pitch grid with player cards."""
    if players_df.empty:
        render_empty_state("Formation", "Team lineup not available yet.")
        return

    lines = _pitch_lines_from_slots(players_df, name_col)
    if not lines or all(player.get("name") == "—" for row in lines for player in row):
        lines = _pitch_lines_from_positions(players_df, name_col)
    render_formation_pitch(lines)


# ─── Podium cards ──────────────────────────────────────────────────────────────

def render_podium_cards(
    df: pd.DataFrame,
    *,
    rank_col: str,
    name_col: str,
    team_col: str = "team",
    score_col: str | None = None,
    award_labels: dict[int, str] | None = None,
) -> None:
    if df.empty:
        st.info("No podium data yet.")
        return
    labels = award_labels or {1: "Gold", 2: "Silver", 3: "Bronze"}
    podium_extra = {1: "wc-podium-1", 2: "wc-podium-2", 3: "wc-podium-3"}
    top = df.sort_values(rank_col).head(3)
    cols = st.columns(3)
    for i, (_, row) in enumerate(top.iterrows()):
        rank = int(row.get(rank_col, i + 1))
        medal = labels.get(rank, "—")
        score = ""
        if score_col and score_col in row:
            try:
                score = (
                    f"{float(row[score_col]):.2%}"
                    if "prob" in score_col
                    else f"{float(row[score_col]):.3g}"
                )
            except (TypeError, ValueError):
                score = str(row[score_col])
        extra_cls = podium_extra.get(rank, "")
        with cols[i]:
            sub = f"{row.get(team_col, '')}{'  ·  ' + score if score else ''}".strip()
            st.markdown(
                f"""
<div class="wc-card {extra_cls}">
  <div class="wc-card-label">{medal}</div>
  <div class="wc-card-value" style="font-size:1.1rem;">{row.get(name_col, '—')}</div>
  {f'<div class="wc-card-sub">{sub}</div>' if sub else ''}
</div>
                """,
                unsafe_allow_html=True,
            )


# ─── Champion spotlight ────────────────────────────────────────────────────────

def render_champion_spotlight(team: str, probability: float, *, sub: str = "") -> None:
    """Large featured card for the Monte Carlo top champion."""
    pct = f"{probability:.1%}"
    st.markdown(
        f"""
<div class="wc-card wc-card-gold" style="text-align:center;padding:1.5rem 1rem;">
  <div class="wc-card-label" style="font-size:0.7rem;letter-spacing:0.15em;">
    Most likely champion
  </div>
  <div class="wc-card-value" style="font-size:1.9rem;color:{COLORS['primary']};">{team}</div>
  <div style="font-size:1.25rem;font-weight:700;color:{COLORS['primary_hover']};margin-top:0.2rem;">{pct}</div>
  {f'<div class="wc-card-sub">{sub}</div>' if sub else ''}
</div>
        """,
        unsafe_allow_html=True,
    )


# ─── Helpers ───────────────────────────────────────────────────────────────────

def load_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


# ─── Step 20C product aliases ──────────────────────────────────────────────────

inject_global_theme = inject_page_theme


def render_page_header(title: str, subtitle: str | None = None, *, eyebrow: str | None = None) -> None:
    render_hero(title, subtitle or "", eyebrow=eyebrow or "World Cup 2026 Analytics")


def render_section(title: str, *, subtitle: str | None = None) -> None:
    render_section_header(title, subtitle=subtitle)


def render_clean_table(
    df: pd.DataFrame,
    *,
    title: str | None = None,
    max_rows: int = 20,
) -> None:
    if title:
        render_section_header(title)
    if df.empty:
        render_empty_state("No data", "Nothing to display yet.")
        return
    render_data_table(df.head(max_rows), hide_index=True)


def render_empty_state(title: str, message: str) -> None:
    st.markdown(
        f"""
<div class="wc-empty-state">
  <div class="wc-action-title">{_esc(title)}</div>
  <div class="wc-action-hint">{_esc(message)}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_app_footer(
    *,
    author_name: str = "Faiaz Zahin",
    author_url: str = "https://fzn011.github.io/portfolio/",
    year: int = 2026,
) -> None:
    """Site-wide footer with portfolio link."""
    st.markdown(
        f"""
<footer class="wc-app-footer">
  <p>© {year} All rights reserved by
    <a href="{_esc(author_url)}" target="_blank" rel="noopener noreferrer">{_esc(author_name)}</a>
  </p>
</footer>
        """,
        unsafe_allow_html=True,
    )

