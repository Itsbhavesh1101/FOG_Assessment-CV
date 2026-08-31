import csv
from pathlib import Path
from typing import List, Optional
from ..core.models import PlayerScorecard


def serialize_match_csv(
    players: List[PlayerScorecard],
    output_path: Path,
) -> None:
    """
    Exports final match scorecard to standard CSV format.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["player", "frame", "rolls", "cumulative", "ttl"])

        for player in players:
            ttl_val = player.total_score if player.total_score is not None else "unknown"
            for f_idx in range(1, 11):
                cell = player.frames[f_idx]
                if not cell.is_played:
                    rolls_str = "unplayed"
                    cum_str = "unplayed"
                else:
                    rolls_str = cell.rolls_formatted()
                    cum_str = str(cell.cumulative_score) if cell.cumulative_score is not None else "unknown"
                writer.writerow([player.name, f_idx, rolls_str, cum_str, ttl_val])


def export_timeline_history_csv(
    history_records: List[dict],
    output_path: Path,
) -> None:
    """Exports full frame-by-frame timeline observations to CSV."""
    if not history_records:
        return

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["timestamp", "player", "frame", "rolls", "cumulative", "ttl"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(history_records)
