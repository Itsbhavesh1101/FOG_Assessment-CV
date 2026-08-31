import unittest
from bowlvision.analytics.bowling_rules import BowlingRules


class TestBowlingRules(unittest.TestCase):
    def test_parse_pin_count(self):
        self.assertEqual(BowlingRules.parse_pin_count("X"), 10)
        self.assertEqual(BowlingRules.parse_pin_count("8-"), 8)
        self.assertEqual(BowlingRules.parse_pin_count("9-"), 9)
        self.assertEqual(BowlingRules.parse_pin_count("5-"), 5)
        self.assertEqual(BowlingRules.parse_pin_count("-"), 0)

    def test_compute_frame_score(self):
        # Vishal completes Frame 5 after having Frame 4 cumulative = 28 and roll = 9-
        new_cum = BowlingRules.compute_frame_score(prev_cumulative=28, roll_str="9-")
        self.assertEqual(new_cum, 37)


if __name__ == "__main__":
    unittest.main()
