#!/usr/bin/env python3
"""Build docs/app-<lang>.png and docs/app-languages.png from app screenshots.

Usage: python3 tools/montage.py SCREENSHOT_DIR     (needs: pip install pillow)
The screenshots come from:  dotcleaner_gui.py --screenshots SCREENSHOT_DIR
"""
import os
import shutil
import sys

from PIL import Image

LANGS = ["en", "fr", "es", "zh", "hi"]
src = sys.argv[1]
docs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")
os.makedirs(docs, exist_ok=True)

shots = []
for code in LANGS:
    path = os.path.join(src, f"app-{code}.png")
    shutil.copy(path, os.path.join(docs, f"app-{code}.png"))
    shots.append(Image.open(path).convert("RGB"))

# 3 + 2 grid, every screenshot scaled to the same width
w = 600
scaled = [im.resize((w, round(im.height * w / im.width)), Image.LANCZOS) for im in shots]
h = max(im.height for im in scaled)
gap = 24
sheet = Image.new("RGB", (3 * w + 4 * gap, 2 * h + 3 * gap), "white")
for i, im in enumerate(scaled):
    row, col = divmod(i, 3)
    x = gap + col * (w + gap) + (0 if row == 0 else (w + gap) // 2)
    sheet.paste(im, (x, gap + row * (h + gap)))
sheet.save(os.path.join(docs, "app-languages.png"), optimize=True)
print("docs/app-*.png and docs/app-languages.png updated")
