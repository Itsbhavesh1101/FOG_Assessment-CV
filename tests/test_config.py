import argparse
import unittest
from pathlib import Path
from bowlvision.cli import build_parser
from bowlvision.core.config import PipelineConfig, DEFAULT_SCOREBOARD_ROI


class TestPipelineConfig(unittest.TestCase):
    def test_default_config_values(self):
        cfg = PipelineConfig()
        self.assertEqual(cfg.video_path, Path("bowling_scoreboard.mp4"))
        self.assertEqual(cfg.sample_fps, 5.0)
        self.assertEqual(cfg.roi, DEFAULT_SCOREBOARD_ROI)
        self.assertEqual(cfg.ocr_engine, "auto")

    def test_from_cli_args(self):
        args = argparse.Namespace(
            video="test_match.mp4",
            output_dir="out_test",
            debug_dir="dbg_test",
            sample_fps=3.0,
            roi=[10, 500, 20, 900],
            ocr_engine="rapidocr",
            window_size=7,
            min_confidence=0.6,
            ocr_cache_diff_threshold=3.5,
            render_video=True,
            save_crops=False,
            debug_preprocessed_limit=10,
        )
        cfg = PipelineConfig.from_cli_args(args)
        self.assertEqual(cfg.video_path, Path("test_match.mp4"))
        self.assertEqual(cfg.output_dir, Path("out_test"))
        self.assertEqual(cfg.sample_fps, 3.0)
        self.assertEqual(cfg.roi, (10, 500, 20, 900))
        self.assertEqual(cfg.ocr_engine, "rapidocr")
        self.assertEqual(cfg.temporal_window_size, 7)
        self.assertTrue(cfg.render_annotated_video)

    def test_cli_accepts_canonical_and_legacy_flags(self):
        parser = build_parser()
        args = parser.parse_args(
            [
                "--output_dir",
                "legacy_out",
                "--debug-dir",
                "debug_out",
                "--sample_fps",
                "4.0",
                "--render_video",
                "--debug-crops-limit",
                "12",
            ]
        )

        self.assertEqual(args.output_dir, "legacy_out")
        self.assertEqual(args.debug_dir, "debug_out")
        self.assertEqual(args.sample_fps, 4.0)
        self.assertTrue(args.render_video)
        self.assertEqual(args.debug_preprocessed_limit, 12)

    def test_validation_errors(self):
        cfg = PipelineConfig(video_path=Path("non_existent_file_xyz.mp4"))
        with self.assertRaises(FileNotFoundError):
            cfg.validate()

        cfg_bad_fps = PipelineConfig(video_path=Path("bowling_scoreboard.mp4"), sample_fps=-2.0)
        # Assuming bowling_scoreboard.mp4 exists in test cwd
        if Path("bowling_scoreboard.mp4").exists():
            with self.assertRaises(ValueError):
                cfg_bad_fps.validate()


if __name__ == "__main__":
    unittest.main()
