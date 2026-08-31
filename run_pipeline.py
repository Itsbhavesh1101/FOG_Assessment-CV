#!/usr/bin/env python3
"""Backward-compatible wrapper for the BowlVision CLI."""

from bowlvision.cli import main


if __name__ == "__main__":
    raise SystemExit(main())

