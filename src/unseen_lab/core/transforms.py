from __future__ import annotations

from io import BytesIO

from PIL import Image, ImageFilter


def apply_gaussian_blur(image: Image.Image, radius: float) -> Image.Image:
    if radius < 0:
        raise ValueError("radius must be >= 0")
    if radius == 0:
        return image.copy()
    return image.filter(ImageFilter.GaussianBlur(radius=radius))


def micro_resample(image: Image.Image, scale: float) -> Image.Image:
    """Resize by a small factor and return to the original dimensions."""
    if not 0.90 <= scale <= 1.10:
        raise ValueError("scale must be between 0.90 and 1.10")
    if scale == 1.0:
        return image.copy()

    width, height = image.size
    intermediate = (
        max(1, round(width * scale)),
        max(1, round(height * scale)),
    )
    resized = image.resize(intermediate, Image.Resampling.LANCZOS)
    return resized.resize((width, height), Image.Resampling.LANCZOS)


def jpeg_roundtrip(image: Image.Image, quality: int) -> Image.Image:
    """Encode/decode RGB through JPEG while preserving alpha separately."""
    if not 1 <= quality <= 100:
        raise ValueError("quality must be between 1 and 100")

    has_alpha = "A" in image.getbands()
    alpha = image.getchannel("A") if has_alpha else None

    stream = BytesIO()
    image.convert("RGB").save(
        stream,
        format="JPEG",
        quality=quality,
        subsampling=0,
        optimize=False,
    )
    stream.seek(0)

    with Image.open(stream) as decoded:
        result = decoded.convert("RGB").copy()

    if alpha is not None:
        result.putalpha(alpha)
    return result
