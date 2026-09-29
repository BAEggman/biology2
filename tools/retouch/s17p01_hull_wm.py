#!/usr/bin/env python3
"""s17p01 — 개념 논리 M(PAH 배의 궤짝 = 포도당 꾸러미로 읽힘): 제미나이 같은 대화 v2(하마 배의 궤짝을 모두 쇠테 두른 둥근 나무통으로 ·
v1 은 통 더미가 너무 높아 하마가 빈 가운데 배에 걸쳐 보여서 두 겹 아래로 낮춤)를 쓰고, 배 옆구리 판자의 반짝이 표식(x 878..928 · y 888..934)만
판자 결을 따라(기울기 ≈ −0.17) (−60, +10) 옮겨 덮음 · 가장자리 8px 섞음.
사용: python3 s17p01_hull_wm.py V2.png OUT.png"""
import sys
import numpy as np
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
a = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
assert a.shape == (1024, 1024, 3), a.shape
out = a.copy()
X0, X1, Y0, Y1, DX, DY, F = 874, 932, 884, 938, -60, 10, 8
for y in range(Y0, Y1):
    wy = min(1.0, (y - Y0 + 1) / F, (Y1 - y) / F)
    for x in range(X0, X1):
        wx = min(1.0, (x - X0 + 1) / F, (X1 - x) / F)
        w = wx * wy
        out[y, x] = a[y, x] * (1 - w) + a[y + DY, x + DX] * w
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst); print('ok', dst)
