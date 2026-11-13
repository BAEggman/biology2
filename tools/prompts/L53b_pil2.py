#!/usr/bin/env python3
# L53b_pil2.py — E2 · E3 뒤: 판자 벽 아래 띠 속 물방울 줄에 ↓ 작은 화살(삼투 — 물이 아래로 · 일치 검사 1회 △)
import sys
from PIL import Image, ImageDraw
src, dst = sys.argv[1], sys.argv[2]
pil = Image.open(src).convert('RGB'); S = 4; INK = (22, 20, 18, 255)
def arrow(x, y0, y1, w=5.5):
    up = y1 < y0; top, bot = min(y0, y1), max(y0, y1); x0 = x - 16; W = 32; H = bot - top + 8; yb = top - 4
    lay = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    def T(px, py): return ((px - x0) * S, (py - yb) * S)
    if up:
        d.line([T(x, bot), T(x, top + 12)], fill=INK, width=int(w * S)); d.polygon([T(x, top), T(x - 11, top + 15), T(x + 11, top + 15)], fill=INK)
    else:
        d.line([T(x, top), T(x, bot - 12)], fill=INK, width=int(w * S)); d.polygon([T(x, bot), T(x - 11, bot - 15), T(x + 11, bot - 15)], fill=INK)
    lay = lay.resize((W, H), Image.LANCZOS); pil.paste(lay, (x0, yb), lay)
arrow(805, 547, 606)
pil.save(dst); print('ok')
