from __future__ import annotations

import numpy as np
from PIL import Image


def add_gaussian_noise_array(
    rgb: np.ndarray,
    *,
    sigma: float,
    monochrome: bool = False,
    seed: int | None = None,
) -> np.ndarray:
    """Return an RGB uint8 array with deterministic optional Gaussian noise."""
    if sigma < 0:
        raise ValueError("sigma must be >= 0")
    if rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError("rgb must have shape (height, width, 3)")

    source = rgb.astype(np.float32, copy=False)
    if sigma == 0:
        return source.astype(np.uint8, copy=True)

    rng = np.random.default_rng(seed)
    noise_shape = (*source.shape[:2], 1) if monochrome else source.shape
    noise = rng.normal(0.0, sigma, noise_shape).astype(np.float32)

    if monochrome:
        noise = np.repeat(noise, 3, axis=2)

    return np.clip(source + noise, 0, 255).astype(np.uint8)


def add_gaussian_noise(
    image: Image.Image,
    *,
    sigma: float,
    monochrome: bool = False,
    seed: int | None = None,
) -> Image.Image:
    """Add noise to RGB channels while preserving an existing alpha channel."""
    has_alpha = "A" in image.getbands()
    converted = image.convert("RGBA") if has_alpha else image.convert("RGB")
    data = np.asarray(converted, dtype=np.uint8)

    processed_rgb = add_gaussian_noise_array(
        data[..., :3],
        sigma=sigma,
        monochrome=monochrome,
        seed=seed,
    )

    if not has_alpha:
        return Image.fromarray(processed_rgb, mode="RGB")

    output = np.empty_like(data)
    output[..., :3] = processed_rgb
    output[..., 3] = data[..., 3]
    return Image.fromarray(output, mode="RGBA")
