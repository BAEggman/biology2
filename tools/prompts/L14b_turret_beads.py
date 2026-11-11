#!/usr/bin/env python3
# turret_beads.py in out — 손가락 탑(미세융모) 셋에 살구색 구슬 줄 심을 그려 넣는다(다른 탑과 같은 꼴)
import sys
from PIL import Image, ImageDraw
src, dst = sys.argv[1], sys.argv[2]
S = 6
im = Image.open(src).convert('RGB')
cols = [(292, 163, 218), (523.5, 152, 216), (742, 152, 218)]   # (x, 위 끝 y, 아래 끝 y)
for x, ya, yb in cols:
    x0, y0, x1, y1 = int(x - 12), int(ya - 8), int(x + 12), int(yb + 6)
    reg = im.crop((x0, y0, x1, y1)).resize(((x1 - x0) * S, (y1 - y0) * S), Image.LANCZOS)
    d = ImageDraw.Draw(reg)
    y = ya
    while y <= yb:
        cx, cy = (x - x0) * S, (y - y0) * S; R = 2.7 * S
        d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(222, 166, 128), outline=(88, 48, 30), width=int(1.35 * S))
        y += 5.3
    reg = reg.resize((x1 - x0, y1 - y0), Image.LANCZOS)
    im.paste(reg, (x0, y0))
im.save(dst)
