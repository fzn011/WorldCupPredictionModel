"""CLI for Step 10 local explanation on future match predictions."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.models.explain_prediction import explain_future_match_prediction
from src.models.prediction_utils import get_prediction_confidence
import src.utils.constants as C

DEFAULT_FUTURE_MATCH_DATE = getattr(C, "DEFAULT_FUTURE_MATCH_DATE", "2026-06-11")
DEFAULT_FUTURE_TOURNAMENT = getattr(C, "DEFAULT_FUTURE_TOURNAMENT", "FIFA World Cup")
DEFAULT_FUTURE_CITY = getattr(C, "DEFAULT_FUTURE_CITY", "Unknown")
DEFAULT_FUTURE_COUNTRY = getattr(C, "DEFAULT_FUTURE_COUNTRY", "Unknown")
DEFAULT_FUTURE_NEUTRAL = getattr(C, "DEFAULT_FUTURE_NEUTRAL", 1)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Explain a future match prediction.")
    parser.add_argument("--team-a", required=True)
    parser.add_argument("--team-b", required=True)
    parser.add_argument("--date", default=DEFAULT_FUTURE_MATCH_DATE)
    parser.add_argument("--tournament", default=DEFAULT_FUTURE_TOURNAMENT)
    parser.add_argument("--city", default=DEFAULT_FUTURE_CITY)
    parser.add_argument("--country", default=DEFAULT_FUTURE_COUNTRY)
    parser.add_argument("--neutral", type=int, default=DEFAULT_FUTURE_NEUTRAL)
    return parser


def _print_factor_block(title: str, table) -> None:
    print(title)
    if table is None or getattr(table, "empty", True):
        print("- (none)")
        return

    for _, row in table.iterrows():
        feature_name = row.get("readable_feature", row.get("feature", "unknown_feature"))
        contribution = row.get("contribution", row.get("shap_value", row.get("importance", 0.0)))
        feature_value = row.get("feature_value", "N/A")
        print(f"- {feature_name}: value={feature_value}, contribution={contribution}")


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)

    try:
        result = explain_future_match_prediction(
            team_a=args.team_a,
            team_b=args.team_b,
            match_date=args.date,
            tournament=args.tournament,
            city=args.city,
            country=args.country,
            neutral=args.neutral,
        )
    except Exception as exc:
        print(f"[error] Explanation failed: {exc}")
        return 1

    prediction = result.get("prediction", {})
    probabilities = prediction.get("probabilities", {})
    confidence_label, confidence_score = get_prediction_confidence(probabilities)

    print("=== Future Match Prediction Explanation ===")
    print(f"Team A: {result.get('team_a')}")
    print(f"Team B: {result.get('team_b')}")
    print(f"Match date: {result.get('match_date')}")
    print(f"Predicted label: {prediction.get('predicted_label')}")
    print(f"Confidence: {confidence_label} ({confidence_score:.3f})")
    print(f"Explanation method: {result.get('explanation_method')}")
    print("Natural-language explanation:")
    print(result.get("natural_language_explanation", "N/A"))

    _print_factor_block("Top supporting factors:", result.get("top_supporting_factors"))
    _print_factor_block("Top opposing factors:", result.get("top_opposing_factors"))

    print(f"Saved report path: {result.get('report_path')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
