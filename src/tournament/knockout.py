"""Knockout bracket placeholders for Step 11 (no simulation yet)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import src.utils.constants as C

PROCESSED_DATA_DIR = getattr(C, "PROCESSED_DATA_DIR", Path("data") / "processed")
KNOCKOUT_PLACEHOLDER_FILE = getattr(C, "KNOCKOUT_PLACEHOLDER_FILE", "knockout_placeholders.csv")

TOURNAMENT_STAGE_ROUND_OF_32 = getattr(C, "TOURNAMENT_STAGE_ROUND_OF_32", "round_of_32")
TOURNAMENT_STAGE_ROUND_OF_16 = getattr(C, "TOURNAMENT_STAGE_ROUND_OF_16", "round_of_16")
TOURNAMENT_STAGE_QUARTER_FINAL = getattr(C, "TOURNAMENT_STAGE_QUARTER_FINAL", "quarter_final")
TOURNAMENT_STAGE_SEMI_FINAL = getattr(C, "TOURNAMENT_STAGE_SEMI_FINAL", "semi_final")
TOURNAMENT_STAGE_THIRD_PLACE = getattr(C, "TOURNAMENT_STAGE_THIRD_PLACE", "third_place")
TOURNAMENT_STAGE_FINAL = getattr(C, "TOURNAMENT_STAGE_FINAL", "final")


def create_knockout_placeholders() -> pd.DataFrame:
    """Create placeholder knockout bracket structure for 32-team knockout path."""
    rows: list[dict[str, str]] = []

    for i in range(1, 17):
        next_match = (i + 1) // 2
        rows.append(
            {
                "round": TOURNAMENT_STAGE_ROUND_OF_32,
                "match_id": f"R32-{i:02d}",
                "slot_a_source": f"R32_SLOT_{2 * i - 1:02d}",
                "slot_b_source": f"R32_SLOT_{2 * i:02d}",
                "winner_to": f"R16-{next_match:02d}",
            }
        )

    for i in range(1, 9):
        next_match = (i + 1) // 2
        rows.append(
            {
                "round": TOURNAMENT_STAGE_ROUND_OF_16,
                "match_id": f"R16-{i:02d}",
                "slot_a_source": f"WINNER-R32-{2 * i - 1:02d}",
                "slot_b_source": f"WINNER-R32-{2 * i:02d}",
                "winner_to": f"QF-{next_match:02d}",
            }
        )

    for i in range(1, 5):
        next_match = (i + 1) // 2
        rows.append(
            {
                "round": TOURNAMENT_STAGE_QUARTER_FINAL,
                "match_id": f"QF-{i:02d}",
                "slot_a_source": f"WINNER-R16-{2 * i - 1:02d}",
                "slot_b_source": f"WINNER-R16-{2 * i:02d}",
                "winner_to": f"SF-{next_match:02d}",
            }
        )

    for i in range(1, 3):
        rows.append(
            {
                "round": TOURNAMENT_STAGE_SEMI_FINAL,
                "match_id": f"SF-{i:02d}",
                "slot_a_source": f"WINNER-QF-{2 * i - 1:02d}",
                "slot_b_source": f"WINNER-QF-{2 * i:02d}",
                "winner_to": "F-01",
            }
        )

    rows.append(
        {
            "round": TOURNAMENT_STAGE_THIRD_PLACE,
            "match_id": "TP-01",
            "slot_a_source": "LOSER-SF-01",
            "slot_b_source": "LOSER-SF-02",
            "winner_to": "THIRD_PLACE_WINNER",
        }
    )
    rows.append(
        {
            "round": TOURNAMENT_STAGE_FINAL,
            "match_id": "F-01",
            "slot_a_source": "WINNER-SF-01",
            "slot_b_source": "WINNER-SF-02",
            "winner_to": "CHAMPION",
        }
    )

    return pd.DataFrame(rows, columns=["round", "match_id", "slot_a_source", "slot_b_source", "winner_to"])


def save_knockout_placeholders(df: pd.DataFrame, output_path: str | None = None) -> str:
    """Save knockout placeholders under processed folder."""
    path = Path(output_path) if output_path else PROCESSED_DATA_DIR / KNOCKOUT_PLACEHOLDER_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return str(path)
