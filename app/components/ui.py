"""Reusable Streamlit UI components — unified blood-red theme."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import pandas as pd
import streamlit as st

from app.styles.worldcup_theme import COLORS, inject_worldcup_css

BadgeKind = Literal["ok", "warn", "danger", "muted"]


def inject_page_theme() -> None:
    """Apply global theme CSS to the current page."""
    inject_worldcup_css()


def render_hero(title: str, subtitle: str, *, eyebrow: str = "FIFA World Cup 2026 AI Predictor") -> None:
    st.markdown(
        f"""
<div class="wc-hero">
  <div class="wc-hero-eyebrow">{eyebrow}</div>
  <h1>{title}</h1>
  <p>{subtitle}</p>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str, *, subtitle: str | None = None) -> None:
    st.markdown(f'<div class="wc-section"><h3>{title}</h3></div>', unsafe_allow_html=True)
    if subtitle:
        st.caption(subtitle)
    st.markdown('<div class="wc-pitch-line"></div>', unsafe_allow_html=True)


def render_status_badge(label: str, kind: BadgeKind = "muted") -> str:
    return f'<span class="wc-badge wc-badge-{kind}">{label}</span>'


def render_metric_card(
    label: str,
    value: str,
    *,
    sub: str | None = None,
    accent_value: bool = False,
) -> None:
    value_class = "wc-card-value wc-card-value-accent" if accent_value else "wc-card-value"
    sub_html = f'<div class="wc-card-sub">{sub}</div>' if sub else ""
    st.markdown(
        f"""
<div class="wc-card">
  <div class="wc-card-label">{label}</div>
  <div class="{value_class}">{value}</div>
  {sub_html}
</div>
        """,
        unsafe_allow_html=True,
    )


def render_status_card(
    label: str,
    value: str,
    *,
    sub: str | None = None,
    badge: BadgeKind | None = None,
) -> None:
    badge_html = ""
    if badge:
        badge_label = {"ok": "Ready", "warn": "Attention", "danger": "Blocked", "muted": "N/A"}.get(badge, value)
        badge_html = f'<div style="margin-top:0.45rem;">{render_status_badge(badge_label, badge)}</div>'
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


def render_warning_panel(message: str) -> None:
    st.markdown(f'<div class="wc-panel-warning">{message}</div>', unsafe_allow_html=True)


def render_success_panel(message: str) -> None:
    st.markdown(f'<div class="wc-panel-success">{message}</div>', unsafe_allow_html=True)


def render_error_panel(message: str) -> None:
    st.markdown(f'<div class="wc-panel-error">{message}</div>', unsafe_allow_html=True)


def render_info_panel(message: str) -> None:
    st.markdown(f'<div class="wc-panel-info">{message}</div>', unsafe_allow_html=True)


def render_pipeline_stepper(steps: list[tuple[str, str, str]]) -> None:
    """Render flow steps: (number, title, description)."""
    for num, title, desc in steps:
        st.markdown(
            f'<div class="wc-step"><span class="wc-step-num">{num}.</span><strong>{title}</strong> — {desc}</div>',
            unsafe_allow_html=True,
        )


def render_quick_nav_cards(items: list[dict[str, str]]) -> None:
    cols = st.columns(min(len(items), 4))
    for idx, item in enumerate(items):
        with cols[idx % len(cols)]:
            st.markdown(
                f"""
<div class="wc-card">
  <div class="wc-card-label">{item.get('label', 'Open')}</div>
  <div class="wc-card-value" style="font-size:1rem;">{item.get('title', '')}</div>
  <div class="wc-card-sub">{item.get('hint', '')}</div>
</div>
                """,
                unsafe_allow_html=True,
            )
            if item.get("page"):
                st.page_link(item["page"], label=f"Open {item.get('title', 'page')}")


def render_action_cards(items: list[dict[str, str]]) -> None:
    cols = st.columns(min(len(items), 3))
    for idx, item in enumerate(items):
        with cols[idx % len(cols)]:
            st.markdown(
                f"""
<div class="wc-card">
  <div class="wc-card-value" style="font-size:1.05rem;">{item.get('title', '')}</div>
  <div class="wc-card-sub">{item.get('description', '')}</div>
</div>
                """,
                unsafe_allow_html=True,
            )
            if item.get("page"):
                st.page_link(item["page"], label=item.get("button", "Open"), use_container_width=True)


def render_data_table(
    df: pd.DataFrame,
    *,
    height: int | None = None,
    hide_index: bool = True,
) -> None:
    if df.empty:
        render_info_panel("No data available.")
        return
    kwargs: dict[str, Any] = {"use_container_width": True, "hide_index": hide_index}
    if height is not None:
        kwargs["height"] = height
    st.dataframe(df, **kwargs)


def render_download_card(
    title: str,
    description: str,
    path: Path,
    *,
    file_name: str | None = None,
    mime: str = "text/csv",
) -> None:
    st.markdown(
        f"""
<div class="wc-download-card">
  <div class="wc-card-label">{title}</div>
  <div class="wc-card-value" style="font-size:1rem;">{description}</div>
</div>
        """,
        unsafe_allow_html=True,
    )
    if path.is_file():
        st.download_button(
            label=f"Download {file_name or path.name}",
            data=path.read_bytes(),
            file_name=file_name or path.name,
            mime=mime,
            use_container_width=True,
            type="primary",
        )
    else:
        st.caption("Not generated yet")


def render_data_quality_card(
    title: str,
    passed: bool,
    *,
    detail: str = "",
    progress: float | None = None,
) -> None:
    kind: BadgeKind = "ok" if passed else "danger"
    badge = render_status_badge("Passed" if passed else "Needs attention", kind)
    prog_html = ""
    if progress is not None:
        pct = int(max(0, min(100, progress * 100)))
        prog_html = f'<div class="wc-card-sub">Completion: {pct}%</div>'
    st.markdown(
        f"""
<div class="wc-card">
  <div class="wc-card-label">{title}</div>
  <div>{badge}</div>
  {prog_html}
  {f'<div class="wc-card-sub">{detail}</div>' if detail else ''}
</div>
        """,
        unsafe_allow_html=True,
    )


def render_formation_diagram(players_by_line: list[list[str]]) -> None:
    lines: list[str] = []
    for row in players_by_line:
        lines.append("    ".join(row))
    body = "\n".join(lines)
    st.markdown(f'<pre class="wc-formation">{body}</pre>', unsafe_allow_html=True)


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
        render_info_panel("No podium data yet.")
        return
    labels = award_labels or {1: "Gold", 2: "Silver", 3: "Bronze"}
    top = df.sort_values(rank_col).head(3)
    cols = st.columns(3)
    for i, (_, row) in enumerate(top.iterrows()):
        medal = labels.get(int(row.get(rank_col, i + 1)), "—")
        score = ""
        if score_col and score_col in row:
            try:
                score = f"{float(row[score_col]):.2%}" if "prob" in score_col else f"{float(row[score_col]):.3g}"
            except (TypeError, ValueError):
                score = str(row[score_col])
        with cols[i]:
            render_metric_card(
                medal,
                str(row.get(name_col, "—")),
                sub=f"{row.get(team_col, '')} {('· ' + score) if score else ''}".strip(),
                accent_value=True,
            )


def load_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    import json

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
