# Development

## Setup

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[desktop,dev]"
```

Linux/macOS:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[desktop,dev]"
```

## Test

```bash
pytest
```

## Lint

```bash
ruff check .
```

## Run

```bash
python -m unseen_lab.cli input.png output.png --noise 2 --seed 42 --report
python -m unseen_lab.app.main
```

## Rules for new transforms

A new transform should normally include:

1. validated inputs;
2. deterministic behavior unless randomness is intentional;
3. a `PipelineConfig` field if it belongs in the canonical stack;
4. pipeline integration;
5. tests for dimensions, source immutability, and alpha where relevant;
6. CLI/UI exposure only after core behavior exists.

## GIMP testing

GIMP host integration cannot be fully validated by the normal unit-test environment because GI modules and the GIMP process are host-provided. Keep host-specific imports in the plug-in and use core unit tests to validate transform semantics.
