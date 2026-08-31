from typing import Dict, Optional
import cv2
import numpy as np

from .core.config import PipelineConfig
from .core.models import PlayerScorecard
from .vision.video_stream import VideoStream
from .vision.cutaway_detector import CutawayDetector
from .vision.image_enhancer import ImageEnhancer
from .ocr.ocr_manager import OCRManager
from .spatial.player_tracker import PlayerTracker
from .spatial.cell_mapper import SpatialGridMapper
from .analytics.temporal_aggregator import TemporalScoreboardTracker
from .export.json_exporter import serialize_match_json
from .export.csv_exporter import serialize_match_csv, export_timeline_history_csv
from .export.visualizer import ScoreboardVisualizer
from .export.video_annotator import VideoAnnotator


class BowlVisionPipeline:
    """
    Main Computer Vision & OCR pipeline orchestrator for Bowling Scoreboard extraction.
    """

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.player_names: Dict[int, str] = config.get_initial_player_names()
        self.last_roi_crop: Optional[np.ndarray] = None
        self.last_ocr_items: list = []
        self.last_observed_cards: Dict[str, PlayerScorecard] = {}
        self.crops_saved_count: int = 0

    def run(self) -> dict:
        self.config.validate()
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        self.config.debug_dir.mkdir(parents=True, exist_ok=True)

        stream = VideoStream(self.config.video_path)
        meta = stream.metadata
        step = stream.sample_step(self.config.sample_fps)
        total_samples = (meta.total_frames + step - 1) // step

        print("=" * 72)
        print("         BOWLVISION — COMPUTER VISION SCOREBOARD EXTRACTION")
        print(f"Target Video: {self.config.video_path.name}")
        print("=" * 72)
        print(f"[1/4] Loaded Video Stream: {meta.width}x{meta.height} @ {meta.fps:.1f} FPS | {meta.total_frames} Frames ({meta.duration_sec:.2f}s)")

        cutaway_detector = CutawayDetector(default_roi=self.config.roi)
        enhancer = ImageEnhancer()
        ocr_mgr = OCRManager(preferred_engine=self.config.ocr_engine)
        player_tracker = PlayerTracker()
        grid_mapper = SpatialGridMapper()
        temporal_tracker = TemporalScoreboardTracker(
            window_size=self.config.temporal_window_size,
            min_confidence=self.config.min_ocr_confidence,
        )

        annotator = None
        if self.config.render_annotated_video or self.config.show_live:
            annotated_video_path = self.config.output_dir / f"annotated_{self.config.video_path.name}"
            annotator = VideoAnnotator(
                output_path=annotated_video_path if self.config.render_annotated_video else None,
                fps=meta.fps,
                frame_size=(meta.width, meta.height),
                show_window=self.config.show_live,
            )
            if self.config.render_annotated_video:
                print(f"[+] Video annotator active -> {annotated_video_path}")
            if self.config.show_live:
                print("[+] Live interactive visualization window active")

        print(f"[2/4] Processing {total_samples} samples (~{self.config.sample_fps:g} FPS) using OCR Engine: [{ocr_mgr.engine_name}]...\n", flush=True)

        for sample in stream.iter_samples(target_fps=self.config.sample_fps):
            ts = sample.timestamp_sec
            frame_bgr = sample.image_bgr

            is_visible = cutaway_detector.is_scoreboard_visible(frame_bgr, self.config.roi)
            ocr_items = []
            observed_cards = {}
            active_row = None
            reused_cache = False

            if is_visible:
                crop = cutaway_detector.crop_scoreboard_roi(frame_bgr, self.config.roi)
                if crop.size > 0:
                    # Check if crop has changed enough to warrant new OCR
                    if self._can_reuse_crop_ocr(crop):
                        ocr_items = self.last_ocr_items
                        observed_cards = self.last_observed_cards
                        reused_cache = True
                    else:
                        enhanced = enhancer.enhance_for_ocr(crop)
                        self._save_debug_crop_if_enabled(enhanced, ts)
                        ocr_items = ocr_mgr.extract_text(enhanced)

                        if len(ocr_items) >= 10:
                            active_row = player_tracker.detect_active_highlight_row(crop)
                            hdr_name = player_tracker.extract_header_name(ocr_items)
                            if active_row and hdr_name:
                                self.player_names[active_row] = hdr_name

                            observed_cards = grid_mapper.map_detections_to_scorecards(
                                ocr_items=ocr_items,
                                player_names=self.player_names,
                            )
                            self.last_roi_crop = crop.copy()
                            self.last_ocr_items = ocr_items
                            self.last_observed_cards = observed_cards
                        else:
                            is_visible = False

            # Process state aggregation
            temporal_tracker.process_frame(
                timestamp=ts,
                is_visible=is_visible,
                observed_players=observed_cards if is_visible else None,
                active_row=active_row,
            )

            # Render video overlay frame if enabled
            if annotator is not None:
                annotator.annotate_frame(
                    frame_bgr=frame_bgr,
                    timestamp=ts,
                    is_visible=is_visible,
                    ocr_items=ocr_items,
                    players=temporal_tracker.current_players,
                    active_row=active_row,
                    roi_coords=self.config.roi,
                )

            # Log frame observation
            self._log_progress(ts, is_visible, ocr_items, temporal_tracker.current_players, reused_cache)

        if annotator is not None:
            annotator.close()

        # 3. Export structured results
        print("\n[3/4] Exporting final structured datasets to output/...")
        json_path = self.config.output_dir / "final_scoreboard.json"
        csv_path = self.config.output_dir / "final_scoreboard.csv"
        timeline_csv_path = self.config.output_dir / "timeline_history.csv"

        ordered_players = [
            temporal_tracker.current_players.get(
                self.player_names.get(r_idx, f"PLAYER_{r_idx}"),
                PlayerScorecard(row_index=r_idx, name=self.player_names.get(r_idx, f"PLAYER_{r_idx}"))
            )
            for r_idx in [1, 2, 3, 4]
        ]

        scoreboard_dict = serialize_match_json(
            video_name=self.config.video_path.name,
            duration_seconds=meta.duration_sec,
            players=ordered_players,
            output_path=json_path,
        )
        serialize_match_csv(ordered_players, csv_path)
        export_timeline_history_csv(temporal_tracker.csv_history_records, timeline_csv_path)

        print(f"  --> JSON Export : {json_path}")
        print(f"  --> CSV Export  : {csv_path}")
        print(f"  --> Timeline CSV: {timeline_csv_path}")

        # 4. Print summary
        print("\n[4/4] Final Results Summary:")
        print(ScoreboardVisualizer.format_terminal_summary(ordered_players))
        print(f"\nStats: Processed {temporal_tracker.stats['total_frames']} samples | "
              f"Visible: {temporal_tracker.stats['visible_frames']} | "
              f"Cutaways: {temporal_tracker.stats['cutaway_frames']} | "
              f"State Corrections: {temporal_tracker.stats['corrections_made']}")
        print("=" * 72)
        return scoreboard_dict

    def _can_reuse_crop_ocr(self, current_crop: np.ndarray) -> bool:
        if self.last_roi_crop is None or not self.last_ocr_items:
            return False
        diff = float(np.mean(cv2.absdiff(current_crop, self.last_roi_crop)))
        return diff < self.config.ocr_cache_threshold

    def _save_debug_crop_if_enabled(self, enhanced_img: np.ndarray, timestamp: float):
        if not self.config.save_debug_crops:
            return
        if self.config.debug_crops_limit > 0 and self.crops_saved_count >= self.config.debug_crops_limit:
            return
        save_dir = self.config.debug_dir / "enhanced_crops"
        save_dir.mkdir(parents=True, exist_ok=True)
        crop_path = save_dir / f"crop_{timestamp:05.1f}s.png"
        cv2.imwrite(str(crop_path), enhanced_img)
        self.crops_saved_count += 1

    def _log_progress(
        self,
        timestamp: float,
        is_visible: bool,
        ocr_items: list,
        players: Dict[str, PlayerScorecard],
        reused_cache: bool,
    ):
        if not is_visible:
            print(f"[{timestamp:5.1f}s] [CUTAWAY] Camera view switched - Scoreboard state frozen", flush=True)
        elif reused_cache:
            print(f"[{timestamp:5.1f}s] [VISIBLE] Scoreboard unchanged (cached frame)", flush=True)
        else:
            ttls = " | ".join([f"{p.name[:3]}:{p.total_score or '-'}" for p in players.values()])
            print(f"[{timestamp:5.1f}s] [VISIBLE] Detections: {len(ocr_items):2d} | TTLs: [{ttls}]", flush=True)
