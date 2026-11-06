#!/usr/bin/env python3
"""pipe_lines.py — s31u01 v2: 놋쇠 관 둘에 들어가는 동전 위에 「떨어져 들어가는」 세로 선(먹) 셋씩 + 오른쪽 동전 뒤 반쯤 가린 방울 자국 지움.
b143 A 가 관 동전을 「순생성」으로 거꾸로 읽음 → 넣는 쪽(투자)을 동작으로. 사용: pipe_lines.py in.png out.png (2배 캔버스 좌표)"""
import sys, numpy as np
from PIL import Image, ImageDraw
src, dst = sys.argv[1:3]
im = Image.open(src).convert('RGB'); A = np.asarray(im).astype(float)
# ① 오른쪽 동전 뒤 방울 자국(회청 · 노랗지 않은 화소)을 그 줄의 하늘빛으로
for y in range(184, 220):
    sky = A[y, 418:428].mean(0)
    for x in range(386, 416):
        r, g, b = A[y, x]
        if abs(r - b) < 34 and not (r > 150 and g > 120 and b < 110):
            A[y, x] = sky
im = Image.fromarray(np.clip(A, 0, 255).astype('uint8'))
# ② 세로 선 — 4배로 그려 줄임
S = 4; x0, y0, x1, y1 = 310, 170, 420, 230
big = im.crop((x0, y0, x1, y1)).resize(((x1 - x0) * S, (y1 - y0) * S), Image.LANCZOS)
d = ImageDraw.Draw(big)
ink = (58, 52, 46)
for (cx, top) in [(340, 222), (385, 202)]:
    for dx, ln in [(-8, 9), (0, 12), (8, 9)]:
        X = (cx + dx - x0) * S; Yb = (top - 5 - y0) * S; Yt = Yb - ln * S
        d.line([(X, Yt), (X, Yb)], fill=ink, width=int(1.8 * S))
small = big.resize((x1 - x0, y1 - y0), Image.LANCZOS)
im.paste(small, (x0, y0))
im.save(dst); print('ok')
