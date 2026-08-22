from __future__ import annotations

from PIL import Image

from unseen_lab.core.metrics import compare_images
from unseen_lab.core.models import PipelineConfig, ProcessingResult
from unseen_lab.core.noise import add_gaussian_noise
from unseen_lab.core.transforms import (
    apply_gaussian_blur,
    jpeg_roundtrip,
    micro_resample,
)


def process_image(image: Image.Image, config: PipelineConfig) -> ProcessingResult:
    """Run the canonical Unseen Lab pipeline without mutating the input image."""
    original = image.copy()
    working = original.copy()

    if config.noise_sigma > 0:
        working = add_gaussian_noise(
            working,
            sigma=config.noise_sigma,
            monochrome=config.monochrome_noise,
            seed=config.seed,
        )
    if config.blur_radius > 0:
        working = apply_gaussian_blur(working, config.blur_radius)
    if config.resample_scale != 1.0:
        working = micro_resample(working, config.resample_scale)
    if config.jpeg_quality is not None:
        working = jpeg_roundtrip(working, config.jpeg_quality)

    return ProcessingResult(
        image=working,
        metrics=compare_images(original, working),
    )
