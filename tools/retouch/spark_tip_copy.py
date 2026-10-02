#!/usr/bin/env python3
"""spark_tip_copy.py — 되돌림(spark_inv) 뒤 **별 끝 뾰족 부분**에 남은 얼룩만, 같은 그림의 위/아래(또는 옆) 결을 옮겨 덮는다.
별 끝은 가늘어 알파가 해석식보다 낮게 찍혀(무름) 되돌림이 지나치게 먹는다 — 결이 한 방향으로 이어지는 자리
(s20p02 세로 줄무늬 기둥)는 그 방향으로 몇 px 옮긴 원본 화소가 가장 자연스럽다.
상자 안을 (dx, dy) 만큼 떨어진 **원본(되돌리기 전)** 화소로 바꾸고, 둘레 3px 고리의 평균 차로 톤을 맞춘 뒤 σ1 섞음.
사용: python3 spark_tip_copy.py ORIG.png INV.png OUT.png x0,y0,x1,y1:dx,dy [...]"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
O = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(np.float64)
J = np.asarray(Image.open(sys.argv[2]).convert('RGB')).astype(np.float64)
out = J.copy()
H, W = J.shape[:2]
for spec in sys.argv[4:]:
    b, d = spec.split(':')
    x0, y0, x1, y1 = map(int, b.split(',')); dx, dy = map(int, d.split(','))
    m = np.zeros((H, W), bool); m[y0:y1, x0:x1] = True
    src = np.roll(np.roll(O, -dy, axis=0), -dx, axis=1)
    ring = ndi.binary_dilation(m, iterations=3) & ~m
    off = (J[ring] - src[ring]).mean(axis=0)
    w = ndi.gaussian_filter(m.astype(float), 1.0)
    w = np.maximum(w, m.astype(float) * 0.0 + ndi.binary_erosion(m, iterations=1))
    out = out * (1 - w[..., None]) + (src + off) * w[..., None]
    print('box', (x0, y0, x1, y1), 'from', (dx, dy), 'tone', off.round(1))
Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)).save(sys.argv[3])
