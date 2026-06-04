"""Inspect and normalize global model explanation report."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import src.utils.constants as C

RANKING_FEATURE_IMPORTANCE_FILE = getattr(C, "RANKING_FEATURE_IMPORTANCE_FILE", "ranking_feature_importance.csv")
IMPROVED_FEATURE_IMPORTANCE_FILE = getattr(C, "IMPROVED_FEATURE_IMPORTANCE_FILE", "improved_feature_importance.csv")
FEATURE_IMPORTANCE_RF_FILE = getattr(C, "FEATURE_IMPORTANCE_RF_FILE", "feature_importance_random_forest.csv")
GLOBAL_EXPLANATION_REPORT_FILE = getattr(C, "GLOBAL_EXPLANATION_REPORT_FILE", "global_model_explanation.csv")
READABLE_FEATURE_NAMES = getattr(C, "READABLE_FEATURE_NAMES", {})


def _readable_name(feature: str) -> str:
    return READABLE_FEATURE_NAMES.get(feature, feature.replace("_", " ").strip().title())


def _resolve_importance_file(reports_dir: Path) -> Path | None:
    candidates = [
        reports_dir / RANKING_FEATURE_IMPORTANCE_FILE,
        reports_dir / IMPROVED_FEATURE_IMPORTANCE_FILE,
        reports_dir / FEATURE_IMPORTANCE_RF_FILE,
    ]
    for path in candidates:
        if path.is_file():
            return path
    return None


def _normalize_importance_table(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["feature", "readable_feature", "importance", "importance_normalized"])

    col_candidates = ["feature", "column", "name"]
    feature_col = next((c for c in col_candidates if c in df.columns), None)
    if feature_col is None:
        feature_col = df.columns[0]

    importance_col_candidates = ["importance", "feature_importance", "score"]
    importance_col = next((c for c in importance_col_candidates if c in df.columns), None)
    if importance_col is None:
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        if not numeric_cols:
            return pd.DataFrame(columns=["feature", "readable_feature", "importance", "importance_normalized"])
        importance_col = numeric_cols[0]

    out = df[[feature_col, importance_col]].copy()
    out.columns = ["feature", "importance"]
    out["importance"] = pd.to_numeric(out["importance"], errors="coerce").fillna(0.0)

    total = out["importance"].sum()
    out["importance_normalized"] = out["importance"] / total if total > 0 else 0.0
    out["readable_feature"] = out["feature"].astype(str).map(_readable_name)

    return out.sort_values("importance", ascending=False).reset_index(drop=True)


def main(argv: Sequence[str] | None = None) -> int:
    _ = argv
    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    source_path = _resolve_importance_file(reports_dir)
    if source_path is None:
        print(
            "No feature importance report found. "
            "Run a model training script first (ranking/improved/baseline)."
        )
        return 0

    source_df = pd.read_csv(source_path)
    normalized = _normalize_importance_table(source_df)

    print(f"Using source importance file: {source_path}")
    print("Top 20 global features:")
    print(normalized.head(20).to_string(index=False))

    out_path = reports_dir / GLOBAL_EXPLANATION_REPORT_FILE
    normalized.to_csv(out_path, index=False)
    print(f"Saved normalized global explanation report to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
