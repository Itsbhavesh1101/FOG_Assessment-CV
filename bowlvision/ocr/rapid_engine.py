from typing import List, Union
import numpy as np
from .base import BaseOCREngine
from ..core.types import BoundingBox, OCRItem


class RapidOCREngine(BaseOCREngine):
    """RapidOCR (ONNXRuntime PP-OCR) backend."""

    def __init__(self):
        self._engine = None
        self._init_engine()

    def _init_engine(self):
        try:
            from rapidocr_onnxruntime import RapidOCR
            self._engine = RapidOCR()
        except Exception:
            self._engine = None

    def is_available(self) -> bool:
        return self._engine is not None

    def detect_and_recognize(self, image_input: Union[np.ndarray, str]) -> List[OCRItem]:
        if not self.is_available():
            return []

        items: List[OCRItem] = []
        try:
            results, _ = self._engine(image_input)
            if not results:
                return []

            for entry in results:
                poly, raw_text, conf_val = entry
                text = str(raw_text).strip()
                if not text:
                    continue

                try:
                    conf = float(conf_val)
                except (ValueError, TypeError):
                    conf = 0.5

                bbox = BoundingBox.from_polygon(poly)
                items.append(OCRItem(
                    text=text,
                    confidence=conf,
                    bbox=bbox,
                    raw_polygon=poly,
                ))
        except Exception as err:
            # Silently catch transient recognition failures
            pass

        return items
