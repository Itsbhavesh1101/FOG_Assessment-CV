from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class RowDefinition:
    row_index: int
    y_min: int
    y_max: int
    split_y: int  # Y coordinate splitting upper roll boxes from lower cumulative boxes

    def contains_y(self, y: float) -> bool:
        return self.y_min <= y < self.y_max

    def is_roll_section(self, y: float) -> bool:
        return y < self.split_y


# Calibrated overhead scoreboard row partitioning
SCOREBOARD_ROWS: List[RowDefinition] = [
    RowDefinition(row_index=1, y_min=135, y_max=290, split_y=205),
    RowDefinition(row_index=2, y_min=290, y_max=460, split_y=370),
    RowDefinition(row_index=3, y_min=460, y_max=630, split_y=535),
    RowDefinition(row_index=4, y_min=630, y_max=830, split_y=700),
]

# Calibrated column horizontal bounds
COLUMN_BOUNDS: Dict[str, Tuple[int, int]] = {
    "NAME": (0, 200),
    "F1": (200, 340),
    "F2": (340, 480),
    "F3": (480, 620),
    "F4": (620, 760),
    "F5": (760, 900),
    "F6": (900, 1040),
    "F7": (1040, 1180),
    "F8": (1180, 1320),
    "F9": (1320, 1460),
    "F10": (1460, 1630),
    "TTL": (1630, 1820),
}


def find_row_for_y(y: float) -> Optional[RowDefinition]:
    for row in SCOREBOARD_ROWS:
        if row.contains_y(y):
            return row
    return None


def find_column_for_x(x: float) -> str:
    for col_name, (x_min, x_max) in COLUMN_BOUNDS.items():
        if x_min <= x < x_max:
            return col_name
    if x >= COLUMN_BOUNDS["TTL"][0]:
        return "TTL"
    return "NAME"
