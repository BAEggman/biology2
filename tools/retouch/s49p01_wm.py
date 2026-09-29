#!/usr/bin/env python3
"""s49p01 — 개념 논리 M(소마토스타틴은 인슐린·글루카곤을 둘 다 억제): 삼각 모자(δ)가 두 손바닥으로 β(왼쪽)와 PP(오른쪽)를 누르고 α 는 멀던 것 →
제미나이 같은 대화 v2(δ 가 긴 장대 하나를 두 손으로 왼쪽으로만 뻗어 β 창 앞을 가로질러 α 의 곤봉 끝을 누름 · PP 쪽으로는 안 뻗음)를 쓰고,
오른쪽 아래 빈 바닥의 반짝이 표식(x 876..930 · y 876..930)만 둘레 바닥 한 색 + 잔잡음(가장자리 8px 섞음)으로 덮음.
사용: python3 s49p01_wm.py V2.png OUT.png"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
src, dst = sys.argv[1], sys.argv[2]
a = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
assert a.shape == (1024, 1024, 3), a.shape
rng = np.random.default_rng(491)
X0, X1, Y0, Y1 = 872, 934, 872, 934
ring = np.concatenate([a[Y0 - 14:Y0, X0:X1].reshape(-1, 3), a[Y1:Y1 + 14, X0:X1].reshape(-1, 3),
                       a[Y0:Y1, X0 - 14:X0].reshape(-1, 3), a[Y0:Y1, X1:X1 + 14].reshape(-1, 3)])
bg = np.median(ring, axis=0)
fill = ndi.gaussian_filter(np.clip(bg + rng.normal(0, 2.0, (Y1 - Y0, X1 - X0, 3)), 0, 255), sigma=(0.8, 0.8, 0))
w = np.ones((Y1 - Y0, X1 - X0), np.float32)
for i in range(8):
    t = (i + 1) / 9
    w[i, :] *= t; w[-1 - i, :] *= t; w[:, i] *= t; w[:, -1 - i] *= t
a[Y0:Y1, X0:X1] = a[Y0:Y1, X0:X1] * (1 - w[..., None]) + fill * w[..., None]
Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(dst); print('bg', bg.astype(int))
