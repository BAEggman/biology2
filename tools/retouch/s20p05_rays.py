#!/usr/bin/env python3
"""s20p05 — 개념 논리 m 1·7(다섯이 같은 빛을 받는다): 창의 옅은 파란 빛살이 셋째 화분께에서 끝나 넷째·다섯째가 빛 밖이던 것 →
제미나이 v1(같은 높이·각도의 빛살을 오른쪽 끝까지 · 식물 뒤로)의 **벽 면만** 옮긴다(식물·화분·탁자·창은 원본).
  벽 가면 = 원본이 크림(L > 78 · 채도 < 25)이고 v1 도 밝은(L > 70) 화소를 2px 깎은 것(식물·화분 윤곽 곁 1px 어긋남을 뺌) · x ≥ 160(벽 모서리 선 오른쪽) · y < 430(탁자 위).
  톤 맞춤: 빛살이 없는 벽 화소(|Δb*| < 1.5)에서 (원본 − v1)을 σ30 정규화 합성곱으로 번져 v1 에 더함.
  (빛살 화소만 문턱으로 고르면 옅은 줄이 점선처럼 끊겼다 — 첫 안, 버림.)
사용: python3 s20p05_rays.py ORIG.png V1.png OUT.png"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import color

op, vp, dst = sys.argv[1], sys.argv[2], sys.argv[3]
O = np.asarray(Image.open(op).convert('RGB')).astype(np.float64)
V = np.asarray(Image.open(vp).convert('RGB')).astype(np.float64)
assert O.shape == V.shape
H, W = O.shape[:2]
Lo = color.rgb2lab(O / 255); Lv = color.rgb2lab(V / 255)
chroma = np.hypot(Lo[..., 1], Lo[..., 2])
wall = (Lo[..., 0] > 78) & (chroma < 25) & (Lv[..., 0] > 70)
yy, xx = np.mgrid[0:H, 0:W]
wall &= (xx >= 160) & (yy < 430)
wall_er = ndi.binary_erosion(wall, iterations=2)
lab_, n_ = ndi.label(wall_er)
sz = ndi.sum(wall_er, lab_, range(1, n_ + 1))
wall_er = np.isin(lab_, 1 + np.flatnonzero(sz >= 200))
calm = wall_er & (np.abs(Lo[..., 2] - Lv[..., 2]) < 1.5) & (np.abs(Lo[..., 0] - Lv[..., 0]) < 4)
D = np.zeros_like(O)
den = ndi.gaussian_filter(calm.astype(float), 30)
for k in range(3):
    D[..., k] = ndi.gaussian_filter((O[..., k] - V[..., k]) * calm, 30) / np.maximum(den, 1e-6)
Vt = V + D
w = ndi.gaussian_filter(wall_er.astype(float), 0.8) * wall_er
out = O * (1 - w[..., None]) + Vt * w[..., None]
Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)).save(dst)
print('wall px', int(wall_er.sum()), 'calm px', int(calm.sum()), 'mean tone shift', D[wall_er].mean(axis=0).round(1))
