import unittest
from bowlvision.analytics.bowling_rules import BowlingRules


class TestOCRSanitizer(unittest.TestCase):
    def test_strike_normalization(self):
        self.assertEqual(BowlingRules.normalize_roll_token("X"), "X")
        self.assertEqual(BowlingRules.normalize_roll_token("x"), "X")
        self.assertEqual(BowlingRules.normalize_roll_token("STRIKE"), "X")

    def test_spare_normalization(self):
        self.assertEqual(BowlingRules.normalize_roll_token("4/"), "4/")
        self.assertEqual(BowlingRules.normalize_roll_token("1/"), "1/")
        self.assertEqual(BowlingRules.normalize_roll_token("/"), "/")

    def test_open_and_gutter_normalization(self):
        self.assertEqual(BowlingRules.normalize_roll_token("-"), "-")
        self.assertEqual(BowlingRules.normalize_roll_token("--"), "-")
        self.assertEqual(BowlingRules.normalize_roll_token("8-"), "8-")
        self.assertEqual(BowlingRules.normalize_roll_token("9-"), "9-")
        self.assertEqual(BowlingRules.normalize_roll_token("6-"), "6-")
        self.assertEqual(BowlingRules.normalize_roll_token("5-"), "5-")

    def test_seven_segment_digital_font_artifacts(self):
        # 71 is a common OCR segmentation error for '8-'
        self.assertEqual(BowlingRules.normalize_roll_token("71"), "8-")
        # 81 confusion for '9-'
        self.assertEqual(BowlingRules.normalize_roll_token("81"), "9-")
        # 61 confusion for '6-'
        self.assertEqual(BowlingRules.normalize_roll_token("61"), "6-")

    def test_invalid_tokens(self):
        self.assertIsNone(BowlingRules.normalize_roll_token(""))
        self.assertIsNone(BowlingRules.normalize_roll_token("unknown"))
        self.assertIsNone(BowlingRules.normalize_roll_token("???"))


if __name__ == "__main__":
    unittest.main()
