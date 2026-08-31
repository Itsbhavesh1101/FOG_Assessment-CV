import re
from typing import Dict, List, Optional, Tuple
from ..core.models import PlayerScorecard
from ..core.types import OCRItem
from .grid_layout import find_column_for_x, find_row_for_y, SCOREBOARD_ROWS


class SpatialGridMapper:
    """
    Assigns OCR detections to the 2D matrix of 4 Player Rows × 10 Frames + TTL.
    Handles sub-cell roll vs. cumulative classification and multi-column token splitting.
    """

    def __init__(self, header_y_min: int = 135, footer_y_max: int = 830):
        self.header_y_min = header_y_min
        self.footer_y_max = footer_y_max

    def _split_text_by_columns(self, text: str, x1: float, x2: float) -> Dict[str, str]:
        """
        Splits merged OCR text strings across frame column intervals
        using proportional character coordinate assignment.
        """
        clean = text.replace(" ", "")
        if not clean:
            return {}

        char_w = (x2 - x1) / len(clean)
        col_chunks: Dict[str, List[str]] = {}
        current_col: Optional[str] = None
        current_chars: List[str] = []

        for i, ch in enumerate(clean):
            cx = x1 + (i + 0.5) * char_w
            col = find_column_for_x(cx)
            if col != current_col:
                if current_col and current_chars:
                    col_chunks[current_col] = current_chars
                current_col = col
                current_chars = [ch]
            else:
                current_chars.append(ch)

        if current_col and current_chars:
            col_chunks[current_col] = current_chars

        return {col: "".join(chars) for col, chars in col_chunks.items()}

    def map_detections_to_scorecards(
        self,
        ocr_items: List[OCRItem],
        player_names: Dict[int, str],
    ) -> Dict[str, PlayerScorecard]:
        """
        Maps a list of raw OCR items from a scoreboard crop into structured PlayerScorecard objects.
        """
        scorecards: Dict[int, PlayerScorecard] = {}
        for row in SCOREBOARD_ROWS:
            r_idx = row.row_index
            name = player_names.get(r_idx, f"PLAYER_{r_idx}")
            scorecards[r_idx] = PlayerScorecard(row_index=r_idx, name=name)

        for item in ocr_items:
            bbox = item.bbox
            cy = bbox.center_y
            cx = bbox.center_x
            text = item.text.strip()
            conf = item.confidence

            # Skip header or footer regions
            if cy < self.header_y_min or cy >= self.footer_y_max:
                continue

            row_def = find_row_for_y(cy)
            if row_def is None:
                continue

            card = scorecards[row_def.row_index]
            is_roll_section = row_def.is_roll_section(cy)

            # Check if this detection is in the TTL column
            col_simple = find_column_for_x(cx)
            if col_simple == "TTL":
                digits = re.sub(r"[^0-9]", "", text)
                if digits and int(digits) > 0:
                    card.total_score = int(digits)
                continue
            elif col_simple == "NAME":
                continue

            # Process tokens and multi-column merged tokens
            assignments = self._split_text_by_columns(text, bbox.x1, bbox.x2)

            for col_name, sub_text in assignments.items():
                if col_name == "TTL":
                    digits = re.sub(r"[^0-9]", "", sub_text)
                    if digits and int(digits) > 0:
                        card.total_score = int(digits)
                elif col_name.startswith("F"):
                    try:
                        f_num = int(col_name[1:])
                    except ValueError:
                        continue

                    if not (1 <= f_num <= 10):
                        continue

                    cell = card.frames[f_num]
                    cell.raw_ocr_items.append(item)

                    if is_roll_section:
                        cell.rolls.append(sub_text)
                    else:
                        digits = re.sub(r"[^0-9]", "", sub_text)
                        if digits and digits.isdigit():
                            val = int(digits)
                            # Single frame cumulative score must be in a realistic bowling range
                            if 0 < val <= 300:
                                cell.cumulative_score = val

        return {card.name: card for card in scorecards.values()}
