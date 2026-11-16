#!/usr/bin/env python3
# L35c_pil.py <in.png> <out.png> — L35c 끝손질(2026-11-16 · 일치 검사 1회 뒤).
#  1) 일꾼 발치에 늘어진 새끼 오리에 검은 얼룩점 — 「얼룩 새끼(잡종)」가 흰 새로 읽혔다(일치 검사 1회 s17 △).
import sys
from PIL import Image, ImageDraw
src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')
x0, y0, x1, y1 = 1238, 190, 1282, 216; S = 8                     # 새끼 둘레만 키워 그리고 줄인다(테두리 부드럽게)
patch = im.crop((x0, y0, x1, y1)).resize(((x1 - x0) * S, (y1 - y0) * S), Image.LANCZOS)
m = Image.new('L', patch.size, 0); d = ImageDraw.Draw(m)
for cx, cy, r in ((1249.5, 202.0, 1.5), (1255.5, 200.8, 1.3), (1260.8, 203.6, 1.5), (1252.0, 206.2, 1.3), (1265.6, 201.2, 1.3), (1246.2, 205.0, 1.2), (1263.2, 207.0, 1.1)):
    d.ellipse([(cx - x0 - r) * S, (cy - y0 - r) * S, (cx - x0 + r) * S, (cy - y0 + r) * S], fill=255)
dark = Image.new('RGB', patch.size, (34, 32, 36))
patch = Image.composite(dark, patch, m).resize((x1 - x0, y1 - y0), Image.LANCZOS)
im.paste(patch, (x0, y0)); im.save(dst)
print('speckles', dst)
