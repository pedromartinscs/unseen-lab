# Architecture

## Goal

Unseen Lab must behave like one product exposed through multiple hosts, not unrelated image tools that happen to share a name.

```text
Front-end / host integration
        ↓
PipelineConfig
        ↓
unseen_lab.core.pipeline
        ↓
small transform primitives
        ↓
ProcessingResult + metrics
```

## Packages

### `unseen_lab.core`

Pure processing logic. It knows nothing about Qt, GIMP, command-line parsing, dialogs, files, or application state.

- `models.py` — immutable configuration and results.
- `noise.py` — stochastic perturbation primitives.
- `transforms.py` — deterministic transforms.
- `metrics.py` — similarity measurements.
- `pipeline.py` — canonical operation order.

### `unseen_lab.io`

File-system adapter using Pillow. Output encoding is intentionally separate from a JPEG round-trip inside the transform stack.

### `unseen_lab.cli`

Converts command-line values into `PipelineConfig`, invokes the core, saves the result, and optionally prints metrics.

### `unseen_lab.app`

Standalone Qt UI. Previews are rebuilt from the untouched original, preventing accidental compounding while tuning controls.

### `gimp-plugin`

GIMP 3 host adapter. It translates drawable pixels and procedure arguments into the same processing primitives. GIMP-specific code stays here.

## Canonical v0.1 pipeline

1. Gaussian noise
2. Gaussian blur
3. Micro-resample
4. Optional JPEG round-trip
5. Similarity measurement against the untouched source

Changing this order is a behavior change and should be documented and tested.

## Image invariants

Unless a transform explicitly documents otherwise:

- width and height remain unchanged;
- source objects are not mutated;
- alpha is preserved;
- comparisons use RGB content;
- stochastic transforms accept a seed;
- output channels are clipped to valid ranges.

## GIMP and GEGL

Python provides a practical shared language for Pillow/NumPy processing, the desktop app, CLI, tests, and GIMP 3 plug-ins through GObject Introspection.

For filters whose best GIMP experience depends on non-destructive live preview, a GEGL operation may later be added. It becomes another implementation target and should match documented transform semantics.

## Dependency policy

The base install stays small: NumPy and Pillow. Desktop dependencies are optional (`PySide6`). GIMP-specific GI dependencies are provided by the host environment.
