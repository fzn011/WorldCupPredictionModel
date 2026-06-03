"""Inspect the saved Step 5 baseline-model results."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

# Make `src` importable when running this script directly.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.constants import (  # noqa: E402
    BASELINE_MODEL_DIR,
    BEST_BASELINE_MODEL_FILE,
    CONFUSION_MATRIX_DUMMY_FILE,
    CONFUSION_MATRIX_LOGISTIC_FILE,
    CONFUSION_MATRIX_RF_FILE,
    FEATURE_IMPORTANCE_RF_FILE,
    MODEL_METADATA_FILE,
    MODEL_METRICS_FILE,
)


def _print_if_exists(path: Path, header: str) -> None:
    if not path.is_file():
        print(f"[info] Missing {path}. Run `python scripts/train_baseline_models.py` first.")
        return
    print(f"\n{header}")
    if path.suffix.lower() == ".csv":
        print(pd.read_csv(path).to_string(index=False))
    else:
        print(path.read_text())


def main() -> None:
    """Print the saved model metrics and supporting artifacts."""
    metrics_path = Path("reports") / MODEL_METRICS_FILE
    if not metrics_path.is_file():
        print("Run `python scripts/train_baseline_models.py` first.")
        return

    metrics_df = pd.read_csv(metrics_path)
    sort_column = "log_loss" if "log_loss" in metrics_df.columns and metrics_df["log_loss"].notna().any() else "macro_f1"
    ascending = sort_column == "log_loss"
    print("=== Model Metrics ===")
    print(metrics_df.sort_values(sort_column, ascending=ascending).to_string(index=False))

    metadata_path = Path(BASELINE_MODEL_DIR) / MODEL_METADATA_FILE
    if metadata_path.is_file():
        metadata = json.loads(metadata_path.read_text())
        print("\n=== Best Model ===")
        print(metadata.get("best_model_name"))
        print(metadata.get("best_model_path"))

        confusion_map = {
            "dummy": CONFUSION_MATRIX_DUMMY_FILE,
            "logistic_regression": CONFUSION_MATRIX_LOGISTIC_FILE,
            "random_forest": CONFUSION_MATRIX_RF_FILE,
        }
        best_name = metadata.get("best_model_name")
        if best_name in confusion_map:
            confusion_path = Path("reports") / confusion_map[best_name]
            if confusion_path.is_file():
                print("\n=== Best Model Confusion Matrix ===")
                print(pd.read_csv(confusion_path, index_col=0).to_string())
    else:
        print(f"\n[info] Missing {metadata_path}")

    rf_importance_path = Path("reports") / FEATURE_IMPORTANCE_RF_FILE
    if rf_importance_path.is_file():
        rf_df = pd.read_csv(rf_importance_path).head(20)
        print("\n=== Top 20 Random Forest Feature Importances ===")
        print(rf_df.to_string(index=False))
    else:
        print(f"\n[info] Missing {rf_importance_path}")

    best_model_path = Path(BASELINE_MODEL_DIR) / BEST_BASELINE_MODEL_FILE
    if best_model_path.is_file():
        print(f"\nBest model artifact: {best_model_path}")
    else:
        print(f"\n[info] Missing {best_model_path}")


if __name__ == "__main__":
    main()
