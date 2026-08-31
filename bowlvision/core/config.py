from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Tuple

# Calibrated Default ROI for 1080p full HD broadcast overhead camera
# Format: (YMIN, YMAX, XMIN, XMAX)
DEFAULT_SCOREBOARD_ROI: Tuple[int, int, int, int] = (10, 850, 70, 1890)

INITIAL_PLAYER_MAP: Dict[int, str] = {
    1: "JAGDISH",
    2: "VISHAL",
    3: "P (Player 3)",
    4: "TARUN",
}


@dataclass
class PipelineConfig:
    """Master configuration for the Scoreboard CV & OCR pipeline."""
    video_path: Path = Path("bowling_scoreboard.mp4")
    output_dir: Path = Path("output")
    debug_dir: Path = Path("debug")
    sample_fps: float = 5.0
    roi: Tuple[int, int, int, int] = DEFAULT_SCOREBOARD_ROI
    ocr_engine: str = "auto"  # 'auto', 'rapidocr', 'pytesseract', 'paddleocr'
    temporal_window_size: int = 5
    min_ocr_confidence: float = 0.45
    ocr_cache_threshold: float = 4.0
    render_annotated_video: bool = False
    show_live: bool = False
    save_debug_crops: bool = False
    debug_crops_limit: int = 50

    @classmethod
    def from_dict(cls, data: dict) -> "PipelineConfig":
        cfg = cls()
        for k, v in data.items():
            if hasattr(cfg, k):
                if k in ("video_path", "output_dir", "debug_dir") and isinstance(v, str):
                    setattr(cfg, k, Path(v))
                elif k == "roi" and isinstance(v, (list, tuple)):
                    setattr(cfg, k, tuple(v))
                else:
                    setattr(cfg, k, v)
        return cfg

    @classmethod
    def from_cli_args(cls, args) -> "PipelineConfig":
        return cls(
            video_path=Path(getattr(args, "video", "bowling_scoreboard.mp4")),
            output_dir=Path(getattr(args, "output_dir", "output")),
            debug_dir=Path(getattr(args, "debug_dir", "debug")),
            sample_fps=float(getattr(args, "sample_fps", 5.0)),
            roi=tuple(getattr(args, "roi", DEFAULT_SCOREBOARD_ROI)),
            ocr_engine=str(getattr(args, "ocr_engine", "auto")),
            temporal_window_size=int(getattr(args, "window_size", 5)),
            min_ocr_confidence=float(getattr(args, "min_confidence", 0.45)),
            ocr_cache_threshold=float(getattr(args, "ocr_cache_diff_threshold", 4.0)),
            render_annotated_video=bool(getattr(args, "render_video", False)),
            show_live=bool(getattr(args, "show_live", False) or getattr(args, "live", False)),
            save_debug_crops=bool(getattr(args, "save_crops", False)),
            debug_crops_limit=int(getattr(args, "debug_preprocessed_limit", -1)),
        )

    def validate(self) -> None:
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found at '{self.video_path.resolve()}'")
        if self.sample_fps <= 0:
            raise ValueError(f"sample_fps must be positive, got {self.sample_fps}")
        if len(self.roi) != 4:
            raise ValueError(f"ROI must contain exactly 4 values (ymin, ymax, xmin, xmax), got {self.roi}")
        ymin, ymax, xmin, xmax = self.roi
        if ymin >= ymax or xmin >= xmax:
            raise ValueError(f"Invalid ROI boundaries: y=[{ymin}:{ymax}], x=[{xmin}:{xmax}]")

    def get_initial_player_names(self) -> Dict[int, str]:
        return dict(INITIAL_PLAYER_MAP)
