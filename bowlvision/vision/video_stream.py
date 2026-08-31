import cv2
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional, Tuple
import numpy as np


@dataclass(frozen=True)
class StreamMetadata:
    width: int
    height: int
    fps: float
    total_frames: int
    duration_sec: float


@dataclass
class VideoFrameSample:
    frame_index: int
    sample_index: int
    timestamp_sec: float
    image_bgr: np.ndarray


class VideoStream:
    """Manages video file reading and uniform temporal downsampling."""

    def __init__(self, video_path: Path):
        self.video_path = Path(video_path)
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file does not exist: {self.video_path}")
        self._meta = self._probe_metadata()

    @property
    def metadata(self) -> StreamMetadata:
        return self._meta

    def _probe_metadata(self) -> StreamMetadata:
        cap = cv2.VideoCapture(str(self.video_path))
        if not cap.isOpened():
            raise IOError(f"Failed to open video source: {self.video_path}")
        try:
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = float(cap.get(cv2.CAP_PROP_FPS) or 30.0)
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total / fps if fps > 0 else 0.0
            return StreamMetadata(
                width=width,
                height=height,
                fps=fps,
                total_frames=total,
                duration_sec=duration,
            )
        finally:
            cap.release()

    def sample_step(self, target_fps: float) -> int:
        """Calculates frame stride for the target sampling FPS."""
        if target_fps <= 0:
            return 1
        return max(1, int(round(self._meta.fps / target_fps)))

    def iter_samples(self, target_fps: float = 5.0) -> Iterator[VideoFrameSample]:
        """Yields temporally sampled frames with frame indexes and timestamps."""
        step = self.sample_step(target_fps)
        cap = cv2.VideoCapture(str(self.video_path))
        if not cap.isOpened():
            raise IOError(f"Could not open stream for iteration: {self.video_path}")

        frame_idx = 0
        sample_idx = 0
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret or frame is None:
                    break

                if frame_idx % step == 0:
                    sample_idx += 1
                    timestamp = round(frame_idx / self._meta.fps, 2)
                    yield VideoFrameSample(
                        frame_index=frame_idx,
                        sample_index=sample_idx,
                        timestamp_sec=timestamp,
                        image_bgr=frame,
                    )
                frame_idx += 1
        finally:
            cap.release()
