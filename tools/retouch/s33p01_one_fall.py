#!/usr/bin/env python3
"""s33p01 — 개념 논리 m 4: 물줄기가 네 번 떨어지던 것(둘째 다리 아래가 가운데 턱에서 한 번 더 꺾임) → 비가역 3단계대로 **폭포 셋**
(맨 위 → 첫 다리 · 첫 다리 → 둘째 다리 · 둘째 다리 → 맨 아래 웅덩이 한 번에).
제미나이 v1 에서 둘째 다리 아래 폭포 자리만(x 480..800 · y 400..920 안, σ2 밝기 차 > 12 → 닫기 3 · 메움 · 넓힘 5 · σ2 섞음) 원본에 옮기고,
오른쪽 아래 바위 위의 옛 흐린 반짝이 표식(원본부터 있던 것, 중심 ≈ (905,905))은 바위 결의 검은 선을 두고 「둘레보다 밝은」 화소만 둘레 밝기로 낮춘다.
사용: python3 s33p01_one_fall.py ORIG.png V1.png OUT.png"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
op, vp, dst = sys.argv[1], sys.argv[2], sys.argv[3]
O = np.asarray(Image.open(op).convert('RGB')).astype(np.float64)
V = np.asarray(Image.open(vp).convert('RGB')).astype(np.float64)
H, W = O.shape[:2]
d = ndi.gaussian_filter(np.abs(O - V).mean(axis=2), 2.0)
b = np.zeros((H, W), bool); b[400:920, 480:800] = True
m = (d > 12) & b
m = ndi.binary_closing(m, iterations=3)
m = ndi.binary_fill_holes(m)
m = ndi.binary_dilation(m, iterations=5) & b
w = ndi.gaussian_filter(m.astype(float), 2.0)
out = O * (1 - w[..., None]) + V * w[..., None]
print('paste px', int(m.sum()))
# 옛 반짝이
X0, X1, Y0, Y1 = 872, 940, 866, 940
sub = out[Y0:Y1, X0:X1]
L = sub.mean(axis=2)
dark = ndi.binary_dilation(L < 110, iterations=1)
Lm = np.where(dark, np.nan, L)
pad = np.pad(Lm, 12, mode='reflect')
from numpy.lib.stride_tricks import sliding_window_view
win = sliding_window_view(pad, (25, 25))
bgL = np.nanpercentile(win.reshape(win.shape[0], win.shape[1], -1), 35, axis=2)
yy, xx = np.mgrid[0:sub.shape[0], 0:sub.shape[1]]
cx, cy = 905 - X0, 905 - Y0
disc = np.hypot(xx - cx, yy - cy) <= 30
bright = (L > bgL + 5) & ~dark & disc
bright = ndi.binary_dilation(ndi.binary_opening(bright, iterations=1), iterations=1) & ~dark
f = np.where(bright, bgL / np.maximum(L, 1), 1.0)
f = ndi.gaussian_filter(f, 1.0)
out[Y0:Y1, X0:X1] = sub * f[..., None]
print('old sparkle px', int(bright.sum()))
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst)
print('saved', dst)
