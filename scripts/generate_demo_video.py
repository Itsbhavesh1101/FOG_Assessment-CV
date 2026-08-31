#!/usr/bin/env python3
"""
BowlVision Demo Video Generator
Renders an annotated video showcasing live scoreboard localization, OCR token detection,
cutaway camera switching, and dynamic score tracking.
"""
import argparse
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bowlvision import BowlVisionPipeline, PipelineConfig


def main():
    parser = argparse.ArgumentParser(description="Render annotated demonstration video")
    parser.add_argument("--video", type=str, default="bowling_scoreboard.mp4", help="Input video")
    parser.add_argument("--output-dir", type=str, default="output", help="Output directory")
    parser.add_argument("--sample-fps", type=float, default=5.0, help="Sampling FPS")
    args = parser.parse_args()

    config = PipelineConfig(
        video_path=Path(args.video),
        output_dir=Path(args.output_dir),
        sample_fps=args.sample_fps,
        render_annotated_video=True,
    )

    pipeline = BowlVisionPipeline(config)
    pipeline.run()


if __name__ == "__main__":
    main()
