#!/usr/bin/env python3
"""
BowlVision Frame Inspection & Debug Tool
Extracts and performs OCR on a frame at a specific timestamp.
"""
import argparse
import sys
from pathlib import Path
import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bowlvision.vision.cutaway_detector import CutawayDetector
from bowlvision.vision.image_enhancer import ImageEnhancer
from bowlvision.ocr.ocr_manager import OCRManager
from bowlvision.spatial.player_tracker import PlayerTracker
from bowlvision.spatial.cell_mapper import SpatialGridMapper


def inspect_timestamp(video_path: str, timestamp_sec: float, output_image: str):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video: {video_path}")
        return

    cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_sec * 1000.0)
    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        print(f"Could not read frame at {timestamp_sec}s")
        return

    detector = CutawayDetector()
    enhancer = ImageEnhancer()
    ocr = OCRManager()
    tracker = PlayerTracker()
    mapper = SpatialGridMapper()

    is_vis = detector.is_scoreboard_visible(frame)
    print(f"--- FRAME AT {timestamp_sec:.2f}s ---")
    print(f"Scoreboard Visible: {is_vis}")

    if is_vis:
        crop = detector.crop_scoreboard_roi(frame)
        enhanced = enhancer.enhance_for_ocr(crop)
        items = ocr.extract_text(enhanced)
        print(f"Detected {len(items)} OCR tokens:")
        for it in items:
            print(f"  - '{it.text}' (Conf: {it.confidence:.3f}, Centroid: ({it.bbox.center_x:.0f}, {it.bbox.center_y:.0f}))")

        active_row = tracker.detect_active_highlight_row(crop)
        header_name = tracker.extract_header_name(items)
        print(f"Active Highlight Row: {active_row}")
        print(f"Header Player Name  : {header_name}")

        cv2.imwrite(output_image, enhanced)
        print(f"Saved enhanced crop to {output_image}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect single frame")
    parser.add_argument("--video", type=str, default="bowling_scoreboard.mp4")
    parser.add_argument("--time", type=float, default=2.0)
    parser.add_argument("--out", type=str, default="debug/inspect_sample.png")
    args = parser.parse_args()

    inspect_timestamp(args.video, args.time, args.out)
