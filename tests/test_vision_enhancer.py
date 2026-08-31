import unittest
import numpy as np
from bowlvision.vision.cutaway_detector import CutawayDetector
from bowlvision.vision.image_enhancer import ImageEnhancer


class TestVisionEnhancer(unittest.TestCase):
    def setUp(self):
        self.detector = CutawayDetector()
        self.enhancer = ImageEnhancer()

    def test_empty_frame_handling(self):
        empty = np.empty((0, 0, 3), dtype=np.uint8)
        self.assertFalse(self.detector.is_scoreboard_visible(empty))
        self.assertEqual(self.detector.crop_scoreboard_roi(empty).size, 0)
        self.assertEqual(self.enhancer.enhance_for_ocr(empty).size, 0)

    def test_synthetic_cutaway_detection(self):
        # Blank black or dark frame (typical of poorly lit camera transition or lane floor)
        dark_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        self.assertFalse(self.detector.is_scoreboard_visible(dark_frame))

        # Uniform white overexposed frame
        bright_frame = np.ones((1080, 1920, 3), dtype=np.uint8) * 255
        self.assertFalse(self.detector.is_scoreboard_visible(bright_frame))

    def test_image_enhancement_clahe_bilateral(self):
        # Test synthetic crop enhancement output dimensions and type
        synthetic_crop = np.random.randint(50, 200, size=(840, 1820, 3), dtype=np.uint8)
        enhanced = self.enhancer.enhance_for_ocr(synthetic_crop)
        self.assertEqual(enhanced.shape, (840, 1820))
        self.assertEqual(enhanced.dtype, np.uint8)


if __name__ == "__main__":
    unittest.main()
