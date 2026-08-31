import cv2
import numpy as np
from typing import Tuple


class CutawayDetector:
    """
    Classifies video frames between the Overhead Electronic Scoreboard view and
    Camera Cutaways (such as player approach shots, bowler reactions, and pin deck angles).
    
    Uses two complementary visual features:
    1. Grid Edge Density: Digital scoreboard grid lines and LED characters produce high
       edge gradient density (> 0.028) under Canny edge extraction.
    2. Header Luminance Stability: The overhead scoreboard top header region maintains
       a controlled mean luminance (70.0 to 130.0), whereas pin deck ceiling lights or dark
       bowling floor surfaces fall outside this band.
    """

    def __init__(self, default_roi: Tuple[int, int, int, int] = (10, 850, 70, 1890)):
        self.default_roi = default_roi

    def clamp_roi(self, frame_bgr: np.ndarray, roi: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        h, w = frame_bgr.shape[:2]
        ymin, ymax, xmin, xmax = roi
        return (
            max(0, min(int(ymin), h)),
            max(0, min(int(ymax), h)),
            max(0, min(int(xmin), w)),
            max(0, min(int(xmax), w)),
        )

    def crop_scoreboard_roi(self, frame_bgr: np.ndarray, roi: Tuple[int, int, int, int] = None) -> np.ndarray:
        if frame_bgr is None or frame_bgr.size == 0:
            return np.empty((0, 0, 3), dtype=np.uint8)

        active_roi = roi or self.default_roi
        ymin, ymax, xmin, xmax = self.clamp_roi(frame_bgr, active_roi)
        if ymin >= ymax or xmin >= xmax:
            return np.empty((0, 0, 3), dtype=frame_bgr.dtype)

        return frame_bgr[ymin:ymax, xmin:xmax]

    def is_scoreboard_visible(self, frame_bgr: np.ndarray, roi: Tuple[int, int, int, int] = None) -> bool:
        """
        Returns True if the frame presents a valid overhead scoreboard display,
        False if it represents a cutaway camera angle or occluded frame.
        """
        if frame_bgr is None or frame_bgr.size == 0:
            return False

        cropped = self.crop_scoreboard_roi(frame_bgr, roi)
        if cropped.size == 0:
            return False

        gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape[:2]

        # Top header region [y: 30-130, x: 1500-1800]
        y1, y2 = min(30, h), min(130, h)
        x1, x2 = min(1500, w), min(1800, w)
        if y1 >= y2 or x1 >= x2:
            return False

        hdr_patch = gray[y1:y2, x1:x2]
        hdr_luminance = float(np.mean(hdr_patch))

        # Full ROI Canny edge density
        edges = cv2.Canny(gray, threshold1=50, threshold2=150)
        edge_density = float(np.mean(edges > 0))

        # Classification decision boundaries
        is_visible = (edge_density > 0.028) and (70.0 <= hdr_luminance <= 130.0)
        return bool(is_visible)
