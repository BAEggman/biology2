#!/usr/bin/env python3
"""s19p02c — 빗장의 p53 판 「점 다섯 · 점 셋」에서 오른쪽 판이 원본부터 점 **둘**(주사위 2)이었다 → 53 이 아니라 52 로 읽힘.
두 빗장 모두 오른쪽 판 가운데에 점 하나를 더해 주사위 3(대각선 셋)으로. 같은 빗장의 점 다섯 판 가운데 점을 떼어
(판 바탕보다 어두운 화소만) 두 점의 한가운데에 옮겨 붙인다 — 새 획 없음, 같은 그림 안의 점을 옮김.
사용: python3 tools/retouch/s19p02c_die_three.py <src.png> <out.png>"""
import sys
import numpy as np
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')
a = np.asarray(im).astype(np.int32).copy()
def dot_center(x, y, r=5):
    """(x,y) 둘레 창에서 가장 어두운 덩어리의 무게중심"""
    x, y = int(round(x)), int(round(y))
    w = a[y-r:y+r+1, x-r:x+r+1].sum(2)
    thr = w.min() + 0.5*(np.median(w) - w.min())
    ys, xs = np.nonzero(w < thr)
    return x - r + xs.mean(), y - r + ys.mean()
# (5판 가운데 점 대략 자리, 2판 두 점 대략 자리)
PAIRS = [((158.0, 196.0), (179.7, 193.0), (188.8, 205.0)),
         ((215.5, 320.5), (237.5, 314.8), (248.5, 325.8))]
R = 4
for src_pt, d1, d2 in PAIRS:
    sx, sy = dot_center(*src_pt)
    p1 = dot_center(*d1); p2 = dot_center(*d2)
    tx, ty = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
    sx, sy, tx, ty = int(round(sx)), int(round(sy)), int(round(tx)), int(round(ty))
    patch = a[sy-R:sy+R+1, sx-R:sx+R+1].copy()
    bg = np.median(a[ty-R-3:ty+R+4, tx-R-3:tx+R+4].reshape(-1, 3), axis=0)
    lum = patch.sum(2)
    yy, xx = np.mgrid[-R:R+1, -R:R+1]
    mask = (lum < bg.sum() - 60) & (xx**2 + yy**2 <= 3.2**2)   # 점 하나만 — 둘레 다른 점·테두리는 빼고
    tgt = a[ty-R:ty+R+1, tx-R:tx+R+1]
    tgt[mask] = patch[mask]
    print('src', (sx, sy), '→ tgt', (tx, ty), 'dots', [tuple(round(v,1) for v in p1), tuple(round(v,1) for v in p2)], 'px', int(mask.sum()))
Image.fromarray(a.clip(0, 255).astype(np.uint8)).save(out)
