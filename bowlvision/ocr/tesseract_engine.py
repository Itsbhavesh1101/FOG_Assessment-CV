from typing import List, Union
import cv2
import numpy as np
from .base import BaseOCREngine
from ..core.types import BoundingBox, OCRItem


class TesseractOCREngine(BaseOCREngine):
    """Pytesseract OCR backend with bounding box parsing."""

    def __init__(self):
        self._available = False
        self._check_available()

    def _check_available(self):
        try:
            import pytesseract
            self._available = True
        except ImportError:
            self._available = False

    def is_available(self) -> bool:
        return self._available

    def detect_and_recognize(self, image_input: Union[np.ndarray, str]) -> List[OCRItem]:
        if not self.is_available():
            return []

        import pytesseract

        if isinstance(image_input, str):
            img = cv2.imread(image_input)
        else:
            img = image_input

        if img is None or img.size == 0:
            return []

        items = []
        try:
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            n_boxes = len(data["text"])
            for i in range(n_boxes):
                text = data["text"][i].strip()
                conf_str = str(data["conf"][i])
                try:
                    conf = float(conf_str) / 100.0
                except ValueError:
                    conf = 0.0

                if text and conf > 0.2:
                    x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                    bbox = BoundingBox(x1=x, y1=y, x2=x + w, y2=y + h)
                    items.append(OCRItem(text=text, confidence=conf, bbox=bbox))
        except Exception:
            pass

        return items
