from typing import List
from ..core.models import PlayerScorecard


class ScoreboardVisualizer:
    """Renders formatted ASCII tables and terminal summaries."""

    @staticmethod
    def format_terminal_summary(players: List[PlayerScorecard]) -> str:
        lines = []
        lines.append("=" * 72)
        lines.append("                FINAL DERIVED BOWLING SCOREBOARD")
        lines.append("=" * 72)
        for p in players:
            ttl = p.total_score if p.total_score is not None else "unknown"
            lines.append(f"  {p.name:20s}  ==>  TTL: {ttl}")
        lines.append("-" * 72)

        header = f"{'PLAYER':<16} | " + " | ".join([f"F{i:<2}" for i in range(1, 11)]) + " | TTL"
        lines.append(header)
        lines.append("-" * len(header))

        for p in players:
            row_items = []
            for i in range(1, 11):
                cell = p.frames[i]
                if not cell.is_played:
                    row_items.append(" .  ")
                else:
                    r = cell.rolls_formatted()
                    c = str(cell.cumulative_score) if cell.cumulative_score is not None else "?"
                    row_items.append(f"{r:>2}|{c:<2}")

            ttl_str = str(p.total_score) if p.total_score is not None else "-"
            lines.append(f"{p.name:<16} | " + " | ".join(row_items) + f" | {ttl_str:>3}")

        lines.append("=" * 72)
        return "\n".join(lines)
