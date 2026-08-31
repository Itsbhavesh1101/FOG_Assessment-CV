#!/usr/bin/env python3
"""Launch the BowlVision live interactive scoreboard demo."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bowlvision.cli import main as run_cli


def main() -> int:
    return run_cli(
        [
            "--video",
            "bowling_scoreboard.mp4",
            "--output-dir",
            "output",
            "--sample-fps",
            "5.0",
            "--render-video",
            "--live",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
