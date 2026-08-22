from __future__ import annotations

from pathlib import Path

from PIL import Image


def load_image(path: str | Path) -> Image.Image:
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(source)

    with Image.open(source) as opened:
        opened.load()
        return opened.copy()


def save_image(image: Image.Image, path: str | Path, *, quality: int = 96) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    suffix = destination.suffix.lower()

    if suffix in {".jpg", ".jpeg"}:
        image.convert("RGB").save(
            destination,
            format="JPEG",
            quality=quality,
            subsampling=0,
            optimize=True,
        )
        return
    if suffix == ".png":
        image.save(destination, format="PNG", optimize=True)
        return
    if suffix == ".webp":
        image.save(destination, format="WEBP", quality=quality, method=6)
        return

    raise ValueError("output format must be PNG, JPEG, or WebP")
