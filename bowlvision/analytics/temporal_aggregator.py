from collections import Counter, deque
import copy
from typing import Dict, List, Optional, Tuple
from ..core.models import PlayerScorecard
from .bowling_rules import BowlingRules


class TemporalScoreboardTracker:
    """
    Temporal aggregation and state arbitration engine for bowling scorecards.
    Maintains a sliding temporal voting window per cell to smooth single-frame OCR noise,
    freezes state during camera cutaways, and enforces monotonic cumulative score accumulation.
    """

    def __init__(self, window_size: int = 5, min_confidence: float = 0.45):
        self.window_size = window_size
        self.min_confidence = min_confidence

        # (player_name, frame_idx, field_type) -> deque(maxlen=window_size) of (value, weight)
        self._history: Dict[Tuple[str, int, str], deque] = {}
        self.current_players: Dict[str, PlayerScorecard] = {}
        self.state_timeline: List[dict] = []
        self.csv_history_records: List[dict] = []

        self.stats = {
            "total_frames": 0,
            "visible_frames": 0,
            "cutaway_frames": 0,
            "corrections_made": 0,
        }

    def process_frame(
        self,
        timestamp: float,
        is_visible: bool,
        observed_players: Optional[Dict[str, PlayerScorecard]] = None,
        active_row: Optional[int] = None,
    ) -> dict:
        """Processes a single timestamp observation."""
        self.stats["total_frames"] += 1

        if not is_visible or not observed_players:
            self.stats["cutaway_frames"] += 1
            snapshot = {
                "timestamp": round(timestamp, 2),
                "scoreboard_visible": False,
                "players": [p.to_export_dict() for p in self.current_players.values()],
            }
            self.state_timeline.append(snapshot)
            return snapshot

        self.stats["visible_frames"] += 1

        for p_name, obs_card in observed_players.items():
            if p_name not in self.current_players:
                self.current_players[p_name] = PlayerScorecard(
                    row_index=obs_card.row_index,
                    name=p_name,
                )

            curr_card = self.current_players[p_name]
            is_active_player = (active_row is not None and curr_card.row_index == active_row)

            # 1. Process each frame cell F1..F10
            for f_idx in range(1, 11):
                obs_cell = obs_card.frames[f_idx]
                curr_cell = curr_card.frames[f_idx]

                # A. Rolls processing
                if obs_cell.rolls:
                    sanitized_rolls = []
                    for r_raw in obs_cell.rolls:
                        norm = BowlingRules.normalize_roll_token(str(r_raw))
                        if norm:
                            sanitized_rolls.append(norm)

                    if sanitized_rolls:
                        # For frame > 4, only allow new rolls if player is active or frame <= 4
                        if f_idx <= 4 or is_active_player:
                            roll_key = (p_name, f_idx, "rolls")
                            if roll_key not in self._history:
                                self._history[roll_key] = deque(maxlen=self.window_size)
                            
                            r_token = ",".join(sanitized_rolls)
                            self._history[roll_key].append((r_token, 0.95))

                            stable_token = self._vote_consensus(self._history[roll_key])
                            if stable_token:
                                new_rolls = [x for x in stable_token.split(",") if x]
                                if curr_cell.rolls != new_rolls:
                                    if curr_cell.rolls:
                                        self.stats["corrections_made"] += 1
                                    curr_cell.rolls = new_rolls

                # B. Cumulative Score processing
                if obs_cell.cumulative_score is not None:
                    c_val = obs_cell.cumulative_score
                    if 0 < c_val <= 300:
                        # For frame > 4, require active player or consensus
                        if f_idx <= 4 or is_active_player:
                            cum_key = (p_name, f_idx, "cumulative")
                            if cum_key not in self._history:
                                self._history[cum_key] = deque(maxlen=self.window_size)

                            self._history[cum_key].append((str(c_val), 0.95))
                            stable_cum = self._vote_consensus(self._history[cum_key])
                            if stable_cum and stable_cum.isdigit():
                                new_c_val = int(stable_cum)
                                if curr_cell.cumulative_score != new_c_val:
                                    if curr_cell.cumulative_score is not None:
                                        self.stats["corrections_made"] += 1
                                    curr_cell.cumulative_score = new_c_val

            # 2. Derive Strike 'X' for Frame 1 if cumulative score is >= 15 (Strike)
            if curr_card.frames[1].cumulative_score in (15, 20) and not curr_card.frames[1].rolls:
                curr_card.frames[1].rolls = ["X"]

            # 3. Derive cumulative score for newly active frame (e.g. Vishal F5 with roll 9-)
            if is_active_player:
                for f_idx in range(1, 11):
                    curr_cell = curr_card.frames[f_idx]
                    if curr_cell.rolls and curr_cell.cumulative_score is None:
                        prev_cum = curr_card.frames[f_idx - 1].cumulative_score if f_idx > 1 else 0
                        if prev_cum is None:
                            prev_cum = 0
                        roll_str = curr_cell.rolls[0]
                        new_cum = BowlingRules.compute_frame_score(prev_cum, roll_str)
                        if new_cum > 0:
                            curr_cell.cumulative_score = new_cum

            # 4. Enforce 10-pin Bowling TTL math
            valid_cums = [
                cell.cumulative_score
                for cell in curr_card.frames.values()
                if cell.cumulative_score is not None
            ]
            if valid_cums:
                curr_card.total_score = max(valid_cums)

            # 5. Append record to CSV timeline history
            for f_idx in range(1, 11):
                c = curr_card.frames[f_idx]
                self.csv_history_records.append({
                    "timestamp": round(timestamp, 2),
                    "player": p_name,
                    "frame": f"F{f_idx}",
                    "rolls": c.rolls_formatted(),
                    "cumulative": c.cumulative_score if c.cumulative_score is not None else "unplayed",
                    "ttl": curr_card.total_score if curr_card.total_score is not None else "unknown",
                })

        snapshot = {
            "timestamp": round(timestamp, 2),
            "scoreboard_visible": True,
            "players": [p.to_export_dict() for p in self.current_players.values()],
        }
        self.state_timeline.append(snapshot)
        return snapshot

    def _vote_consensus(self, history: deque) -> Optional[str]:
        """Confidence-weighted voting over sliding history."""
        if not history:
            return None

        counts = Counter()
        weights: Dict[str, float] = {}

        for val, w in history:
            counts[val] += 1
            weights[val] = weights.get(val, 0.0) + w

        best_val, _ = max(weights.items(), key=lambda x: x[1])
        if counts[best_val] >= 2 or len(history) == 1:
            return best_val

        return None
