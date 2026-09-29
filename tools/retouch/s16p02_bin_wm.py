#!/usr/bin/env python3
"""s16p02 — 개념 논리 M(PDE: cAMP → 5′-AMP, AC 의 역반응 아님): 제미나이 v1(짧은 토막 · 통과 바닥에 짧은 토막 · 왼쪽 바닥의 긴 막대는 그대로 —
장면을 조금 넓혀 다시 그림, 모든 소품 그대로)을 쓰고, 통 왼쪽 면의 반짝이 표식(x 926..952 · y 452..494)만 그 면의 한 색 + 잔잡음으로 덮음.
사용: python3 s16p02_bin_wm.py V1.png OUT.png"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
src, dst = sys.argv[1], sys.argv[2]
a = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
assert a.shape == (559, 1024, 3), a.shape
rng = np.random.default_rng(162)
X0, X1, Y0, Y1 = 926, 953, 452, 495
sub = a[Y0:Y1, X0:X1]
lum = sub.mean(2)
face = np.median(sub[(lum > 120) & (lum < 205)], axis=0)
m = lum > face.mean() + 9
m = ndi.binary_dilation(m, iterations=1)
# keep the dark outline strokes of the bin (lum < 110)
m &= lum > 110
sub[m] = np.clip(face + rng.normal(0, 2.0, (m.sum(), 3)), 0, 255)
a[Y0:Y1, X0:X1] = sub
Image.fromarray(a.astype(np.uint8)).save(dst); print('face', face.astype(int), 'px', int(m.sum()))
