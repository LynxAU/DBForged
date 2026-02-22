#!/usr/bin/env python3
"""
Quick local preview of the ANSI logo rendering WITHOUT running Evennia.
Run from the repo root: python test_logo_preview.py
"""
import sys
from pathlib import Path

REPO = Path(__file__).parent
COLOR_CANDIDATES = [
    REPO / "live" / "server" / "conf" / "assets" / "db_logo.png",
    REPO / "evennia" / "web" / "static" / "ui" / "dbforgedfullcoloralpha.png",
    REPO / "evennia" / "web" / "static" / "ui" / "dbforgedfullcoloralpha.png.png",
    REPO / "evennia" / "web" / "static" / "ui" / "dbforgedfullcolor.png",
    REPO / "evennia" / "web" / "static" / "ui" / "dbforgedfullcolonoalpha.png",
]


def _find_color_path():
    for path in COLOR_CANDIDATES:
        if path.exists():
            return path
    return COLOR_CANDIDATES[0]


COLOR_PATH = _find_color_path()


def render(color_path=COLOR_PATH, out_w=96):
    from PIL import Image

    print(f"Color: {color_path}")
    color_rgba = Image.open(color_path).convert("RGBA")
    alpha = color_rgba.getchannel("A")
    amin, amax = alpha.getextrema()
    if amin >= 255 or amax <= 0:
        print("ERROR: expected a transparent PNG (alpha channel required)")
        return

    mw, mh = alpha.size
    print(f"Source size: {mw}x{mh}")

    apx = alpha.load()
    fg_xs = [xx for yy in range(mh) for xx in range(mw) if apx[xx, yy] >= 16]
    fg_ys = [yy for yy in range(mh) for xx in range(mw) if apx[xx, yy] >= 16]
    if not fg_xs:
        print("ERROR: no visible pixels found in alpha channel")
        return

    pad = 2
    bx0 = max(0, min(fg_xs) - pad)
    by0 = max(0, min(fg_ys) - pad)
    bx1 = min(mw - 1, max(fg_xs) + pad)
    by1 = min(mh - 1, max(fg_ys) + pad)
    print(f"Tight bbox: ({bx0},{by0})-({bx1},{by1}) -> {bx1 - bx0 + 1}x{by1 - by0 + 1}")

    color_crop = color_rgba.crop((bx0, by0, bx1 + 1, by1 + 1))
    alpha_crop = alpha.crop((bx0, by0, bx1 + 1, by1 + 1))
    crop_w, crop_h = alpha_crop.size

    out_px_h = max(4, int(out_w * (crop_h / max(1, crop_w)) * 0.55 * 2))
    if out_px_h % 2:
        out_px_h += 1
    print(f"Output canvas: {out_w}x{out_px_h} pixel rows -> {out_px_h // 2} terminal rows")

    alpha_small = alpha_crop.resize((out_w, out_px_h), Image.Resampling.BOX)
    color_small = color_crop.resize((out_w, out_px_h), Image.Resampling.LANCZOS)
    ap = alpha_small.load()
    cp = color_small.load()
    fg_threshold = 64

    def is_fg(x, y):
        return ap[x, y] >= fg_threshold

    x0, y0, x1, y1 = 0, 0, out_w - 1, out_px_h - 1
    while y0 < y1 and not any(is_fg(xx, y0) for xx in range(out_w)):
        y0 += 1
    while y1 > y0 and not any(is_fg(xx, y1) for xx in range(out_w)):
        y1 -= 1
    while x0 < x1 and not any(is_fg(x0, yy) for yy in range(out_px_h)):
        x0 += 1
    while x1 > x0 and not any(is_fg(x1, yy) for yy in range(out_px_h)):
        x1 -= 1
    if ((y1 - y0 + 1) % 2) != 0 and y1 > y0:
        y1 -= 1

    print(f"Active region: x={x0}-{x1}  y={y0}-{y1}  -> {(y1 - y0 + 1) // 2} rendered rows")

    lines = []
    for y in range(y0, y1 + 1, 2):
        parts = []
        for x in range(x0, x1 + 1):
            top_fg = is_fg(x, y)
            bot_fg = is_fg(x, y + 1) if (y + 1) <= y1 else False
            if not top_fg and not bot_fg:
                parts.append(" ")
                continue
            tr, tg, tb, _ = cp[x, y]
            br, bg, bb, _ = cp[x, y + 1] if (y + 1) <= y1 else (0, 0, 0, 0)
            if top_fg and bot_fg:
                parts.append(f"\x1b[48;2;{br};{bg};{bb}m\x1b[38;2;{tr};{tg};{tb}m?")
            elif top_fg:
                parts.append(f"\x1b[48;2;0;0;0m\x1b[38;2;{tr};{tg};{tb}m?")
            else:
                parts.append(f"\x1b[48;2;0;0;0m\x1b[38;2;{br};{bg};{bb}m?")
        parts.append("\x1b[0m")
        lines.append("".join(parts).rstrip())

    print("\n" + "\n".join(lines) + "\n")
    print(f"({len(lines)} terminal rows)")


if __name__ == "__main__":
    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        print("Pillow not found. Install: pip install Pillow")
        sys.exit(1)

    render()
