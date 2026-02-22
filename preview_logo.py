#!/usr/bin/env python3
"""
Generates logo_preview.html from a transparent color logo PNG.
Usage: python preview_logo.py
"""
from pathlib import Path

from PIL import Image

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
OUT_W = 96


def render(color_path=COLOR_PATH, out_w=OUT_W):
    color_rgba = Image.open(color_path).convert("RGBA")
    alpha = color_rgba.getchannel("A")
    amin, amax = alpha.getextrema()
    if amin >= 255 or amax <= 0:
        raise ValueError("Color logo must be a transparent PNG with an alpha channel")

    mw, mh = alpha.size
    apx = alpha.load()
    fg_xs = [xx for yy in range(mh) for xx in range(mw) if apx[xx, yy] >= 16]
    fg_ys = [yy for yy in range(mh) for xx in range(mw) if apx[xx, yy] >= 16]
    if not fg_xs:
        raise ValueError("No visible pixels found in alpha channel")

    pad = 2
    bx0 = max(0, min(fg_xs) - pad)
    by0 = max(0, min(fg_ys) - pad)
    bx1 = min(mw - 1, max(fg_xs) + pad)
    by1 = min(mh - 1, max(fg_ys) + pad)

    color_crop = color_rgba.crop((bx0, by0, bx1 + 1, by1 + 1))
    alpha_crop = alpha.crop((bx0, by0, bx1 + 1, by1 + 1))

    cw, ch = alpha_crop.size
    print(f"Color crop: {cw}x{ch}  aspect={cw / max(1, ch):.2f}")

    out_px_h = max(4, int(out_w * (ch / max(1, cw)) * 0.55 * 2))
    if out_px_h % 2:
        out_px_h += 1
    print(f"Output   : {out_w}x{out_px_h} px -> {out_px_h // 2} terminal rows")

    alpha_s = alpha_crop.resize((out_w, out_px_h), Image.Resampling.BOX)
    color_s = color_crop.resize((out_w, out_px_h), Image.Resampling.LANCZOS)
    ap = alpha_s.load()
    cp = color_s.load()
    fg_threshold = 64

    def fg(x, y):
        return ap[x, y] >= fg_threshold

    x0, y0, x1, y1 = 0, 0, out_w - 1, out_px_h - 1
    while y0 < y1 and not any(fg(xx, y0) for xx in range(out_w)):
        y0 += 1
    while y1 > y0 and not any(fg(xx, y1) for xx in range(out_w)):
        y1 -= 1
    while x0 < x1 and not any(fg(x0, yy) for yy in range(out_px_h)):
        x0 += 1
    while x1 > x0 and not any(fg(x1, yy) for yy in range(out_px_h)):
        x1 -= 1
    if ((y1 - y0 + 1) % 2) != 0 and y1 > y0:
        y1 -= 1

    rows = []
    for y in range(y0, y1 + 1, 2):
        row = []
        for x in range(x0, x1 + 1):
            tf = fg(x, y)
            bf = fg(x, y + 1) if (y + 1) <= y1 else False
            if not tf and not bf:
                row.append((" ", None, None))
                continue
            tr, tg, tb, _ = cp[x, y]
            br, bg, bb, _ = cp[x, y + 1] if (y + 1) <= y1 else (0, 0, 0, 0)
            if tf and bf:
                row.append(("?", (tr, tg, tb), (br, bg, bb)))
            elif tf:
                row.append(("?", (tr, tg, tb), (0, 0, 0)))
            else:
                row.append(("?", (br, bg, bb), (0, 0, 0)))
        rows.append(row)
    return rows


def rows_to_html(rows):
    lines = []
    for row in rows:
        spans = []
        for ch, fg_c, bg_c in row:
            if fg_c is None:
                spans.append("&nbsp;")
            else:
                spans.append(
                    f'<span style="color:rgb{fg_c};background:rgb{bg_c};">{ch}</span>'
                )
        lines.append("".join(spans))
    return "\n".join(lines)


rows = render()
html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>DBForged Logo Preview</title>
<style>
  body {{ background:#000; margin:20px; }}
  pre  {{ font-family:"Courier New",Courier,monospace; font-size:14px;
          line-height:1.0; background:#000; color:#fff; white-space:pre; }}
  .info {{ color:#666; font-size:11px; margin-top:8px; }}
</style>
</head>
<body>
<pre>{rows_to_html(rows)}</pre>
<p class="info">{len(rows)} terminal rows x {len(rows[0]) if rows else 0} cols - color: {COLOR_PATH.name}</p>
</body></html>"""

OUT = REPO / "logo_preview.html"
OUT.write_text(html, encoding="utf-8")
print(f"Saved: {OUT}")
