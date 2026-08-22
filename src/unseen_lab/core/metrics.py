from __future__ import annotations

import math

import numpy as np
from PIL import Image

from unseen_lab.core.models import SimilarityMetrics


def _comparable_rgb(image: Image.Image) -> np.ndarray:
    return np.asarray(image.convert("RGB"), dtype=np.float32)


def compare_images(reference: Image.Image, candidate: Image.Image) -> SimilarityMetrics:
    if reference.size != candidate.size:
        raise ValueError("images must have the same dimensions")

    a = _comparable_rgb(reference)
    b = _comparable_rgb(candidate)
    difference = a - b

    mae = float(np.mean(np.abs(difference)))
    mse = float(np.mean(np.square(difference)))
    rmse = math.sqrt(mse)
    psnr = math.inf if mse == 0 else 20.0 * math.log10(255.0 / rmse)

    return SimilarityMetrics(mae=mae, rmse=rmse, psnr_db=psnr)
