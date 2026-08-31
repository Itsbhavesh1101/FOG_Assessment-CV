#!/usr/bin/env python3
"""Compatibility wrapper for the BowlVision CLI."""

import sys

from bowlvision.cli import main


if __name__ == "__main__":
    sys.exit(main())

