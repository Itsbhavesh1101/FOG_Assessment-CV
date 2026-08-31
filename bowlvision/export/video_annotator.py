from pathlib import Path
from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np
from PIL import Image, ImageTk
from ..core.models import PlayerScorecard
from ..core.types import OCRItem


class TkLiveViewer:
    """Lightweight cross-platform GUI window for live video & HUD telemetry preview."""

    def __init__(self, title: str = "BowlVision — Live Scoreboard Telemetry", size: tuple = (1280, 720)):
        import tkinter as tk
        self.root = tk.Tk()
        self.root.title(title)
        self.width, self.height = size
        self.root.geometry(f"{self.width}x{self.height}")
        self.root.configure(bg="#111111")
        self.label = tk.Label(self.root, bg="#111111")
        self.label.pack(fill=tk.BOTH, expand=True)
        self._is_closed = False
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.bind("<Escape>", lambda e: self._on_close())
        self.root.bind("q", lambda e: self._on_close())
        self.photo = None

    def _on_close(self):
        self._is_closed = True
        try:
            self.root.destroy()
        except Exception:
            pass

    def update_frame(self, frame_bgr: np.ndarray) -> bool:
        if self._is_closed:
            return False

        try:
            rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            resized = cv2.resize(rgb, (self.width, self.height))
            img = Image.fromarray(resized)
            self.photo = ImageTk.PhotoImage(image=img)
            self.label.config(image=self.photo)
            self.root.update_idletasks()
            self.root.update()
            return True
        except Exception:
            self._is_closed = True
            return False

    def close(self):
        if not self._is_closed:
            self._on_close()


