#!/usr/bin/env python3
"""
Draws the Dotcleaner logos with a transparent background, for the console menus:

  console/menu-logo/images/dotcleaner-image.png    512 x 512  SD card + sparkles  (<image>, <thumbnail>)
  console/menu-logo/images/dotcleaner-marquee.png  ~780 x 240 card + "Dotcleaner" (<marquee>: the logo)
  console/Onion/App/Dotcleaner/icon.png   64 x 64    Onion app icon

A dark outline keeps them readable on light and dark themes.
Run:  python3 tools/make_logos.py   (needs Pillow)
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
S = 4                                   # draw 4x bigger, then shrink: smooth edges
WHITE, BLUE, LIGHT, GOLD, OUTLINE = "#ffffff", "#2f6fde", "#a9c6f5", "#ffc928", "#13203a"
FONTS = ["/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]


def card_polygon(x, y, w, h, cut):
    """SD card outline: a rectangle with the top-right corner cut."""
    return [(x, y), (x + w - cut, y), (x + w, y + cut), (x + w, y + h), (x, y + h)]


def sparkle(d, cx, cy, r, fill, outline=None, width=0):
    """Four-pointed star."""
    k = r * 0.28
    pts = [(cx, cy - r), (cx + k, cy - k), (cx + r, cy), (cx + k, cy + k),
           (cx, cy + r), (cx - k, cy + k), (cx - r, cy), (cx - k, cy - k)]
    d.polygon(pts, fill=fill, outline=outline, width=width)


def draw_card(img, x, y, w, h, stroke):
    """The SD card with its contacts and label lines, plus two sparkles, at (x, y) size w x h."""
    d = ImageDraw.Draw(img)
    cut = w * 0.22
    poly = card_polygon(x, y, w, h, cut)
    # outline: the same shape, drawn bigger behind
    d.polygon(poly, fill=OUTLINE)
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).polygon(poly, fill=255)
    m = m.filter(ImageFilter.MaxFilter(stroke * 2 + 1))
    img.paste(Image.new("RGBA", img.size, OUTLINE), (0, 0), m)
    d.polygon(poly, fill=WHITE)
    # contacts
    pw, ph, gap = w * 0.085, h * 0.17, w * 0.045
    px = x + w * 0.12
    for i in range(5):
        if px + pw > x + w - cut * 0.55:
            break
        d.rounded_rectangle([px, y + h * 0.07, px + pw, y + h * 0.07 + ph], radius=pw * 0.35, fill=BLUE)
        px += pw + gap
    # label lines
    for i, f in enumerate((0.62, 0.48, 0.36)):
        ly = y + h * (0.46 + i * 0.12)
        d.rounded_rectangle([x + w * 0.14, ly, x + w * (0.14 + f), ly + h * 0.055], radius=h * 0.03, fill=LIGHT)
    # sparkles, with the same outline
    for cx, cy, r in ((x + w * 1.0, y + h * 0.78, w * 0.42), (x + w * 0.80, y + h * 1.04, w * 0.17)):
        sm = Image.new("L", img.size, 0)
        sparkle(ImageDraw.Draw(sm), cx, cy, r, 255)
        sm = sm.filter(ImageFilter.MaxFilter(stroke * 2 + 1))
        img.paste(Image.new("RGBA", img.size, OUTLINE), (0, 0), sm)
        sparkle(d, cx, cy, r, GOLD)


def logo_image(size):
    big = size * S
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    w, h = big * 0.50, big * 0.66
    draw_card(img, big * 0.17, big * 0.10, w, h, stroke=max(2, int(big * 0.018)))
    return img.resize((size, size), Image.LANCZOS)


def logo_marquee(width, height):
    W, H = width * S, height * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ch = H * 0.70
    stroke = max(2, int(H * 0.025))
    draw_card(img, H * 0.10, H * 0.08, ch * 0.76, ch, stroke)
    font = next((f for f in FONTS if os.path.exists(f)), None)
    size = int(H * 0.40)
    ft = ImageFont.truetype(font, size) if font else ImageFont.load_default()
    d = ImageDraw.Draw(img)
    tx, ty = H * 0.95, H * 0.5
    d.text((tx, ty), "Dotcleaner", font=ft, anchor="lm", fill=WHITE,
           stroke_width=int(stroke * 1.4), stroke_fill=OUTLINE)
    box = img.getbbox()                                   # trim the empty right side
    img = img.crop((0, 0, min(W, box[2] + H * 0.08), H))
    return img.resize((int(img.width / S), height), Image.LANCZOS)


def main():
    out = os.path.join(ROOT, "console", "menu-logo", "images")
    os.makedirs(out, exist_ok=True)
    logo_image(512).save(os.path.join(out, "dotcleaner-image.png"), optimize=True)
    logo_marquee(900, 240).save(os.path.join(out, "dotcleaner-marquee.png"), optimize=True)
    logo_image(64).save(os.path.join(ROOT, "console", "Onion", "App", "Dotcleaner", "icon.png"), optimize=True)
    print("logos saved in console/menu-logo/images and the Onion app")


if __name__ == "__main__":
    main()
