"""Unseen Lab shared image-processing toolkit."""

from unseen_lab.core.models import PipelineConfig, ProcessingResult, SimilarityMetrics
from unseen_lab.core.pipeline import process_image

__all__ = [
    "PipelineConfig",
    "ProcessingResult",
    "SimilarityMetrics",
    "process_image",
]

__version__ = "0.1.0"
