#!/usr/bin/env python3
"""s36p02 — 담장 왼쪽 아래 밑선 위의 서명 같은 낙서(「Cruz」 비슷한 필기체)를 지운다. 원본부터 있던 것 · 덱 규칙 「글자 없음」.
낙서 둘레(x 31..79, y 722..748)를 줄마다 왼쪽 깨끗한 칸(x 12..29)의 중앙값으로 채우고(담 돌 · 밑선 · 모래 땅이 줄 단위로 이어진다),
같은 칸의 표준편차만큼 잡음을 얹어 결을 맞춘다. 가장자리 3px 섞음.
사용: python3 tools/retouch/s36p02_erase_scribble.py <입력.png> <출력.png>"""
import sys
import numpy as np
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
a = np.asarray(Image.open(src).convert('RGB').resize((1024, 1024), Image.LANCZOS), dtype=float)
b = a.copy()
rng = np.random.default_rng(7)
X0, X1, Y0, Y1, F = 31, 79, 722, 748, 3
for y in range(Y0, Y1 + 1):
    ref = a[y, 12:30]
    med = np.median(ref, axis=0); sd = ref.std(axis=0).mean() * 0.6
    for x in range(X0, X1 + 1):
        w = min(1.0, (x - X0 + 1) / F, (X1 - x + 1) / F)
        v = med + rng.normal(0, sd, 3)
        b[y, x] = a[y, x] * (1 - w) + v * w
Image.fromarray(b.round().clip(0, 255).astype(np.uint8)).save(out)
print('saved', out)
