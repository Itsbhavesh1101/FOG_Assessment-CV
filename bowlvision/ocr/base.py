from abc import ABC, abstractmethod
from typing import List, Union
import numpy as np
from ..core.types import OCRItem


class BaseOCREngine(ABC):
    """Abstract interface for all OCR backends."""

    @abstractmethod
    def is_available(self) -> bool:
        """Checks if backend dependencies and models are functional."""
        pass

    @abstractmethod
    def detect_and_recognize(self, image_input: Union[np.ndarray, str]) -> List[OCRItem]:
        """Runs text localization and recognition, returning standardized OCRItems."""
        pass
