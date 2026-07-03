#!/usr/bin/env python3
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path
from PIL import Image, ImageOps


def main() -> None:
    parser = argparse.ArgumentParser(description="Resize rendered note pages for Xiaohongshu.")
    parser.add_argument("--src", required=True, help="Source directory containing page PNGs")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=1706)
    parser.add_argument("--dpi", type=int, default=72)
    args = parser.parse_args()

    src = Path(args.src).expanduser()
    out = Path(args.out).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    target = (args.width, args.height)
    dpi = (args.dpi, args.dpi)

    files = sorted(src.glob("*.png"))
    if not files:
        raise SystemExit(f"No PNG files found in {src}")

    for page in files:
        img = Image.open(page).convert("RGBA")
        fitted = ImageOps.contain(img, target, method=Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", target, (255, 255, 255, 255))
        xy = ((target[0] - fitted.width) // 2, (target[1] - fitted.height) // 2)
        canvas.alpha_composite(fitted, xy)
        canvas.convert("RGB").save(out / page.name, "PNG", dpi=dpi, optimize=True)

    zip_path = out.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for page in sorted(out.glob("*.png")):
            zf.write(page, arcname=f"{out.name}/{page.name}")

    print(f"OK  {out}  ({len(files)} pages)")
    print(f"ZIP {zip_path}")


if __name__ == "__main__":
    main()

