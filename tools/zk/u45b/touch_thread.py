#!/usr/bin/env python3
"""touch_thread.py — s45u02 v2: cur5c → cur5 · 걸상 위 사상조류를 「굵은 마디 실 한 오라기」로 다시 긋는다
 (b131 — 가는 초록 줄이 걸상 뒷모서리 띠로 묻혀 「한 오라기가 모든 파장을 받는다」가 안 섰다).
 세포 칸(마디)이 줄줄이 이어진 실 — 일곱 띠를 모두 가로지른다. 헤엄이는 이 위에 paste_d2 로 다시 붙는다."""
import sys, os, math, numpy as np
from PIL import Image, ImageDraw
os.chdir(sys.argv[1] if len(sys.argv) > 1 else '.')
img = Image.open('cur5c.png').convert('RGB'); W, H = img.size
SS = 4
ty = lambda x: 611 + (x - 1560) * 0.117 + 2.5
x0, x1 = 1572, 1994
lay = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
S = lambda x, y: (x * SS, y * SS)
OUT, FILL, HL, WALL = (28, 62, 26, 255), (70, 138, 58, 255), (150, 204, 118, 255), (36, 86, 34, 255)
pts = [S(x, ty(x)) for x in np.linspace(x0, x1, 120)]
d.line(pts, fill=OUT, width=int(SS * 7.0), joint='curve')
d.line(pts, fill=FILL, width=int(SS * 4.6), joint='curve')
d.line([S(x, ty(x) - 1.2) for x in np.linspace(x0 + 2, x1 - 2, 120)], fill=HL, width=int(SS * 1.1), joint='curve')
ang = math.atan(0.117); nx, ny = -math.sin(ang), math.cos(ang)
x = x0 + 6
while x < x1 - 4:
    cx, cy = x, ty(x)
    d.line([S(cx - nx * 2.6, cy - ny * 2.6), S(cx + nx * 2.6, cy + ny * 2.6)], fill=WALL, width=int(SS * 1.0))
    x += 10.5
for xe in (x0, x1):   # 둥근 끝
    d.ellipse([S(xe - 3.4, ty(xe) - 3.4), S(xe + 3.4, ty(xe) + 3.4)], fill=FILL, outline=OUT, width=int(SS * 1.0))
im2 = img.convert('RGBA'); im2.alpha_composite(lay.resize((W, H), Image.LANCZOS)); img = im2.convert('RGB')
img.save('cur5.png')
img.crop((1560, 580, 2010, 680)).resize((900, 200), Image.LANCZOS).save('v5_thread.png')
print('cur5 (thread) saved')
