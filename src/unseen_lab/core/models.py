from __future__ import annotations

from dataclasses import dataclass

from PIL import Image


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    """Configuration for the conservative image-processing pipeline."""

    noise_sigma: float = 2.0
    monochrome_noise: bool = False
    blur_radius: float = 0.0
    resample_scale: float = 1.0
    jpeg_quality: int | None = None
    seed: int | None = None

    def __post_init__(self) -> None:
        if self.noise_sigma < 0:
            raise ValueError("noise_sigma must be >= 0")
        if self.blur_radius < 0:
            raise ValueError("blur_radius must be >= 0")
        if not 0.90 <= self.resample_scale <= 1.10:
            raise ValueError("resample_scale must be between 0.90 and 1.10")
        if self.jpeg_quality is not None and not 1 <= self.jpeg_quality <= 100:
            raise ValueError("jpeg_quality must be between 1 and 100")


@dataclass(frozen=True, slots=True)
class SimilarityMetrics:
    mae: float
    rmse: float
    psnr_db: float


@dataclass(frozen=True, slots=True)
class ProcessingResult:
    image: Image.Image
    metrics: SimilarityMetrics
