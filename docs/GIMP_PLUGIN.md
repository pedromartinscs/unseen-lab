# GIMP 3 Integration

## Direction

Unseen Lab supports GIMP as a host without making the GIMP implementation the canonical source of processing logic.

GIMP 3 Python plug-ins use GObject Introspection. A plug-in script is placed in a folder with the same base name under GIMP's plug-ins directory. The v0.1 adapter registers an image procedure under **Filters → Unseen Lab** and delegates pixel processing to `unseen_lab.core`.

## Current plug-in

Location:

```text
gimp-plugin/unseen-lab/unseen-lab.py
```

Current operation:

- **Subtle Gaussian Noise**
- configurable sigma;
- optional monochrome/shared RGB noise;
- deterministic integer seed;
- one drawable at a time;
- RGBA dimensions and alpha preserved.

## Requirements

- GIMP 3.x with Python plug-in support.
- The `unseen_lab` package importable by the Python interpreter used for GIMP plug-ins.
- NumPy available in that environment.

The exact interpreter layout differs by platform and GIMP distribution. During development, verify GIMP's Python `sys.path` rather than assuming a system `pip` install is visible.

## Plug-in wrapper installation

Copy:

```text
gimp-plugin/unseen-lab/
```

into the user plug-ins directory, producing:

```text
plug-ins/
└── unseen-lab/
    └── unseen-lab.py
```

On platforms that require it, mark the script executable. Restart GIMP after installation.

## Why keep the core outside the plug-in?

Duplicating processing inside the GIMP wrapper would create two products. Instead, the adapter translates host pixels to a NumPy representation and calls the same transform primitive used elsewhere.

## GEGL roadmap

GIMP recommends GEGL operations for visual filters that benefit from live canvas preview and non-destructive effects. Stable Unseen Lab transforms may therefore gain GEGL counterparts later.

The Python plug-in remains useful for multi-step workflows, layer orchestration, recipe execution, and bridging the shared Python engine into GIMP.
