# Desktop Design Direction

## Product character

Unseen Lab should feel like a compact image editor / signal workbench rather than a one-off script wrapper.

The visual direction is:

- dark, neutral workspace that keeps attention on the image;
- restrained technical feel rather than decorative hacker clichés;
- transformation parameters grouped as a visible stack;
- objective metrics beside subjective visual inspection;
- ordinary image-editor vocabulary in primary controls.

## Main workspace

```text
┌─────────────────────────────────────────────────────────────────────┐
│ Open   Save As   Reset   Show Original                             │
├────────────────────────────────────────────┬────────────────────────┤
│                                            │ UNSEEN LAB             │
│                                            │ Controlled workspace   │
│                                            │                        │
│               IMAGE PREVIEW                │ Transform Stack        │
│                                            │ Noise           [2.0]  │
│                                            │ Mono RGB         [ ]   │
│                                            │ Blur            [0.0]  │
│                                            │ Resample      [1.000]  │
│                                            │ JPEG            [ ]    │
│                                            │ Quality          [96]  │
│                                            │ Seed             [42]  │
│                                            │                        │
│                                            │ Similarity             │
│                                            │ MAE              1.52  │
│                                            │ RMSE             2.03  │
│                                            │ PSNR         41.98 dB  │
├────────────────────────────────────────────┴────────────────────────┤
│ 1920 × 1080 • preview updated                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Interaction rules

- Parameter edits rebuild from the original after a short debounce.
- Show Original is a comparison view, not a state change.
- Save As saves the processed result without overwriting the source implicitly.
- Reset returns to conservative defaults.
- Routine adjustments stay in the main workspace, not modal dialogs.

## Future editor capabilities

- zoom percentage and 1:1 mode;
- pan / fit-to-window;
- split-view comparison;
- histogram and difference heatmap;
- recipes / presets;
- reorderable transform stack;
- per-transform enable switches;
- batch queue;
- SSIM and perceptual metrics.
