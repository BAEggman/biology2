#!/usr/bin/env python3
"""spark_faint.py — **흐린** 반짝이 표식(불투명도 a ≲ 0.3)을 덧씌움 식으로 되돌린다: I = (I′ − 255·a·M)/(1 − a·M).
a 가 작으면 잡음 키움(1/(1 − a))이 1.1~1.4 배라 결 · 물건 위에서도 선과 색이 그대로 남는다(또렷한 별 a 0.5~0.76 은 이 방법이 얼룩을 남겨
spark_clone · spark_grid 로 했다). 별 모양 M 은 spark_clone 과 같은 해석식(판마다 R · 중심 다시 맞춤, 8배 덧표본이라 가장자리가 부드럽다).
a 재기: 별 안(M > 0.98)과 바로 바깥 고리(경계에서 3..8px)가 **둘 다 평평한 크림**(L > 200 · 기울기 < 6)인 화소만 써서
  a = median((안 − 바깥 중앙값)/(255 − 바깥 중앙값)) — 채널 평균. 크림이 모자라면 둘레 결 그대로 쓴다(--a 로 박을 수 있다).
마무리: 크림 면(L > 200 · 선에서 2px 밖)에 남는 별 가장자리 테는 중앙값 7 로 고른다.
사용: python3 spark_faint.py SRC.png OUT.png [--at cx,cy,R] [--a A]"""
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spark_clone import star_mask_full, fit_geometry

args = sys.argv[1:]
src, dst = args[0], args[1]
at = None; A = None
if '--at' in args:
    at = tuple(float(v) for v in args[args.index('--at') + 1].split(','))
if '--a' in args:
    A = float(args[args.index('--a') + 1])
I = np.asarray(Image.open(src).convert('RGB')).astype(np.float64)
H, W = I.shape[:2]
L = I.mean(axis=2)
if at:
    c, R, cx, cy = fit_geometry(L, at[2], at[0], at[1], span=2.0)
else:
    c, R, cx, cy = fit_geometry(L)
M = star_mask_full(R, cx, cy, H, W)
if A is None:
    g = ndi.gaussian_gradient_magnitude(L, 1.0)
    inside = (M > 0.98) & (L > 200) & (g < 6)
    dout = ndi.distance_transform_edt(M < 0.01)
    ring = (M < 0.01) & (dout >= 3) & (dout <= 8) & (L > 190) & (g < 6)
    if inside.sum() < 30 or ring.sum() < 30:
        print('크림이 모자라 a 를 못 잼 — --a 로 박을 것'); sys.exit(1)
    B = np.median(I[ring], axis=0)
    a = np.median((I[inside] - B) / np.maximum(255 - B, 8), axis=0)
    A = float(np.clip(a.mean(), 0, 0.5))
    print('B', B.round(1), 'a per ch', a.round(3))
aM = (A * M)[..., None]
out = (I - 255.0 * aM) / (1.0 - aM)
# 크림 면에 남는 별 가장자리 테(실제 α 가 식보다 넓게 번진 것)는 크림 화소만 중앙값 7 로 고른다 — 선·물건(L < 150 에서 2px)은 건드리지 않음
Lo_ = out.mean(axis=2)
zone = ndi.binary_dilation(M > 0.01, iterations=3) & (Lo_ > 200) & ~ndi.binary_dilation(Lo_ < 150, iterations=2)
med = np.stack([ndi.median_filter(out[..., k], size=7) for k in range(3)], axis=2)
wz = ndi.gaussian_filter(zone.astype(float), 1.0) * zone
out = out * (1 - wz[..., None]) + med * wz[..., None]
Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)).save(dst)
print('R %.2f c (%.1f, %.1f) contrast %.1f  a %.3f' % (R, cx, cy, c, A))
