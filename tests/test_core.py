import math

import numpy as np
from PIL import Image

from unseen_lab.core.metrics import compare_images
from unseen_lab.core.models import PipelineConfig
from unseen_lab.core.noise import add_gaussian_noise
from unseen_lab.core.pipeline import process_image


def sample_rgba() -> Image.Image:
    data = np.zeros((12, 16, 4), dtype=np.uint8)
    data[..., 0] = 60
    data[..., 1] = 120
    data[..., 2] = 180
    data[..., 3] = np.arange(16, dtype=np.uint8)[None, :] * 16
    return Image.fromarray(data, mode="RGBA")


def test_noise_is_deterministic_with_seed() -> None:
    image = sample_rgba()
    first = add_gaussian_noise(image, sigma=2.5, seed=123)
    second = add_gaussian_noise(image, sigma=2.5, seed=123)
    assert np.array_equal(np.asarray(first), np.asarray(second))


def test_noise_preserves_alpha() -> None:
    image = sample_rgba()
    result = add_gaussian_noise(image, sigma=3.0, seed=1)
    assert np.array_equal(np.asarray(image)[..., 3], np.asarray(result)[..., 3])


def test_identical_images_have_zero_error_and_infinite_psnr() -> None:
    image = sample_rgba()
    metrics = compare_images(image, image.copy())
    assert metrics.mae == 0
    assert metrics.rmse == 0
    assert math.isinf(metrics.psnr_db)


def test_pipeline_preserves_canvas_and_source() -> None:
    image = sample_rgba()
    before = np.asarray(image).copy()
    config = PipelineConfig(
        noise_sigma=2.0,
        blur_radius=0.1,
        resample_scale=0.98,
        jpeg_quality=97,
        seed=42,
    )
    result = process_image(image, config)

    assert result.image.size == image.size
    assert np.array_equal(np.asarray(image), before)
    assert result.metrics.rmse > 0


def test_zero_pipeline_is_identity() -> None:
    image = sample_rgba()
    result = process_image(image, PipelineConfig(noise_sigma=0.0))
    assert np.array_equal(np.asarray(result.image), np.asarray(image))
    assert result.metrics.mae == 0
