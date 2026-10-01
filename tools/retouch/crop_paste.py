#!/usr/bin/env python3
"""crop_paste.py — **키운 조각**을 제미나이에 보낸 경우의 되옮기기(s21p02 · s18p02 방식의 일반판).
제미나이 출력(조각을 키운 크기)을 조각 상자 크기로 줄여 원본 크기의 V 를 만들고(상자 밖은 원본),
어긋남을 ±4px 에서 잰 뒤(바뀌지 않은 곳의 제곱차 최소), paste_boxes 와 같은 방식으로 **준 상자들 안의 바뀐 곳만** 옮긴다.
사용: python3 crop_paste.py ORIG.png GEM.png OUT.png CROP=x0,y0,x1,y1 THR x0,y0,x1,y1 [...]   (뒤 상자들은 원본 좌표)"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

op, gp, dst = sys.argv[1], sys.argv[2], sys.argv[3]
cx0, cy0, cx1, cy1 = (int(v) for v in sys.argv[4].split('=')[-1].split(','))
thr = float(sys.argv[5])
boxes = [tuple(int(v) for v in b.split(',')) for b in sys.argv[6:]]
O = np.asarray(Image.open(op).convert('RGB')).astype(np.float64)
H, W = O.shape[:2]
G = Image.open(gp).convert('RGB').resize((cx1 - cx0, cy1 - cy0), Image.LANCZOS)
Gc = np.asarray(G).astype(np.float64)
Oc = O[cy0:cy1, cx0:cx1]
# 어긋남: 상자들 밖(조각 안) 화소로 ±4px
keep = np.ones(Oc.shape[:2], bool)
for (x0, y0, x1, y1) in boxes:
    keep[max(0, y0 - cy0 - 8):max(0, y1 - cy0 + 8), max(0, x0 - cx0 - 8):max(0, x1 - cx0 + 8)] = False
keep[:6, :] = keep[-6:, :] = False; keep[:, :6] = keep[:, -6:] = False
best = None
for dy in range(-4, 5):
    for dx in range(-4, 5):
        Gs = np.roll(np.roll(Gc, dy, axis=0), dx, axis=1)
        e = ((Gs - Oc)[keep] ** 2).mean()
        if best is None or e < best[0]:
            best = (e, dx, dy)
e, dx, dy = best
Gc = np.roll(np.roll(Gc, dy, axis=0), dx, axis=1)
V = O.copy()
V[cy0:cy1, cx0:cx1] = Gc
d = ndi.gaussian_filter(np.abs(O - V).mean(axis=2), 2.0)
m = np.zeros((H, W), bool)
for (x0, y0, x1, y1) in boxes:
    b = np.zeros((H, W), bool)
    b[max(0, y0 - 6):min(H, y1 + 6), max(0, x0 - 6):min(W, x1 + 6)] = True
    mm = (d > thr) & b
    mm = ndi.binary_closing(mm, iterations=3)
    mm = ndi.binary_fill_holes(mm)
    mm = ndi.binary_dilation(mm, iterations=3) & b
    m |= mm
w = ndi.gaussian_filter(m.astype(float), 1.5)
out = O * (1 - w[..., None]) + V * w[..., None]
Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)).save(dst)
print('shift (%d, %d) rms %.1f  pasted px %d' % (dx, dy, np.sqrt(e), int(m.sum())))
