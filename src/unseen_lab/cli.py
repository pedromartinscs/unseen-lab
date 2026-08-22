from __future__ import annotations

import argparse
import math
from pathlib import Path

from unseen_lab.core.models import PipelineConfig
from unseen_lab.core.pipeline import process_image
from unseen_lab.io import load_image, save_image


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="unseen-lab",
        description="Apply controlled image transformations while measuring visual change.",
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--noise", type=float, default=2.0, metavar="SIGMA")
    parser.add_argument("--monochrome-noise", action="store_true")
    parser.add_argument("--blur", type=float, default=0.0, metavar="RADIUS")
    parser.add_argument("--resample", type=float, default=1.0, metavar="SCALE")
    parser.add_argument("--jpeg-quality", type=int, default=None, metavar="1-100")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--save-quality", type=int, default=96, metavar="1-100")
    parser.add_argument("--report", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = PipelineConfig(
        noise_sigma=args.noise,
        monochrome_noise=args.monochrome_noise,
        blur_radius=args.blur,
        resample_scale=args.resample,
        jpeg_quality=args.jpeg_quality,
        seed=args.seed,
    )

    result = process_image(load_image(args.input), config)
    save_image(result.image, args.output, quality=args.save_quality)

    if args.report:
        psnr = "inf" if math.isinf(result.metrics.psnr_db) else f"{result.metrics.psnr_db:.2f} dB"
        print(f"MAE:  {result.metrics.mae:.4f}")
        print(f"RMSE: {result.metrics.rmse:.4f}")
        print(f"PSNR: {psnr}")
        print(f"Saved: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
