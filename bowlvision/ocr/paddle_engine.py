from typing import List, Union
import numpy as np
from .base import BaseOCREngine
from ..core.types import BoundingBox, OCRItem


class PaddleOCREngine(BaseOCREngine):
    """PaddleOCR backend wrapper."""

    def __init__(self):
        self._engine = None
        self._init_engine()

    def _init_engine(self):
        try:
            from paddleocr import PaddleOCR
            self._engine = PaddleOCR(
                lang="en",
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                enable_mkldnn=False,
            )
        except Exception:
            self._engine = None

    def is_available(self) -> bool:
        return self._engine is not None

    def detect_and_recognize(self, image_input: Union[np.ndarray, str]) -> List[OCRItem]:
        if not self.is_available():
            return []

        items: List[OCRItem] = []
        try:
            if hasattr(self._engine, "predict"):
                res = list(self._engine.predict(image_input))
            else:
                res = list(self._engine.ocr(image_input))

            if res and len(res) > 0 and res[0] is not None:
                item = res[0]
                if isinstance(item, dict):
                    texts = item.get("rec_texts", [])
                    scores = item.get("rec_scores", [])
                    polys = item.get("rec_polys", item.get("dt_polys", []))
                    for text, score, poly in zip(texts, scores, polys):
                        t_str = str(text).strip()
                        if t_str:
                            bbox = BoundingBox.from_polygon(poly)
                            items.append(OCRItem(text=t_str, confidence=float(score), bbox=bbox))
                elif isinstance(item, list):
                    for line in item:
                        poly = line[0]
                        text = str(line[1][0]).strip()
                        conf = float(line[1][1])
                        if text:
                            bbox = BoundingBox.from_polygon(poly)
                            items.append(OCRItem(text=text, confidence=conf, bbox=bbox))
        except Exception:
            pass

        return items