class VideoAnnotator:
    """
    Renders diagnostic overlays and real-time scoreboard HUD onto video frames,
    producing an annotated video demonstration and live interactive visualization.
    """

    def __init__(
        self,
        output_path: Optional[Path] = None,
        fps: float = 30.0,
        frame_size: tuple = (1920, 1080),
        show_window: bool = False,
    ):
        self.output_path = Path(output_path) if output_path else None
        self.fps = fps
        self.frame_size = frame_size
        self.show_window = show_window
        self.writer: Optional[cv2.VideoWriter] = None
        self.viewer: Optional[TkLiveViewer] = None

        if self.output_path:
            self._init_writer()

        if self.show_window:
            self._init_viewer()

    def _init_writer(self):
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.writer = cv2.VideoWriter(
            str(self.output_path),
            fourcc,
            self.fps,
            self.frame_size,
        )

    def _init_viewer(self):
        try:
            self.viewer = TkLiveViewer(title="BowlVision — Live Scoreboard Telemetry", size=(1280, 720))
        except Exception as e:
            print(f"[!] Warning initializing GUI viewer: {e}")
            self.viewer = None

    def annotate_frame(
        self,
        frame_bgr: np.ndarray,
        timestamp: float,
        is_visible: bool,
        ocr_items: List[OCRItem],
        players: Dict[str, PlayerScorecard],
        active_row: Optional[int] = None,
        roi_coords: Tuple[int, int, int, int] = (10, 850, 70, 1890),  # (ymin, ymax, xmin, xmax)
    ) -> np.ndarray:
        """Draws bounding boxes, grid annotations, status badge, and scoreboard HUD onto frame."""
        annotated = frame_bgr.copy()
        ymin, ymax, xmin, xmax = roi_coords

        # 1. Top Status Banner
        status_color = (0, 220, 0) if is_visible else (0, 0, 240)
        status_text = f"SCOREBOARD: {'ACTIVE / DETECTED' if is_visible else 'CAMERA CUTAWAY (STATE FROZEN)'}  |  TIME: {timestamp:05.1f}s"
        cv2.rectangle(annotated, (15, 12), (1050, 56), (15, 15, 15), -1)
        cv2.rectangle(annotated, (15, 12), (1050, 56), status_color, 2)
        cv2.putText(
            annotated,
            status_text,
            (30, 42),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            status_color,
            2,
            cv2.LINE_AA,
        )

        if is_visible:
            # 2. Draw Scoreboard ROI Boundary Box
            cv2.rectangle(annotated, (xmin, ymin), (xmax, ymax), (255, 200, 0), 2)
            cv2.putText(
                annotated,
                f"OVERHEAD SCOREBOARD ROI [{xmax-xmin}x{ymax-ymin}]",
                (xmin + 10, ymin + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 200, 0),
                2,
                cv2.LINE_AA,
            )

            # 3. Draw OCR Detected Bounding Boxes with text tags
            if ocr_items:
                for item in ocr_items:
                    bx1 = int(item.bbox.x1 + xmin)
                    by1 = int(item.bbox.y1 + ymin)
                    bx2 = int(item.bbox.x2 + xmin)
                    by2 = int(item.bbox.y2 + ymin)

                    cv2.rectangle(annotated, (bx1, by1), (bx2, by2), (0, 255, 255), 1)
                    conf_pct = int(item.confidence * 100)
                    cv2.putText(
                        annotated,
                        f"{item.text} ({conf_pct}%)",
                        (bx1, max(by1 - 4, ymin + 15)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (0, 255, 0),
                        1,
                        cv2.LINE_AA,
                    )

            # 4. Highlight Active Player Indicator
            if active_row:
                active_y_map = {1: (140, 280), 2: (295, 435), 3: (450, 590), 4: (610, 750)}
                if active_row in active_y_map:
                    ay1, ay2 = active_y_map[active_row]
                    cv2.rectangle(
                        annotated,
                        (xmin + 10, ymin + ay1),
                        (xmin + 120, ymin + ay2),
                        (0, 255, 255),
                        3,
                    )
                    cv2.putText(
                        annotated,
                        "ACTIVE",
                        (xmin + 15, ymin + ay1 + 25),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 255),
                        2,
                        cv2.LINE_AA,
                    )

        # 5. Bottom Live Scoreboard Telemetry HUD
        hud_y1 = 910
        hud_y2 = 1070
        cv2.rectangle(annotated, (15, hud_y1), (1905, hud_y2), (15, 15, 15), -1)
        cv2.rectangle(annotated, (15, hud_y1), (1905, hud_y2), (100, 100, 100), 2)

        cv2.putText(
            annotated,
            "BOWLVISION REAL-TIME TELEMETRY HUD (4-PLAYER MATCH STATS)",
            (35, hud_y1 + 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 220, 255),
            2,
            cv2.LINE_AA,
        )

        p_list = list(players.values())
        for idx, p in enumerate(p_list):
            p_x = 35 + (idx % 2) * 935
            p_y = hud_y1 + 65 + (idx // 2) * 50

            played_frames = [
                f"F{num}:[{cell.rolls_formatted()}|{cell.cumulative_score or '-'}]"
                for num, cell in p.frames.items()
                if cell.is_played
            ]
            frames_str = " ".join(played_frames) if played_frames else "No frames played"
            ttl_str = f"TTL: {p.total_score if p.total_score is not None else '-'}"

            is_active_p = (active_row is not None and p.row_index == active_row)
            color = (0, 255, 255) if is_active_p else (225, 225, 225)
            badge = "[ACTIVE] " if is_active_p else ""
            line = f"{badge}{p.name:<12} | {ttl_str:<8} | {frames_str}"
            cv2.putText(annotated, line, (p_x, p_y), cv2.FONT_HERSHEY_SIMPLEX, 0.52, color, 1, cv2.LINE_AA)

        # Write to video file if writer is initialized
        if self.writer is not None:
            self.writer.write(annotated)

        # Show interactive live window if viewer is initialized
        if self.viewer is not None:
            self.viewer.update_frame(annotated)

        return annotated

    def close(self):
        if self.writer is not None:
            self.writer.release()
            self.writer = None
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None
