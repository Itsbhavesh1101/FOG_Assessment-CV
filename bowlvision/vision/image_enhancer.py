import cv2
import numpy as np


class ImageEnhancer:
    """
    Multi-stage image processing module designed for digital scoreboard typography:
    1. Grayscale luminance transformation
    2. CLAHE (Contrast Limited Adaptive Histogram Equalization)
    3. Bilateral Edge-Preserving Denoising to sharpen digital segment edges while smoothing noise
    """

    def __init__(self, clip_limit: float = 2.5, tile_grid_size: tuple = (8, 8), bilateral_d: int = 5):
        self.clip_limit = clip_limit
        self.tile_grid_size = tile_grid_size
        self.bilateral_d = bilateral_d
        self._clahe = cv2.createCLAHE(clipLimit=self.clip_limit, tileGridSize=self.tile_grid_size)

    def enhance_for_ocr(self, crop_bgr: np.ndarray, scale: float = 1.0) -> np.ndarray:
        if crop_bgr is None or crop_bgr.size == 0:
            return np.empty((0, 0), dtype=np.uint8)

        if scale <= 0:
            raise ValueError(f"Scale factor must be positive, got {scale}")

        if scale != 1.0:
            h, w = crop_bgr.shape[:2]
            target_size = (int(w * scale), int(h * scale))
            working_img = cv2.resize(crop_bgr, target_size, interpolation=cv2.INTER_CUBIC)
        else:
            working_img = crop_bgr

        if len(working_img.shape) == 3 and working_img.shape[2] == 3:
            gray = cv2.cvtColor(working_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = working_img.copy()

        equalized = self._clahe.apply(gray)
        denoised = cv2.bilateralFilter(
            equalized,
            d=self.bilateral_d,
            sigmaColor=50,
            sigmaSpace=50,
        )
        return denoised
