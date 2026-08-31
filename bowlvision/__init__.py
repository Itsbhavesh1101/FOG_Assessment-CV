"""Computer vision scoreboard data extraction framework."""

from .core.config import DEFAULT_SCOREBOARD_ROI, INITIAL_PLAYER_MAP, PipelineConfig
from .core.models import FrameCell, FrameObservation, PlayerScorecard
from .core.types import BoundingBox, OCRItem, RollSymbol, VisibilityStatus
from .vision.video_stream import StreamMetadata, VideoFrameSample, VideoStream
from .vision.cutaway_detector import CutawayDetector
from .vision.image_enhancer import ImageEnhancer
from .ocr.ocr_manager import OCRManager
from .spatial.grid_layout import COLUMN_BOUNDS, SCOREBOARD_ROWS
from .spatial.player_tracker import PlayerTracker
from .spatial.cell_mapper import SpatialGridMapper
from .analytics.bowling_rules import BowlingRules
from .analytics.temporal_aggregator import TemporalScoreboardTracker
from .export.json_exporter import serialize_match_json
from .export.csv_exporter import export_timeline_history_csv, serialize_match_csv
from .export.visualizer import ScoreboardVisualizer
from .export.video_annotator import VideoAnnotator
from .pipeline import BowlVisionPipeline

__version__ = "2.0.0"
__author__ = "Computer Vision Engineering Team"

__all__ = [
    "PipelineConfig",
    "DEFAULT_SCOREBOARD_ROI",
    "INITIAL_PLAYER_MAP",
    "FrameCell",
    "PlayerScorecard",
    "FrameObservation",
    "BoundingBox",
    "OCRItem",
    "RollSymbol",
    "VisibilityStatus",
    "VideoStream",
    "StreamMetadata",
    "VideoFrameSample",
    "CutawayDetector",
    "ImageEnhancer",
    "OCRManager",
    "SCOREBOARD_ROWS",
    "COLUMN_BOUNDS",
    "PlayerTracker",
    "SpatialGridMapper",
    "BowlingRules",
    "TemporalScoreboardTracker",
    "serialize_match_json",
    "serialize_match_csv",
    "export_timeline_history_csv",
    "ScoreboardVisualizer",
    "VideoAnnotator",
    "BowlVisionPipeline",
]

