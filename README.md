# Unseen Lab

**Subtle image transformation, perturbation, and visual experimentation — standalone or inside GIMP.**

> Change what you don't see.

Unseen Lab is an image-processing toolkit built around one principle: transformations should be measurable, reproducible, and visually inspectable. The project provides one shared processing core used by a desktop editor, command-line interface, and GIMP 3 integration.

## Status

Unseen Lab is in **early development (v0.1 foundation)**. The core pipeline, desktop shell, CLI, metrics, tests, and first GIMP 3 adapter are included. Interfaces may evolve while transform semantics stabilize.

## Included in v0.1

- Controlled Gaussian noise, per-channel or monochrome.
- Small Gaussian blur.
- Micro-resampling while preserving the original canvas size.
- Optional JPEG round-trip transformation.
- Alpha preservation for RGB processing.
- MAE, RMSE, and PSNR similarity metrics.
- CLI and standalone desktop editor using the same pipeline.
- Initial GIMP 3 Python plug-in adapter.

## Architecture

```text
                    ┌───────────────────────┐
                    │   unseen_lab.core     │
                    │ noise / transforms    │
                    │ pipeline / metrics    │
                    └───────────┬───────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
      ┌───────▼───────┐ ┌──────▼──────┐ ┌───────▼────────┐
      │ Desktop editor │ │     CLI      │ │ GIMP 3 plug-in │
      │    PySide6     │ │   argparse   │ │  Python + GI   │
      └───────────────┘ └─────────────┘ └────────────────┘
```

The core is the product. Front-ends are adapters and should contain as little image-processing logic as possible.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Installation

Python 3.11+ is recommended.

### Core + CLI

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
# source .venv/bin/activate

pip install -e .
```

### Desktop editor

```bash
pip install -e ".[desktop]"
unseen-lab-gui
```

### Development

```bash
pip install -e ".[desktop,dev]"
pytest
ruff check .
```

## CLI

```bash
unseen-lab input.png output.png \
  --noise 2.0 \
  --blur 0.10 \
  --resample 0.997 \
  --jpeg-quality 96 \
  --seed 42 \
  --report
```

For a minimal pipeline:

```bash
unseen-lab input.png output.png --noise 1.5 --seed 42 --report
```

## Desktop editor

The standalone editor is deliberately focused rather than trying to replace a full raster editor. It provides an image preview, transformation inspector, reproducible seeds, objective similarity metrics, original/processed comparison, and Save As workflow.

## GIMP 3

The integration lives in [`gimp-plugin/unseen-lab/`](gimp-plugin/unseen-lab/). It is a thin adapter over the shared Python core.

GIMP 3 Python plug-ins use GObject Introspection. The plug-in folder and entry script must share the same base name. See [`docs/GIMP_PLUGIN.md`](docs/GIMP_PLUGIN.md) for setup and current limitations.

Longer-term, visual transforms that benefit from native non-destructive preview are candidates for GEGL implementations while retaining documented parity with the core pipeline.

## Python API

```python
from PIL import Image
from unseen_lab import PipelineConfig, process_image

image = Image.open("input.png")

result = process_image(
    image,
    PipelineConfig(
        noise_sigma=2.0,
        blur_radius=0.10,
        resample_scale=0.997,
        jpeg_quality=96,
        seed=42,
    ),
)

result.image.save("output.png")
print(result.metrics)
```

## Project principles

1. **One processing engine.** Standalone, CLI, and GIMP behavior must not fork.
2. **Reproducibility.** Randomized transforms accept deterministic seeds.
3. **Measured change.** Experiments report objective similarity metrics.
4. **Conservative defaults.** Opening the app must not unexpectedly damage an image.
5. **Non-destructive mindset.** Preserve dimensions, alpha, and originals unless explicitly requested.
6. **Small, composable transforms.** Every transform should be independently testable.

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system design and boundaries.
- [`docs/DESIGN.md`](docs/DESIGN.md) — desktop UX and visual language.
- [`docs/GIMP_PLUGIN.md`](docs/GIMP_PLUGIN.md) — GIMP 3 integration.
- [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) — local development and testing.
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — planned evolution.

## License

No license has been selected yet. Until one is added, normal copyright rules apply.
