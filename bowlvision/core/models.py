from dataclasses import dataclass, field
from typing import Dict, List, Optional
from .types import OCRItem


@dataclass
class FrameCell:
    """Represents a single frame (1-10) for a player."""
    frame_number: int
    rolls: List[str] = field(default_factory=list)
    cumulative_score: Optional[int] = None
    raw_ocr_items: List[OCRItem] = field(default_factory=list)

    @property
    def is_played(self) -> bool:
        return bool(self.rolls) or self.cumulative_score is not None

    def rolls_formatted(self) -> str:
        return "/".join(self.rolls) if self.rolls else "-"

    def to_export_dict(self) -> Optional[dict]:
        if not self.is_played:
            return None
        return {
            "rolls": self.rolls,
            "cumulative": self.cumulative_score,
        }


@dataclass
class PlayerScorecard:
    """Represents full scorecard for a single player."""
    row_index: int
    name: str
    name_confidence: float = 1.0
    frames: Dict[int, FrameCell] = field(default_factory=dict)
    total_score: Optional[int] = None
    is_active: bool = False

    def __post_init__(self):
        if not self.frames:
            self.frames = {i: FrameCell(frame_number=i) for i in range(1, 11)}

    def to_export_dict(self) -> dict:
        return {
            "name": self.name,
            "frames": {
                str(num): cell.to_export_dict()
                for num, cell in self.frames.items()
            },
            "ttl": self.total_score if self.total_score is not None else "unknown",
        }


@dataclass
class FrameObservation:
    """Snapshot of analysis for a single video timestamp."""
    timestamp: float
    is_scoreboard_visible: bool
    ocr_items: List[OCRItem] = field(default_factory=list)
    players: Dict[str, PlayerScorecard] = field(default_factory=dict)
    reused_cache: bool = False
