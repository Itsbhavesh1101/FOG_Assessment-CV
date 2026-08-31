"""Command-line interface for BowlVision."""

from __future__ import annotations

import argparse
import sys

from . import DEFAULT_SCOREBOARD_ROI, BowlVisionPipeline, PipelineConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bowlvision",
        description=(
            "Extract structured match statistics and player scores from "
            "bowling broadcast video using computer vision and OCR."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--video",
        type=str,
        default="bowling_scoreboard.mp4",
        help="Path to input bowling match video file.",
    )
    parser.add_argument(
        "--output-dir",
        "--output_dir",
        dest="output_dir",
        type=str,
        default="output",
        help="Directory for JSON, CSV, and optional video exports.",
    )
    parser.add_argument(
        "--debug-dir",
        "--debug_dir",
        dest="debug_dir",
        type=str,
        default="debug",
        help="Directory for debug crops and inspection artifacts.",
    )
    parser.add_argument(
        "--sample-fps",
        "--sample_fps",
        dest="sample_fps",
        type=float,
        default=5.0,
        help="Frame sampling frequency for OCR analysis.",
    )
    parser.add_argument(
        "--roi",
        type=int,
        nargs=4,
        metavar=("YMIN", "YMAX", "XMIN", "XMAX"),
        default=DEFAULT_SCOREBOARD_ROI,
        help="Scoreboard ROI coordinates in full-frame space.",
    )
    parser.add_argument(
        "--ocr-engine",
        "--ocr_engine",
        dest="ocr_engine",
        choices=["auto", "rapidocr", "paddleocr", "pytesseract"],
        default="auto",
        help="OCR backend preference.",
    )
    parser.add_argument(
        "--window-size",
        "--window_size",
        dest="window_size",
        type=int,
        default=5,
        help="Temporal consensus window size.",
    )
    parser.add_argument(
        "--min-confidence",
        "--min_confidence",
        dest="min_confidence",
        type=float,
        default=0.45,
        help="Minimum OCR confidence accepted by temporal tracking.",
    )
    parser.add_argument(
        "--ocr-cache-diff-threshold",
        "--ocr_cache_diff_threshold",
        dest="ocr_cache_diff_threshold",
        type=float,
        default=4.0,
        help="Mean pixel-difference threshold for reusing OCR on unchanged crops.",
    )
    parser.add_argument(
        "--render-video",
        "--render_video",
        dest="render_video",
        action="store_true",
        help="Render annotated MP4 demo video with telemetry overlay.",
    )
    parser.add_argument(
        "--live",
        "--show-live",
        "--show_live",
        dest="show_live",
        action="store_true",
        help="Display a live interactive playback window.",
    )
    parser.add_argument(
        "--save-crops",
        "--save_crops",
        dest="save_crops",
        action="store_true",
        help="Save preprocessed ROI crops to the debug directory.",
    )
    parser.add_argument(
        "--debug-crops-limit",
        "--debug_preprocessed_limit",
        dest="debug_preprocessed_limit",
        type=int,
        default=50,
        help="Maximum number of debug crops to write; -1 keeps all.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        config = PipelineConfig.from_cli_args(args)
        BowlVisionPipeline(config).run()
    except KeyboardInterrupt:
        print("\n[!] Execution interrupted by user.")
        return 130
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"\n[ERROR] {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"\n[UNEXPECTED ERROR] {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

