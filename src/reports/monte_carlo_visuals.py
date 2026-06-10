"""Step 16 Monte Carlo plotting utilities using matplotlib only."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib
matplotlib.use("Agg", force=True)
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import numpy as np
import pandas as pd

import src.utils.constants as C

PROJECT_ROOT = getattr(C, "PROJECT_ROOT", Path(__file__).resolve().parents[2])
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
MONTE_CARLO_CHAMPION_CHART_FILE = getattr(C, "MONTE_CARLO_CHAMPION_CHART_FILE", "monte_carlo_champion_probabilities.png")
MONTE_CARLO_STAGE_HEATMAP_FILE = getattr(C, "MONTE_CARLO_STAGE_HEATMAP_FILE", "monte_carlo_stage_heatmap.png")
MONTE_CARLO_TOP_N_TEAMS = int(getattr(C, "MONTE_CARLO_TOP_N_TEAMS", 20))


def plot_champion_probabilities(
    champion_df: pd.DataFrame,
    top_n: int = 15,
    output_path: str | None = None,
) -> str:
    """Plot a horizontal bar chart of top champion probabilities."""
    if champion_df.empty:
        raise ValueError("Champion probability DataFrame is empty.")

    df = champion_df.sort_values(["champion_probability", "champion_count", "team"], ascending=[False, False, True]).head(int(top_n)).copy()
    path = Path(output_path) if output_path else FIGURES_DIR / MONTE_CARLO_CHAMPION_CHART_FILE
    path.parent.mkdir(parents=True, exist_ok=True)

    fig = Figure(figsize=(10, max(5, len(df) * 0.45)))
    FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    ax.barh(df["team"], df["champion_probability"])
    ax.set_xlabel("Champion probability")
    ax.set_ylabel("Team")
    ax.set_title("Monte Carlo Champion Probabilities")
    ax.invert_yaxis()
    ax.set_xlim(0, max(0.01, float(df["champion_probability"].max()) * 1.15))
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    return str(path)


def plot_stage_probability_heatmap(
    stage_df: pd.DataFrame,
    top_n: int = 15,
    output_path: str | None = None,
) -> str:
    """Plot a simple matplotlib heatmap of stage progression probabilities."""
    if stage_df.empty:
        raise ValueError("Stage probability DataFrame is empty.")

    cols = [
        "round_of_32_probability",
        "round_of_16_probability",
        "quarter_final_probability",
        "semi_final_probability",
        "final_probability",
        "champion_probability",
    ]
    labels = ["Round of 32", "Round of 16", "Quarter-final", "Semi-final", "Final", "Champion"]
    df = stage_df.sort_values(["champion_probability", "final_probability", "team"], ascending=[False, False, True]).head(int(top_n)).copy()

    matrix = df[cols].to_numpy(dtype=float)
    path = Path(output_path) if output_path else FIGURES_DIR / MONTE_CARLO_STAGE_HEATMAP_FILE
    path.parent.mkdir(parents=True, exist_ok=True)

    fig = Figure(figsize=(11, max(5, len(df) * 0.45)))
    FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    image = ax.imshow(matrix, aspect="auto", cmap="Blues", vmin=0.0, vmax=max(1.0, float(np.nanmax(matrix)) if matrix.size else 1.0))
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df["team"].tolist())
    ax.set_title("Monte Carlo Stage Progression Heatmap")
    cbar = fig.colorbar(image, ax=ax)
    cbar.set_label("Probability")
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    return str(path)
