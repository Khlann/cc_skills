#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

W, H = 1080, 1350
BLACK = (5, 7, 12)
WHITE = (255, 255, 246)
YELLOW = (255, 226, 18)
BLUE = (27, 140, 255)
GREEN = (32, 232, 132)
RED = (255, 68, 76)

FONT_CN = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_MONO = "/System/Library/Fonts/Menlo.ttc"
FONT_EN = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def font(path: str, size: int):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.truetype(FONT_CN, size)


def text_size(draw, text, f, stroke_width=0):
    box = draw.textbbox((0, 0), text, font=f, stroke_width=stroke_width)
    return box[2] - box[0], box[3] - box[1]


def center(draw, y, text, f, fill, stroke=BLACK, sw=0, cx=W // 2):
    tw, th = text_size(draw, text, f, sw)
    draw.text((cx - tw / 2, y), text, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke)
    return y + th


def rounded(draw, xy, r, fill, outline=None, width=4):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def cover_fit(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    sw, sh = img.size
    scale = max(W / sw, H / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - W) // 2
    top = (nh - H) // 2
    return img.crop((left, top, left + W, top + H)).convert("RGBA")


def split_semicolon(value: str, fallback: list[str]) -> list[str]:
    items = [item.strip() for item in value.split(";") if item.strip()]
    return items or fallback


def main() -> None:
    parser = argparse.ArgumentParser(description="Overlay exact Xiaohongshu cover text on an AIGC background.")
    parser.add_argument("--background", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--name", default="xhs-cover-aigc-refined")
    parser.add_argument("--title", required=True, help='Title lines separated by "|".')
    parser.add_argument("--kicker", default="技术笔记")
    parser.add_argument("--subtitle", default="")
    parser.add_argument("--formula", default="")
    parser.add_argument("--checklist", default="")
    parser.add_argument("--code", default="")
    parser.add_argument("--bottom", default="一张图搞懂核心概念")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    bg = cover_fit(Image.open(Path(args.background).expanduser()))
    bg = ImageEnhance.Color(bg).enhance(1.12)
    bg = ImageEnhance.Contrast(bg).enhance(1.08)
    canvas = bg.copy()

    veil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(veil)
    vd.rectangle((0, 0, W, H), fill=(0, 0, 0, 58))
    vd.rounded_rectangle((68, 150, 1012, 1248), radius=46, fill=(255, 246, 210, 32), outline=(255, 226, 18, 150), width=4)
    canvas = Image.alpha_composite(canvas, veil)
    draw = ImageDraw.Draw(canvas)

    rounded(draw, (292, 118, 788, 174), 28, (0, 0, 0, 220), YELLOW, 4)
    center(draw, 129, args.kicker, font(FONT_CN, 28), WHITE)

    title_lines = [line.strip() for line in args.title.split("|") if line.strip()]
    y = 245
    for i, line in enumerate(title_lines[:3]):
        fill = YELLOW if i % 2 == 0 else WHITE
        size = 92 if len(line) <= 8 else 78
        y = center(draw, y, line, font(FONT_CN, size), fill, BLACK, 9)
        y += 12
    if args.subtitle:
        center(draw, 500, args.subtitle, font(FONT_EN if args.subtitle.isascii() else FONT_CN, 29), YELLOW, BLACK, 3)

    rounded(draw, (96, 610, 470, 764), 30, (230, 255, 238, 225), GREEN, 6)
    rounded(draw, (610, 610, 984, 764), 30, (255, 232, 232, 225), RED, 6)
    rounded(draw, (484, 638, 596, 736), 26, (0, 0, 0, 235), YELLOW, 5)
    draw.text((130, 637), "Chosen", font=font(FONT_EN, 34), fill=GREEN, stroke_width=1, stroke_fill=BLACK)
    draw.text((318, 641), "y_w", font=font(FONT_MONO, 32), fill=BLACK)
    draw.text((638, 637), "Rejected", font=font(FONT_EN, 33), fill=RED, stroke_width=1, stroke_fill=BLACK)
    draw.text((845, 641), "y_l", font=font(FONT_MONO, 32), fill=BLACK)
    center(draw, 661, "VS", font(FONT_EN, 49), YELLOW, cx=540)

    formula = args.formula or "core formula goes here"
    rounded(draw, (82, 805, 998, 940), 30, (255, 226, 18, 238), BLACK, 7)
    draw.text((116, 830), formula[:54], font=font(FONT_MONO, 24), fill=BLACK)
    if len(formula) > 54:
        draw.text((168, 873), formula[54:108], font=font(FONT_MONO, 24), fill=BLACK)

    rounded(draw, (78, 1010, 500, 1218), 28, (255, 255, 246, 235), BLACK, 6)
    for i, item in enumerate(split_semicolon(args.checklist, ["公式怎么来？", "代码怎么写？", "面试怎么讲？"])[:3]):
        yy = 1042 + i * 58
        rounded(draw, (112, yy + 4, 148, yy + 40), 8, YELLOW, BLACK, 4)
        draw.line((120, yy + 24, 130, yy + 35, 144, yy + 10), fill=BLACK, width=5)
        draw.text((168, yy - 2), item, font=font(FONT_CN, 27), fill=BLACK)

    rounded(draw, (568, 994, 1000, 1218), 28, (0, 0, 0, 232), YELLOW, 6)
    for i, line in enumerate(split_semicolon(args.code, ["pred = model(x)", "loss = compute()", "optimizer.step()"])[:3]):
        color = (125, 255, 160) if i == 1 else (YELLOW if i == 2 else WHITE)
        draw.text((606, 1030 + i * 56), line, font=font(FONT_MONO, 24), fill=color)

    rounded(draw, (54, 1273, 1026, 1334), 26, (0, 0, 0, 235), YELLOW, 5)
    tw, _ = text_size(draw, args.bottom, font(FONT_CN, 31))
    draw.text(((W - tw) / 2, 1285), args.bottom, font=font(FONT_CN, 31), fill=WHITE)

    png = out_dir / f"{args.name}.png"
    jpg = out_dir / f"{args.name}.jpg"
    canvas.convert("RGB").save(png)
    canvas.convert("RGB").save(jpg, quality=96)
    print(png)
    print(jpg)


if __name__ == "__main__":
    main()

