from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple


class VisibilityStatus(str, Enum):
    VISIBLE = "VISIBLE"
    CUTAWAY = "CUTAWAY"
    UNCERTAIN = "UNCERTAIN"


class RollSymbol(str, Enum):
    STRIKE = "X"
    SPARE = "/"
    GUTTER = "-"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class BoundingBox:
    """Represents a 2D bounding box defined by 4 corner points or (x1, y1, x2, y2)."""
    x1: float
    y1: float
    x2: float
    y2: float

    @classmethod
    def from_polygon(cls, poly: List[List[float]]) -> "BoundingBox":
        xs = [float(pt[0]) for pt in poly]
        ys = [float(pt[1]) for pt in poly]
        return cls(x1=min(xs), y1=min(ys), x2=max(xs), y2=max(ys))

    @property
    def center_x(self) -> float:
        return (self.x1 + self.x2) / 2.0

    @property
    def center_y(self) -> float:
        return (self.y1 + self.y2) / 2.0

    @property
    def width(self) -> float:
        return max(0.0, self.x2 - self.x1)

    @property
    def height(self) -> float:
        return max(0.0, self.y2 - self.y1)

    def to_points(self) -> List[List[int]]:
        return [
            [int(self.x1), int(self.y1)],
            [int(self.x2), int(self.y1)],
            [int(self.x2), int(self.y2)],
            [int(self.x1), int(self.y2)],
        ]


@dataclass
class OCRItem:
    """Standardized representation of a single OCR detected token."""
    text: str
    confidence: float
    bbox: BoundingBox
    raw_polygon: Optional[List[List[float]]] = None

    def as_dict(self) -> dict:
        return {
            "text": self.text,
            "confidence": round(self.confidence, 4),
            "bbox": self.bbox.to_points(),
        }
