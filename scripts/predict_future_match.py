"""CLI for Step 8 future match prediction."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.models.prediction_utils import (
    append_prediction_history,
    format_probability,
    save_latest_prediction_report,
)
from src.models.predict_match import predict_future_match
import src.utils.constants as C

DEFAULT_FUTURE_MATCH_DATE = getattr(C, "DEFAULT_FUTURE_MATCH_DATE", "2026-06-11")
DEFAULT_FUTURE_TOURNAMENT = getattr(C, "DEFAULT_FUTURE_TOURNAMENT", "FIFA World Cup")
DEFAULT_FUTURE_CITY = getattr(C, "DEFAULT_FUTURE_CITY", "Unknown")
DEFAULT_FUTURE_COUNTRY = getattr(C, "DEFAULT_FUTURE_COUNTRY", "Unknown")
DEFAULT_FUTURE_NEUTRAL = getattr(C, "DEFAULT_FUTURE_NEUTRAL", 1)
PREDICTION_HISTORY_FILE = getattr(C, "PREDICTION_HISTORY_FILE", "future_prediction_log.csv")
LATEST_PREDICTION_REPORT_FILE = getattr(C, "LATEST_PREDICTION_REPORT_FILE", "latest_prediction_report.csv")



def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Predict an arbitrary future match.")
    parser.add_argument("--team-a", required=True)
    parser.add_argument("--team-b", required=True)
    parser.add_argument("--date", default=DEFAULT_FUTURE_MATCH_DATE)
    parser.add_argument("--tournament", default=DEFAULT_FUTURE_TOURNAMENT)
    parser.add_argument("--city", default=DEFAULT_FUTURE_CITY)
    parser.add_argument("--country", default=DEFAULT_FUTURE_COUNTRY)
    parser.add_argument("--neutral", type=int, default=DEFAULT_FUTURE_NEUTRAL)
    return parser



def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)

    try:
        prediction = predict_future_match(
            team_a=args.team_a,
            team_b=args.team_b,
            match_date=args.date,
            tournament=args.tournament,
            city=args.city,
            country=args.country,
            neutral=args.neutral,
        )
    except Exception as exc:
        print(f"[error] Future prediction failed: {exc}")
        return 1

    probs = prediction["probabilities"]
    confidence = prediction.get("confidence", {})

    print("=== Future Match Prediction ===")
    print(f"Team A: {prediction['team_a']}")
    print(f"Team B: {prediction['team_b']}")
    print(f"Match date: {prediction['match_date']}")
    print(f"Tournament: {prediction.get('tournament')}")
    print(f"Model type: {prediction['model_type']}")
    print(f"Predicted label: {prediction['predicted_label']}")
    print(f"Confidence label: {confidence.get('confidence_label', 'Unknown')}")
    print(f"Team A loss probability: {format_probability(probs['team_a_loss'])}")
    print(f"Draw probability: {format_probability(probs['draw'])}")
    print(f"Team A win probability: {format_probability(probs['team_a_win'])}")

    preview = prediction.get("feature_preview", {})
    if preview:
        print("Feature preview:")
        for key, value in preview.items():
            print(f"- {key}: {value}")

    notes = prediction.get("notes", [])
    if notes:
        print("Notes:")
        for note in notes:
            print(f"- {note}")

    history_path = append_prediction_history(prediction)
    latest_report_path = save_latest_prediction_report(prediction)
    print(f"Prediction history path: {history_path}")
    print(f"Latest report path: {latest_report_path}")

    # Keep explicit artifact names visible in script output.
    print(f"History artifact file: reports/{PREDICTION_HISTORY_FILE}")
    print(f"Latest report artifact file: reports/{LATEST_PREDICTION_REPORT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
