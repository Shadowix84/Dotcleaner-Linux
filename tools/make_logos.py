#!/usr/bin/env python3
"""
Draws the Dotcleaner icon for the console menus, in the same style as other Knulli tools
(e.g. PlayTime): one big square PNG, transparent background, white shapes with a thick
black outline and one accent colour.

  console/icons/dotcleaner.png           1024 x 1024  shown in the Ports / Tools menu
  console/Onion/App/Dotcleaner/icon.png    64 x 64    Onion app icon

The launcher adds itself to the menu's gamelist.xml with <image>./icons/dotcleaner.png</image>.
Run:  python3 tools/make_logos.py   (needs Pillow)
"""
import math
import os
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
S = 4                                   # draw 4x bigger, then shrink: smooth edges
WHITE, BLACK, ACCENT, GREY = "#ffffff", "#111111", "#2f6fde", "#e9e9e9"


def rounded(points, r, steps=12):
    """Polygon with rounded corners (radius r) as a list of points."""
    out = []
    n = len(points)
    for i in range(n):
        p0, p1, p2 = points[i - 1], points[i], points[(i + 1) % n]
        v1 = (p0[0] - p1[0], p0[1] - p1[1])
        v2 = (p2[0] - p1[0], p2[1] - p1[1])
        l1, l2 = math.hypot(*v1), math.hypot(*v2)
        u1, u2 = (v1[0] / l1, v1[1] / l1), (v2[0] / l2, v2[1] / l2)
        a = math.acos(max(-1, min(1, u1[0] * u2[0] + u1[1] * u2[1])))
        d = min(r / math.tan(a / 2), l1 / 2, l2 / 2)
        s = (p1[0] + u1[0] * d, p1[1] + u1[1] * d)
        e = (p1[0] + u2[0] * d, p1[1] + u2[1] * d)
        for k in range(steps + 1):          # quadratic curve through the corner
            t = k / steps
            out.append(((1 - t) ** 2 * s[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * e[0],
                        (1 - t) ** 2 * s[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * e[1]))
    return out


def outlined(d, pts, fill, stroke):
    """Filled shape with a black outline centred on its edge."""
    d.polygon(pts, fill=fill)
    d.line(pts + pts[:2], fill=BLACK, width=stroke, joint="curve")


def star(cx, cy, r, pinch=0.22, steps=24):
    """Four-pointed sparkle with curved sides."""
    pts = []
    tips = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    for i in range(4):
        a, b = tips[i], tips[(i + 1) % 4]
        c = (cx + (a[0] + b[0] - 2 * cx) * pinch, cy + (a[1] + b[1] - 2 * cy) * pinch)
        for k in range(steps):
            t = k / steps
            pts.append(((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * c[0] + t ** 2 * b[0],
                        (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * c[1] + t ** 2 * b[1]))
    return pts


def icon(size):
    B = size * S
    img = Image.new("RGBA", (B, B), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    st = int(B * 0.030)                                       # outline width (like PlayTime)

    # faint grey ring behind, like the clock face behind PlayTime's controller
    d.ellipse([B * 0.36, B * 0.06, B * 0.94, B * 0.64], outline=GREY, width=int(B * 0.035))

    # SD card: rounded, top-right corner cut
    x0, y0, x1, y1 = B * 0.16, B * 0.14, B * 0.64, B * 0.88
    cut = (x1 - x0) * 0.30
    card = rounded([(x0, y0), (x1 - cut, y0), (x1, y0 + cut), (x1, y1), (x0, y1)], B * 0.05)
    outlined(d, card, WHITE, st)

    # contacts (black, like the D-pad)
    w, h, gap = B * 0.048, B * 0.15, B * 0.028
    x = x0 + B * 0.075
    for _ in range(4):
        d.rounded_rectangle([x, y0 + B * 0.075, x + w, y0 + B * 0.075 + h], radius=w * 0.45, fill=BLACK)
        x += w + gap
    # label: one accent bar and two black lines
    d.rounded_rectangle([x0 + B * 0.075, y0 + B * 0.40, x1 - B * 0.075, y0 + B * 0.47],
                        radius=B * 0.035, fill=ACCENT)
    for i, f in enumerate((0.72, 0.50)):
        ly = y0 + B * (0.55 + i * 0.09)
        d.rounded_rectangle([x0 + B * 0.075, ly, x0 + B * 0.075 + (x1 - x0 - B * 0.15) * f, ly + B * 0.045],
                            radius=B * 0.022, fill=BLACK)

    # sparkles in the accent colour, with a transparent gap where they cross the card
    for cx, cy, r in ((B * 0.71, B * 0.73, B * 0.19), (B * 0.85, B * 0.42, B * 0.085)):
        mask = Image.new("L", img.size, 0)
        ImageDraw.Draw(mask).polygon(star(cx, cy, r + st * 1.6, pinch=0.26), fill=255)
        img.putalpha(Image.composite(Image.new("L", img.size, 0), img.getchannel("A"), mask))
        d = ImageDraw.Draw(img)
        d.polygon(star(cx, cy, r), fill=ACCENT)

    box = img.getbbox()                                       # fill the square, like PlayTime
    side = max(box[2] - box[0], box[3] - box[1]) * 1.04
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    canvas = Image.new("RGBA", (int(side), int(side)), (0, 0, 0, 0))
    canvas.paste(img.crop(box), (int(side / 2 - (cx - box[0])), int(side / 2 - (cy - box[1]))))
    return canvas.resize((size, size), Image.LANCZOS)


def main():
    out = os.path.join(ROOT, "console", "icons")
    os.makedirs(out, exist_ok=True)
    big = icon(1024)
    big.save(os.path.join(out, "dotcleaner.png"), optimize=True)
    big.resize((64, 64), Image.LANCZOS).save(
        os.path.join(ROOT, "console", "Onion", "App", "Dotcleaner", "icon.png"), optimize=True)
    print("icon saved in console/icons/dotcleaner.png and the Onion app")


if __name__ == "__main__":
    main()
