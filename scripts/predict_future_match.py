"""CLI for Step 8 future match prediction."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.features.future_match_features import create_future_prediction_report
from src.models.predict_match import predict_future_match
import src.utils.constants as C

DEFAULT_FUTURE_MATCH_DATE = getattr(C, "DEFAULT_FUTURE_MATCH_DATE", "2026-06-11")
DEFAULT_FUTURE_TOURNAMENT = getattr(C, "DEFAULT_FUTURE_TOURNAMENT", "FIFA World Cup")
DEFAULT_FUTURE_CITY = getattr(C, "DEFAULT_FUTURE_CITY", "Unknown")
DEFAULT_FUTURE_COUNTRY = getattr(C, "DEFAULT_FUTURE_COUNTRY", "Unknown")
DEFAULT_FUTURE_NEUTRAL = getattr(C, "DEFAULT_FUTURE_NEUTRAL", 1)
FUTURE_PREDICTION_LOG_FILE = getattr(C, "FUTURE_PREDICTION_LOG_FILE", "future_prediction_log.csv")



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



def _append_prediction_log(report_df: pd.DataFrame) -> Path:
    log_path = Path("reports") / FUTURE_PREDICTION_LOG_FILE
    log_path.parent.mkdir(parents=True, exist_ok=True)

    if log_path.is_file():
        existing = pd.read_csv(log_path)
        combined = pd.concat([existing, report_df], ignore_index=True)
    else:
        combined = report_df

    combined.to_csv(log_path, index=False)
    return log_path



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
    print("=== Future Match Prediction ===")
    print(f"Team A: {prediction['team_a']}")
    print(f"Team B: {prediction['team_b']}")
    print(f"Match date: {prediction['match_date']}")
    print(f"Model type: {prediction['model_type']}")
    print(f"Team A loss probability: {probs['team_a_loss']:.6f}")
    print(f"Draw probability: {probs['draw']:.6f}")
    print(f"Team A win probability: {probs['team_a_win']:.6f}")
    print(f"Predicted label: {prediction['predicted_label']}")

    notes = prediction.get("notes", [])
    if notes:
        print("Notes:")
        for note in notes:
            print(f"- {note}")

    report_df = create_future_prediction_report(prediction["feature_row"], prediction)
    log_path = _append_prediction_log(report_df)
    print(f"Prediction log appended to: {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
