#!/usr/bin/env python3
"""s22p01 — 체관요소 셋 가운데 **가운데**(머리 없는 사람 y≈500..620)에만 옆방 조수(반세포)가 없었다(logic_0929 s22p01 6 M).
6행 「반세포 — 체관요소마다 하나씩 붙는다」 → 맨 위 조수 옆방(x 884..952 × y 192..342)을 그대로 떠서 dy=+285 로 가운데 체관요소 곁 나무껍질에 붙인다.
붙일 자리(y 477..627)는 민 나무껍질이다. 위아래 8px · 오른쪽 4px 섞음, 왼쪽(관 벽 쪽)은 그대로 이어 붙인다.
사용: python3 tools/retouch/s22p01_middle_companion.py <입력.png> <출력.png>"""
import sys
import numpy as np
from PIL import Image
src, out = sys.argv[1:3]
a = np.asarray(Image.open(src).convert('RGB').resize((1024, 1024), Image.LANCZOS), dtype=float)
X0, X1, Y0, Y1, DY = 884, 952, 192, 342, 285
H, W = Y1 - Y0, X1 - X0
w = np.ones((H, W))
F = 8
for i in range(F):
    w[i, :] *= (i + 1) / F
    w[H - 1 - i, :] *= (i + 1) / F
for j in range(4):
    w[:, W - 1 - j] *= (j + 1) / 4
w = w[..., None]
b = a.copy()
b[Y0 + DY:Y1 + DY, X0:X1] = a[Y0:Y1, X0:X1] * w + a[Y0 + DY:Y1 + DY, X0:X1] * (1 - w)
Image.fromarray(b.round().clip(0, 255).astype(np.uint8)).save(out)
print('saved', out)
