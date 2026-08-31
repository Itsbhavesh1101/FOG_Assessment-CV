from typing import List, Optional, Union
import numpy as np
from .base import BaseOCREngine
from .rapid_engine import RapidOCREngine
from .tesseract_engine import TesseractOCREngine
from .paddle_engine import PaddleOCREngine
from ..core.types import OCRItem


class OCRManager:
    """
    Factory and unified manager for OCR execution.
    Auto-detects and loads the optimal available engine (RapidOCR -> PaddleOCR -> Tesseract).
    """

    def __init__(self, preferred_engine: str = "auto"):
        self.preferred_engine = preferred_engine.lower().strip()
        self._engine: Optional[BaseOCREngine] = None
        self._engine_name: str = "none"
        self._initialize_backend()

    @property
    def engine_name(self) -> str:
        return self._engine_name

    def _initialize_backend(self):
        candidates = []
        if self.preferred_engine == "rapidocr":
            candidates = [("rapidocr", RapidOCREngine)]
        elif self.preferred_engine == "paddleocr":
            candidates = [("paddleocr", PaddleOCREngine)]
        elif self.preferred_engine == "pytesseract":
            candidates = [("pytesseract", TesseractOCREngine)]
        else:  # "auto" or other
            candidates = [
                ("rapidocr", RapidOCREngine),
                ("paddleocr", PaddleOCREngine),
                ("pytesseract", TesseractOCREngine),
            ]

        for name, cls_type in candidates:
            try:
                inst = cls_type()
                if inst.is_available():
                    self._engine = inst
                    self._engine_name = name
                    break
            except Exception:
                continue

    def is_ready(self) -> bool:
        return self._engine is not None and self._engine.is_available()

    def extract_text(self, image_input: Union[np.ndarray, str]) -> List[OCRItem]:
        if not self.is_ready():
            return []
        return self._engine.detect_and_recognize(image_input)
