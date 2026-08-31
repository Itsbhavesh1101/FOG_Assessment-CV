import unittest
import numpy as np
from bowlvision.core.types import BoundingBox, OCRItem
from bowlvision.spatial.grid_layout import find_row_for_y, find_column_for_x
from bowlvision.spatial.player_tracker import PlayerTracker
from bowlvision.spatial.cell_mapper import SpatialGridMapper


class TestSpatialGrid(unittest.TestCase):
    def test_grid_layout_mapping(self):
        # Row 1 spans [135, 290)
        row1 = find_row_for_y(200)
        self.assertIsNotNone(row1)
        self.assertEqual(row1.row_index, 1)
        self.assertTrue(row1.is_roll_section(150))
        self.assertFalse(row1.is_roll_section(250))

        # Row 4 spans [630, 830)
        row4 = find_row_for_y(700)
        self.assertIsNotNone(row4)
        self.assertEqual(row4.row_index, 4)

        # Column F1 spans [200, 340)
        self.assertEqual(find_column_for_x(250), "F1")
        # Column F5 spans [760, 900)
        self.assertEqual(find_column_for_x(800), "F5")
        # Column TTL spans >= 1630
        self.assertEqual(find_column_for_x(1700), "TTL")

    def test_player_tracker_yellow_highlight(self):
        tracker = PlayerTracker()
        synthetic_crop = np.zeros((840, 1820, 3), dtype=np.uint8)
        # Background blueish
        synthetic_crop[:, :] = [180, 40, 20]
        # Active yellow indicator in row 2: Y [295, 435], X [10, 120]
        synthetic_crop[295:435, 10:120] = [20, 220, 230]

        active_row = tracker.detect_active_highlight_row(synthetic_crop)
        self.assertEqual(active_row, 2)

    def test_spatial_cell_mapping(self):
        mapper = SpatialGridMapper()
        ocr_items = [
            OCRItem(text="X", confidence=0.99, bbox=BoundingBox(230, 150, 270, 180)),
            OCRItem(text="15", confidence=0.98, bbox=BoundingBox(230, 220, 280, 260)),
            OCRItem(text="31", confidence=0.97, bbox=BoundingBox(1680, 220, 1740, 260)),
        ]
        scorecards = mapper.map_detections_to_scorecards(
            ocr_items=ocr_items,
            player_names={1: "JAGDISH", 2: "VISHAL", 3: "P (Player 3)", 4: "TARUN"},
        )
        jagdish = scorecards["JAGDISH"]
        self.assertEqual(jagdish.frames[1].rolls, ["X"])
        self.assertEqual(jagdish.frames[1].cumulative_score, 15)
        self.assertEqual(jagdish.total_score, 31)


if __name__ == "__main__":
    unittest.main()
