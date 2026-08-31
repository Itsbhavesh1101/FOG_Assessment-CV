import re
from typing import List, Optional, Tuple


class BowlingRules:
    """
    Encapsulates 10-pin bowling domain rules and OCR symbol normalization.
    """

    @staticmethod
    def normalize_roll_token(raw_text: str) -> Optional[str]:
        """
        Normalizes OCR strings into standard bowling roll symbols:
        - Strikes: 'X'
        - Spares: '4/', '1/', etc.
        - Misses / Open pins: '8-', '9-', '6-', '5-', '3-', etc.
        - Gutter: '-'
        """
        if not raw_text:
            return None

        clean = raw_text.strip().upper()
        if not clean or "UNKNOWN" in clean:
            return None

        if clean in ("X", "STRIKE", "XX"):
            return "X"

        if "/" in clean:
            match = re.search(r"([0-9]/)", clean)
            if match:
                return match.group(1)
            return "/"

        if clean in ("-", "--"):
            return "-"

        # Common digital 7-segment OCR confusions
        if clean == "71":
            return "8-"
        if clean == "81":
            return "9-"
        if clean == "61":
            return "6-"

        if re.match(r"^[1-9]-$", clean):
            return clean

        if re.match(r"^[1-9]$", clean):
            return f"{clean}-"

        if re.match(r"^[0-9X/\-]{1,3}$", clean):
            return clean

        return None

    @staticmethod
    def parse_pin_count(roll_str: str) -> int:
        """Parses the pin count from an open or single roll symbol."""
        if not roll_str or roll_str in ("-", "--"):
            return 0
        if roll_str == "X":
            return 10
        digits = re.sub(r"[^0-9]", "", roll_str)
        if digits:
            return int(digits[0])
        return 0

    @staticmethod
    def compute_frame_score(prev_cumulative: int, roll_str: str) -> int:
        """Calculates expected cumulative score given previous cumulative and new roll."""
        pins = BowlingRules.parse_pin_count(roll_str)
        return prev_cumulative + pins
