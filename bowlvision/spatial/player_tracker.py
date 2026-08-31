import re
from typing import Dict, List, Optional, Tuple
import numpy as np
from ..core.types import OCRItem


class PlayerTracker:
    """
    Identifies active player highlights and resolves dynamic player names
    from broadcast header graphics and row indicators.
    """

    INDICATOR_ROW_BINS = [
        (1, 140, 280),
        (2, 295, 435),
        (3, 450, 590),
        (4, 610, 750),
    ]

    def detect_active_highlight_row(self, crop_bgr: np.ndarray) -> Optional[int]:
        """
        Determines which player row (1..4) has the active bowler yellow indicator.
        The yellow patch is characterized by high Red & Green channels and low Blue channel.
        """
        if crop_bgr is None or crop_bgr.size == 0:
            return None

        h, w = crop_bgr.shape[:2]
        indicator_width = min(120, w)
        yellow_scores: List[Tuple[int, float]] = []

        for row_idx, y1, y2 in self.INDICATOR_ROW_BINS:
            if y2 > h:
                continue

            patch = crop_bgr[y1:y2, 10:indicator_width]
            if patch.size == 0:
                continue

            b = patch[:, :, 0].astype(np.float32)
            g = patch[:, :, 1].astype(np.float32)
            r = patch[:, :, 2].astype(np.float32)

            # Yellow chroma metric: ((R + G) / 2) - B
            score = float(np.mean(((r + g) / 2.0) - b))
            yellow_scores.append((row_idx, score))

        if not yellow_scores:
            return None

        best_row, best_score = max(yellow_scores, key=lambda x: x[1])
        if best_score > 50.0:
            return best_row
        return None

    def extract_header_name(self, ocr_items: List[OCRItem]) -> Optional[str]:
        """
        Extracts active bowler full name from the broadcast header banner
        (Y: [10, 100], X: [150, 600]).
        """
        candidates = []
        for item in ocr_items:
            bbox = item.bbox
            cy = bbox.center_y
            cx = bbox.center_x
            text = item.text.strip().upper()

            if 10 <= cy <= 100 and 150 <= cx <= 600:
                clean = re.sub(r"[^A-Z]", "", text)
                if len(clean) >= 3 and clean not in ["TTL", "LANE", "FRAME", "GAME"]:
                    candidates.append((clean, item.confidence))

        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]

        return None
