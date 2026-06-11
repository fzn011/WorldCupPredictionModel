"""Reusable UI component exports."""

from app.components.ui import (
    inject_page_theme,
    render_data_quality_card,
    render_data_table,
    render_download_card,
    render_formation_diagram,
    render_hero,
    render_metric_card,
    render_pipeline_stepper,
    render_podium_cards,
    render_quick_nav_cards,
    render_section_header,
    render_status_badge,
    render_status_card,
    render_success_panel,
    render_warning_panel,
)

try:
    from app.components.ui import render_quick_nav_grid
except ImportError:
    render_quick_nav_grid = render_quick_nav_cards

__all__ = [
    "inject_page_theme",
    "render_data_quality_card",
    "render_data_table",
    "render_download_card",
    "render_formation_diagram",
    "render_hero",
    "render_metric_card",
    "render_pipeline_stepper",
    "render_podium_cards",
    "render_quick_nav_cards",
    "render_quick_nav_grid",
    "render_section_header",
    "render_status_badge",
    "render_status_card",
    "render_success_panel",
    "render_warning_panel",
]
