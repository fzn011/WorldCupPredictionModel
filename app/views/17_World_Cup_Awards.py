"""Streamlit page: FIFA World Cup 2026 Awards Predictor."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
APP_DIR = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

try:
    from app.streamlit_paths import OFFICIAL_PROCESSED_DIR, PROCESSED_DATA_DIR, PROJECT_ROOT, REPORTS_DIR
except ModuleNotFoundError:
    from streamlit_paths import OFFICIAL_PROCESSED_DIR, PROCESSED_DATA_DIR, PROJECT_ROOT, REPORTS_DIR

try:
    from app.components.layout import navigate_to
except ModuleNotFoundError:
    from components.layout import navigate_to

try:
    from app.components.ui import (
        render_data_table,
        render_download_card,
        render_empty_state,
        render_hero,
        render_metric_card,
        render_podium_cards,
        render_section_header,
        render_status_badge,
        render_team_formation,
    )
except ModuleNotFoundError:
    from components.ui import (
        render_data_table,
        render_download_card,
        render_empty_state,
        render_hero,
        render_metric_card,
        render_podium_cards,
        render_section_header,
        render_status_badge,
        render_team_formation,
    )

try:
    from app.product_status import load_product_data_status
except ModuleNotFoundError:
    from product_status import load_product_data_status

from src.awards.award_data import resolve_player_sort_column  # noqa: E402
from src.awards.manual_priors import resolve_manual_prior_file  # noqa: E402
from src.awards.prior_enrichment import create_enriched_player_priors, merge_enriched_priors_into_award_candidates  # noqa: E402
from src.awards.prepare_awards import prepare_step18_world_cup_awards  # noqa: E402
import src.utils.constants as C  # noqa: E402

AWARDS_ANALYTICS_DISCLAIMER = str(getattr(C, "AWARDS_ANALYTICS_DISCLAIMER", "Analytics estimate only."))
MANUAL_PRIOR_DISCLAIMER = str(getattr(C, "MANUAL_PRIOR_DISCLAIMER", "Manual priors are optional user-provided adjustments."))

MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE = getattr(
    C, "MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE", "monte_carlo_team_stage_probabilities.csv"
)
WORLD_CUP_AWARDS_PREDICTIONS_FILE = getattr(C, "WORLD_CUP_AWARDS_PREDICTIONS_FILE", "world_cup_awards_predictions.csv")
GOLDEN_BALL_PREDICTIONS_FILE = getattr(C, "GOLDEN_BALL_PREDICTIONS_FILE", "golden_ball_predictions.csv")
GOLDEN_BOOT_PREDICTIONS_FILE = getattr(C, "GOLDEN_BOOT_PREDICTIONS_FILE", "golden_boot_predictions.csv")
GOLDEN_GLOVE_PREDICTIONS_FILE = getattr(C, "GOLDEN_GLOVE_PREDICTIONS_FILE", "golden_glove_predictions.csv")
YOUNG_PLAYER_PREDICTIONS_FILE = getattr(C, "YOUNG_PLAYER_PREDICTIONS_FILE", "young_player_predictions.csv")
FAIR_PLAY_PREDICTIONS_FILE = getattr(C, "FAIR_PLAY_PREDICTIONS_FILE", "fair_play_predictions.csv")
MOST_ENTERTAINING_TEAM_PREDICTIONS_FILE = getattr(
    C, "MOST_ENTERTAINING_TEAM_PREDICTIONS_FILE", "most_entertaining_team_predictions.csv"
)
TEAM_OF_THE_TOURNAMENT_FILE = getattr(C, "TEAM_OF_THE_TOURNAMENT_FILE", "team_of_the_tournament.csv")
PLAYER_OF_THE_MATCH_PROXY_FILE = getattr(C, "PLAYER_OF_THE_MATCH_PROXY_FILE", "player_of_the_match_proxy.csv")
GOAL_OF_THE_TOURNAMENT_PROXY_FILE = getattr(
    C, "GOAL_OF_THE_TOURNAMENT_PROXY_FILE", "goal_of_the_tournament_proxy.csv"
)
WORLD_CUP_AWARDS_SUMMARY_FILE = getattr(C, "WORLD_CUP_AWARDS_SUMMARY_FILE", "world_cup_awards_summary.json")
WORLD_CUP_AWARDS_VALIDATION_REPORT_FILE = getattr(
    C, "WORLD_CUP_AWARDS_VALIDATION_REPORT_FILE", "world_cup_awards_validation_report.csv"
)
WORLD_CUP_AWARDS_REPORT_FILE = getattr(C, "WORLD_CUP_AWARDS_REPORT_FILE", "world_cup_awards_report.md")

_SESSION_AWARDS_NOTICE = "awards_action_notice"


def _load_csv(file_name: str) -> pd.DataFrame:
    path = PROCESSED_DATA_DIR / file_name
    return pd.read_csv(path) if path.is_file() else pd.DataFrame()


def _load_json(file_name: str) -> dict:
    path = PROCESSED_DATA_DIR / file_name
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _player_col(df: pd.DataFrame) -> str:
    if df.empty:
        return "player_name"
    try:
        return resolve_player_sort_column(df)
    except KeyError:
        return "player_name"


def _leader_from_df(df: pd.DataFrame, rank_col: str, name_col: str) -> str:
    if df.empty or rank_col not in df.columns:
        return ""
    top = df.sort_values(rank_col).head(1)
    if top.empty:
        return ""
    return str(top.iloc[0].get(name_col, ""))


def _awards_outputs_exist() -> bool:
    summary = _load_json(WORLD_CUP_AWARDS_SUMMARY_FILE)
    if summary:
        return True
    return any(
        (PROCESSED_DATA_DIR / f).is_file()
        for f in (
            GOLDEN_BALL_PREDICTIONS_FILE,
            GOLDEN_BOOT_PREDICTIONS_FILE,
            GOLDEN_GLOVE_PREDICTIONS_FILE,
            YOUNG_PLAYER_PREDICTIONS_FILE,
            TEAM_OF_THE_TOURNAMENT_FILE,
        )
    )


def _pop_awards_notice() -> dict | None:
    notice = st.session_state.pop(_SESSION_AWARDS_NOTICE, None)
    return notice if isinstance(notice, dict) else None


def _show_awards_notice() -> None:
    notice = _pop_awards_notice()
    if not notice:
        return
    level = notice.get("level", "info")
    message = notice.get("message", "")
    if level == "success":
        st.success(message)
    elif level == "error":
        st.error(message)
    elif level == "warning":
        st.warning(message)
    else:
        st.info(message)
    if notice.get("details") is not None:
        with st.expander("Action details"):
            st.json(notice["details"])


def _run_awards_generation(*, use_enriched: bool = False, use_manual: bool = False, manual_prior_file=None) -> None:
    with st.spinner("Generating World Cup awards predictions…"):
        try:
            kwargs: dict = {}
            if use_enriched:
                kwargs["use_enriched_candidates"] = True
            if use_manual:
                kwargs["use_enriched_candidates"] = True
                kwargs["use_manual_priors"] = True
                kwargs["manual_prior_file"] = manual_prior_file
            result = prepare_step18_world_cup_awards(**kwargs)
            st.session_state[_SESSION_AWARDS_NOTICE] = {
                "level": "success",
                "message": "World Cup awards artifacts generated successfully.",
                "details": result,
            }
        except (RuntimeError, FileNotFoundError, ValueError) as exc:
            st.session_state[_SESSION_AWARDS_NOTICE] = {
                "level": "error",
                "message": str(exc),
                "details": None,
            }
        except Exception as exc:  # pragma: no cover - UI safety
            st.session_state[_SESSION_AWARDS_NOTICE] = {
                "level": "error",
                "message": f"Awards generation failed: {exc}",
                "details": None,
            }
    st.rerun()


def render_page() -> None:
    render_hero(
        "World Cup Awards Forecast",
        "Golden Ball, Golden Boot, Golden Glove, Young Player, and Team of the Tournament estimates.",
        eyebrow="Awards analytics",
    )

    pdata = load_product_data_status()
    summary = _load_json(WORLD_CUP_AWARDS_SUMMARY_FILE)
    golden_ball_df = _load_csv(GOLDEN_BALL_PREDICTIONS_FILE)
    golden_boot_df = _load_csv(GOLDEN_BOOT_PREDICTIONS_FILE)
    golden_glove_df = _load_csv(GOLDEN_GLOVE_PREDICTIONS_FILE)
    young_player_df = _load_csv(YOUNG_PLAYER_PREDICTIONS_FILE)
    fair_play_df = _load_csv(FAIR_PLAY_PREDICTIONS_FILE)
    entertaining_df = _load_csv(MOST_ENTERTAINING_TEAM_PREDICTIONS_FILE)
    team_of_tournament_df = _load_csv(TEAM_OF_THE_TOURNAMENT_FILE)
    potm_proxy_df = _load_csv(PLAYER_OF_THE_MATCH_PROXY_FILE)
    got_proxy_df = _load_csv(GOAL_OF_THE_TOURNAMENT_PROXY_FILE)
    validation_df = _load_csv(WORLD_CUP_AWARDS_VALIDATION_REPORT_FILE)
    report_path = REPORTS_DIR / WORLD_CUP_AWARDS_REPORT_FILE
    player_col = _player_col(golden_ball_df) or "player_name"
    has_awards = _awards_outputs_exist()

    if has_awards:
        render_section_header("Award leaders")
        gb = summary.get("top_golden_ball_player") or _leader_from_df(golden_ball_df, "golden_ball_rank", player_col)
        gbt = summary.get("top_golden_boot_player") or _leader_from_df(golden_boot_df, "golden_boot_rank", player_col)
        gg = summary.get("top_golden_glove_player") or _leader_from_df(golden_glove_df, "golden_glove_rank", player_col)
        yp = summary.get("top_young_player") or _leader_from_df(young_player_df, "young_player_rank", player_col)
        tot_count = summary.get("team_of_tournament_count") or len(team_of_tournament_df)

        l1, l2, l3, l4, l5 = st.columns(5)
        with l1:
            render_metric_card("Golden Ball", gb or "—", sub="Best player", variant="accent" if gb else "")
        with l2:
            render_metric_card("Golden Boot", gbt or "—", sub="Top scorer", variant="accent" if gbt else "")
        with l3:
            render_metric_card("Golden Glove", gg or "—", sub="Best goalkeeper", variant="accent" if gg else "")
        with l4:
            render_metric_card("Young Player", yp or "—", sub="Best U-21", variant="accent" if yp else "")
        with l5:
            render_metric_card("Team of Tournament", f"{tot_count} players" if tot_count else "—", sub="4-3-3 XI")

        tab_leaders, tab_all, tab_downloads = st.tabs(["Podiums", "All categories", "Downloads"])

        with tab_leaders:
            render_section_header("Golden Ball podium")
            if not golden_ball_df.empty and "golden_ball_rank" in golden_ball_df.columns:
                render_podium_cards(
                    golden_ball_df,
                    rank_col="golden_ball_rank",
                    name_col=player_col,
                    score_col="golden_ball_probability" if "golden_ball_probability" in golden_ball_df.columns else None,
                    award_labels={1: "Golden Ball", 2: "Silver Ball", 3: "Bronze Ball"},
                )
            else:
                st.info("Golden Ball rankings not available.")

            render_section_header("Golden Boot race")
            if not golden_boot_df.empty:
                render_podium_cards(
                    golden_boot_df,
                    rank_col="golden_boot_rank",
                    name_col=player_col,
                    score_col="golden_boot_probability" if "golden_boot_probability" in golden_boot_df.columns else "expected_goals",
                    award_labels={1: "Golden Boot", 2: "Silver Boot", 3: "Bronze Boot"},
                )
            else:
                st.info("Golden Boot rankings not available.")

            render_section_header("Team of the Tournament — 4-3-3")
            if not team_of_tournament_df.empty:
                render_team_formation(team_of_tournament_df, name_col=player_col)
            else:
                st.info("Team of the Tournament not available.")

        with tab_all:
            g1, g2 = st.columns(2)
            with g1:
                render_section_header("Golden Glove")
                if not golden_glove_df.empty:
                    with st.expander("Golden Glove table", expanded=True):
                        cols = [c for c in ["golden_glove_rank", player_col, "team", "golden_glove_probability", "award"] if c in golden_glove_df.columns]
                        render_data_table(golden_glove_df[cols].head(10))
                else:
                    st.info("No Golden Glove output available.")

                render_section_header("Fair Play Trophy")
                if not fair_play_df.empty:
                    top = fair_play_df.sort_values("fair_play_rank").head(1).iloc[0]
                    render_metric_card("Leader", str(top.get("team", "—")))
                    with st.expander("Fair Play table"):
                        cols = [c for c in ["fair_play_rank", "team", "fair_play_probability", "award"] if c in fair_play_df.columns]
                        render_data_table(fair_play_df[cols].head(10))
                else:
                    st.info("No Fair Play output available.")

            with g2:
                render_section_header("Young Player")
                if not young_player_df.empty:
                    with st.expander("Young Player table", expanded=True):
                        cols = [
                            c
                            for c in ["young_player_rank", player_col, "team", "position", "young_player_probability", "award"]
                            if c in young_player_df.columns
                        ]
                        render_data_table(young_player_df[cols].head(10))
                else:
                    st.info("No Young Player output available.")

                render_section_header("Most Entertaining Team")
                if not entertaining_df.empty:
                    top = entertaining_df.sort_values("most_entertaining_rank").head(1).iloc[0]
                    render_metric_card("Leader", str(top.get("team", "—")))
                    with st.expander("Entertaining team table"):
                        cols = [c for c in ["most_entertaining_rank", "team", "most_entertaining_probability", "award"] if c in entertaining_df.columns]
                        render_data_table(entertaining_df[cols].head(10))
                else:
                    st.info("No Most Entertaining Team output available.")

            render_section_header("Proxy awards")
            p1, p2 = st.columns(2)
            with p1:
                st.caption("Player of the Match proxy")
                if not potm_proxy_df.empty:
                    cols = [c for c in ["player_of_match_proxy_rank", player_col, "team", "estimated_potm_count"] if c in potm_proxy_df.columns]
                    render_data_table(potm_proxy_df[cols].head(8))
                else:
                    st.info("No Player of the Match proxy available.")
            with p2:
                st.caption("Goal of the Tournament proxy")
                if not got_proxy_df.empty:
                    cols = [c for c in ["goal_of_tournament_proxy_rank", player_col, "team", "goal_of_tournament_proxy_probability"] if c in got_proxy_df.columns]
                    render_data_table(got_proxy_df[cols].head(8))
                else:
                    st.info("No Goal of the Tournament proxy available.")

            if not golden_ball_df.empty:
                with st.expander("Full Golden Ball table"):
                    cols = [c for c in ["golden_ball_rank", player_col, "team", "position", "golden_ball_probability", "award"] if c in golden_ball_df.columns]
                    render_data_table(golden_ball_df[cols].head(15))
            if not golden_boot_df.empty:
                with st.expander("Full Golden Boot table"):
                    cols = [
                        c
                        for c in ["golden_boot_rank", player_col, "team", "position", "expected_goals", "golden_boot_probability", "award"]
                        if c in golden_boot_df.columns
                    ]
                    render_data_table(golden_boot_df[cols].head(15))

        with tab_downloads:
            render_section_header("Export artifacts")
            d1, d2 = st.columns(2)
            download_files = [
                (WORLD_CUP_AWARDS_PREDICTIONS_FILE, "Combined awards predictions"),
                (GOLDEN_BALL_PREDICTIONS_FILE, "Golden Ball rankings"),
                (GOLDEN_BOOT_PREDICTIONS_FILE, "Golden Boot rankings"),
                (GOLDEN_GLOVE_PREDICTIONS_FILE, "Golden Glove rankings"),
                (TEAM_OF_THE_TOURNAMENT_FILE, "Team of the Tournament XI"),
            ]
            for idx, (file_name, desc) in enumerate(download_files):
                col = d1 if idx % 2 == 0 else d2
                with col:
                    render_download_card(desc, file_name, PROCESSED_DATA_DIR / file_name)
            render_download_card(
                "Awards narrative report",
                WORLD_CUP_AWARDS_REPORT_FILE,
                report_path,
                mime="text/markdown",
            )

    else:
        render_empty_state(
            "Awards forecast not generated yet",
            "Run a tournament forecast first, then generate awards predictions.",
        )
        _show_awards_notice()
        monte_carlo_path = PROCESSED_DATA_DIR / MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE
        if pdata["awards_allowed"] and monte_carlo_path.is_file():
            with st.form("awards_generate_empty_form", clear_on_submit=False):
                generate_empty_clicked = st.form_submit_button(
                    "Generate awards forecast",
                    type="primary",
                    use_container_width=True,
                )
            if generate_empty_clicked:
                _run_awards_generation()
        elif not monte_carlo_path.is_file():
            st.button(
                "Open Tournament Forecast",
                use_container_width=True,
                key="awards_open_forecast_empty",
                on_click=navigate_to,
                kwargs={"page": "Tournament Forecast"},
            )

    with st.expander("Dataset readiness", expanded=False):
        badge_kind = "ok" if pdata["is_verified"] else "warn"
        st.markdown(
            f"{render_status_badge(pdata['data_label'], badge_kind)} "
            f"{render_status_badge(pdata['verification_label'], badge_kind if pdata['is_verified'] else 'warn')}",
            unsafe_allow_html=True,
        )
        r1, r2, r3, r4 = st.columns(4)
        with r1:
            render_metric_card("Teams", str(pdata["teams_count"]))
        with r2:
            render_metric_card("Players", f"{pdata['players_count']:,}")
        with r3:
            render_metric_card("Full squads", str(pdata["teams_with_26_players"]))
        with r4:
            render_metric_card("Fixtures", str(pdata["fixtures_count"]))

    with st.expander("Advanced generation tools", expanded=False):
        enriched_path = PROCESSED_DATA_DIR / getattr(C, "ENRICHED_OFFICIAL_AWARD_CANDIDATES_FILE", "enriched_official_award_candidates.csv")
        quality_path = PROCESSED_DATA_DIR / getattr(C, "PLAYER_PRIOR_QUALITY_REPORT_FILE", "player_prior_quality_report.csv")
        monte_carlo_path = PROCESSED_DATA_DIR / MONTE_CARLO_TEAM_STAGE_PROBABILITIES_FILE

        _show_awards_notice()

        if not pdata["awards_allowed"]:
            st.info("Official data must be verified before generating awards. Check the Data Quality page.")
        elif not monte_carlo_path.is_file():
            st.info("Monte Carlo team stage probabilities are required. Run a tournament forecast first.")
            st.button(
                "Open Tournament Forecast",
                key="awards_open_forecast_tools",
                on_click=navigate_to,
                kwargs={"page": "Tournament Forecast"},
            )
        else:
            with st.form("awards_generate_tools_form", clear_on_submit=False):
                col_gen, col_refresh = st.columns(2)
                with col_gen:
                    generate_clicked = st.form_submit_button(
                        "Generate awards predictions",
                        type="primary",
                        use_container_width=True,
                    )
                with col_refresh:
                    refresh_clicked = st.form_submit_button("Refresh page", use_container_width=True)

            if generate_clicked:
                _run_awards_generation()
            elif refresh_clicked:
                st.rerun()

        render_section_header("Prior enrichment")
        st.caption(MANUAL_PRIOR_DISCLAIMER)
        with st.form("awards_enrichment_form", clear_on_submit=False):
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                enrich_clicked = st.form_submit_button("Enrich player priors", use_container_width=True)
            with col_e2:
                regenerate_enriched_clicked = st.form_submit_button(
                    "Regenerate with enriched priors",
                    use_container_width=True,
                )

        if enrich_clicked:
            with st.spinner("Enriching player priors…"):
                try:
                    enrich_summary = create_enriched_player_priors()
                    merge_enriched_priors_into_award_candidates(update_official=False)
                    st.session_state[_SESSION_AWARDS_NOTICE] = {
                        "level": "success",
                        "message": f"Enriched {enrich_summary.get('candidate_count')} candidates.",
                        "details": enrich_summary,
                    }
                except Exception as exc:
                    st.session_state[_SESSION_AWARDS_NOTICE] = {
                        "level": "error",
                        "message": str(exc),
                        "details": None,
                    }
            st.rerun()

        if regenerate_enriched_clicked:
            with st.spinner("Regenerating awards with enriched priors…"):
                try:
                    if not enriched_path.is_file():
                        create_enriched_player_priors()
                        merge_enriched_priors_into_award_candidates(update_official=False)
                    result = prepare_step18_world_cup_awards(use_enriched_candidates=True)
                    st.session_state[_SESSION_AWARDS_NOTICE] = {
                        "level": "success",
                        "message": "Awards regenerated with enriched candidates.",
                        "details": result,
                    }
                except Exception as exc:
                    st.session_state[_SESSION_AWARDS_NOTICE] = {
                        "level": "error",
                        "message": str(exc),
                        "details": None,
                    }
            st.rerun()

        if quality_path.is_file():
            qdf = pd.read_csv(quality_path)
            flat_row = qdf[qdf["metric"] == "flatness_score"]
            flat_val = flat_row.iloc[0]["value"] if not flat_row.empty else "—"
            render_metric_card("Prior flatness score", str(flat_val))

        with st.form("awards_manual_priors_form", clear_on_submit=False):
            manual_clicked = st.form_submit_button(
                "Generate with manual demo priors",
                use_container_width=True,
            )

        if manual_clicked:
            with st.spinner("Generating awards with manual demo priors…"):
                try:
                    demo_path = resolve_manual_prior_file(None)
                    if not enriched_path.is_file():
                        create_enriched_player_priors()
                        merge_enriched_priors_into_award_candidates(update_official=False)
                    result = prepare_step18_world_cup_awards(
                        use_enriched_candidates=True,
                        use_manual_priors=True,
                        manual_prior_file=demo_path,
                    )
                    st.session_state[_SESSION_AWARDS_NOTICE] = {
                        "level": "success",
                        "message": "Awards regenerated with enriched + manual demo priors.",
                        "details": result,
                    }
                except Exception as exc:
                    st.session_state[_SESSION_AWARDS_NOTICE] = {
                        "level": "error",
                        "message": str(exc),
                        "details": None,
                    }
            st.rerun()

        with st.expander("Methodology and validation", expanded=False):
            st.markdown(
                "Analytics estimates using official squads and Monte Carlo stage probabilities. "
                "Not official FIFA predictions."
            )
            if not validation_df.empty:
                render_data_table(validation_df)

    st.markdown(f'<p class="wc-disclaimer-sm">{AWARDS_ANALYTICS_DISCLAIMER}</p>', unsafe_allow_html=True)
