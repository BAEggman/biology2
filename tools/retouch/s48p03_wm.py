#!/usr/bin/env python3
"""s48p03 — 제미나이 v1(도장 셋 자리마다 줄이 끊겨 끝이 말림 · 가운데 도장 없는 곳의 끊김은 이어 붙임)에
오른쪽 아래 창고 벽 밑동의 반짝이 표식(x 928..956 · y 398..433)이 남음 → 25px 왼쪽 벽·바닥 결로 덮음(가장자리 6px 섞음).
사용: python3 s48p03_wm.py V1.png OUT.png"""
import sys
import numpy as np
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB'); W, H = im.size
assert (W, H) == (1024, 506), (W, H)
a = np.asarray(im).astype(np.float32); out = a.copy()
X0, X1, Y0, Y1, OFF, F = 926, 960, 396, 436, -25, 6
for x in range(X0, X1):
    wx = min(1.0, (x - X0 + 1) / F, (X1 - x) / F)
    for y in range(Y0, Y1):
        wy = min(1.0, (y - Y0 + 1) / 3.0, (Y1 - y) / 3.0)
        w = wx * wy
        out[y, x] = out[y, x] * (1 - w) + a[y, x + OFF] * w
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst); print('ok', dst)
