#!/usr/bin/env python3
"""s31p01 — 개념 논리 m 7: 해당과정에서 NADH 가 생기는 유일한 단계(G3P 탈수소)의 양동이가 **비어** 있던 것(빈 양동이 = NAD⁺) →
가득 차 넘치는 양동이(= NADH 로 채워짐). 제미나이 v1 에서 양동이 자리(x 540..720 · y 860..1000)만 옮겨 붙이고(σ2 밝기 차 > 12 · 닫기 3 ·
메움 · 넓힘 4 · σ2 섞음), 오른쪽 아래 인부 바짓가랑이 위의 옛 반짝이 표식(중심 ≈ (902,903))은 검은 윤곽과 크림 바탕을 두고
「둘레(25px 창 35 백분위)보다 3 넘게 밝은」 바지 화소만 둘레 밝기로 낮춘다.
사용: python3 s31p01_bucket_paste.py ORIG.png V1.png OUT.png"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from numpy.lib.stride_tricks import sliding_window_view
op, vp, dst = sys.argv[1], sys.argv[2], sys.argv[3]
O = np.asarray(Image.open(op).convert('RGB')).astype(np.float64)
V = np.asarray(Image.open(vp).convert('RGB')).astype(np.float64)
H, W = O.shape[:2]
d = ndi.gaussian_filter(np.abs(O - V).mean(axis=2), 2.0)
b = np.zeros((H, W), bool); b[860:1000, 540:720] = True
m = (d > 12) & b
m = ndi.binary_closing(m, iterations=3)
m = ndi.binary_fill_holes(m)
m = ndi.binary_dilation(m, iterations=4) & b
w = ndi.gaussian_filter(m.astype(float), 2.0)
out = O * (1 - w[..., None]) + V * w[..., None]
print('paste px', int(m.sum()))
def unspark(out, cx, cy, R=46, lo=110, hi=230):
    X0, X1, Y0, Y1 = cx - R, cx + R, cy - R, cy + R
    sub = out[Y0:Y1, X0:X1]
    L = sub.mean(axis=2)
    keep = (L >= lo) & (L <= hi)                       # 검은 윤곽 · 크림 바탕 제외
    Lm = np.where(ndi.binary_erosion(keep, iterations=1), L, np.nan)
    pad = np.pad(Lm, 12, mode='reflect')
    win = sliding_window_view(pad, (25, 25))
    bgL = np.nanpercentile(win.reshape(win.shape[0], win.shape[1], -1), 35, axis=2)
    yy, xx = np.mgrid[0:sub.shape[0], 0:sub.shape[1]]
    disc = np.hypot(xx - R, yy - R) <= R
    bright = (L > bgL + 3) & keep & disc & ~np.isnan(bgL)
    bright = ndi.binary_dilation(ndi.binary_opening(bright, iterations=1), iterations=1) & keep
    f = np.where(bright, np.nan_to_num(bgL, nan=1.0) / np.maximum(L, 1), 1.0)
    f = ndi.gaussian_filter(f, 1.0)
    out[Y0:Y1, X0:X1] = sub * f[..., None]
    return int(bright.sum())
print('sparkle px', unspark(out, 902, 903))
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst)
print('saved', dst)
