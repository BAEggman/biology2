#!/usr/bin/env python3
"""s09p03 — 오른쪽 아래 반짝이 표식(중심 (903.5, 903.5))이 **담 윗단의 위 끝**(크림 하늘 · 담 윗선 · 벽돌 · 세로 줄눈 x≈915)에 걸침.
제미나이 모음판(grid_sp4)은 이 칸 전체를 벽돌 담으로 바꿔 버렸고(rms 116), 결 복제(spark_clone)는 왼쪽 담 윗선이 두 줄(893 · 899–901)이라
오른쪽 한 줄(896–898)과 이어지지 않았다 → 세 띠로 나눠 손으로:
  ① y ≤ 888 크림: 바로 위(0, −46)의 맨 크림을 옮김.
  ② 889 ≤ y ≤ 902 담 윗선: 벽돌마다 윗선 모양이 달라(왼 벽돌 두 줄 892–895 · 897–900 / 오른 벽돌 한 줄 896–899)
     줄눈 x = 913 왼쪽은 x 864..872 의 세로 단면, 오른쪽은 x 936..944 의 세로 단면을 가로로 늘여 깖(3px 섞음).
  ③ y ≥ 903 벽돌·줄눈: 같은 단 왼쪽 줄눈(x≈822)을 이 줄눈(x≈915)에 맞춘 (−93, 0) 복제.
덮을 곳 = 별(spark_clone 의 맞춘 별 M > 0.01)을 3px 넓힘 · 띠 사이는 1px 섞음 · 바깥은 σ1.5.
사용: python3 s09p03_spark.py ORIG.png OUT.png"""
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spark_clone import star_mask_full, fit_geometry

op, dst = sys.argv[1], sys.argv[2]
full = np.asarray(Image.open(op).convert('RGB')).astype(np.float64)
H, W = full.shape[:2]
L = full.mean(axis=2)
c, R, cx, cy = fit_geometry(L)
M = star_mask_full(R, cx, cy)
mask = ndi.binary_dilation(M > 0.01, iterations=3)
yy, xx = np.mgrid[0:H, 0:W]
srcA = np.roll(full, 46, axis=0)                       # src[y] = full[y − 46]
profL = full[:, 864:873].mean(axis=1)                  # 왼쪽 벽돌의 세로 단면(담 윗선 892–895 + 벽돌 윗선 897–900)
profR = full[:, 936:945].mean(axis=1)                  # 오른쪽 벽돌의 세로 단면(한 줄 896–899)
JX = 913                                               # 줄눈(왼 벽돌 끝) — 여기서 왼 단면 → 오른 단면
tL = np.clip((JX + 1.5 - xx) / 3.0, 0, 1)[..., None]
srcB = np.repeat(profL[:, None, :], W, axis=1) * tL + np.repeat(profR[:, None, :], W, axis=1) * (1 - tL)
srcC = np.roll(full, 93, axis=1)                       # src[x] = full[x − 93]
zA = (yy <= 888).astype(float)
zB = ((yy >= 889) & (yy <= 902)).astype(float)
zC = (yy >= 903).astype(float)
# 띠 사이 1px 섞음
zA, zB, zC = [ndi.uniform_filter(z, size=(3, 1)) for z in (zA, zB, zC)]
s = zA + zB + zC
src = (srcA * zA[..., None] + srcB * zB[..., None] + srcC * zC[..., None]) / s[..., None]
w = np.maximum(ndi.gaussian_filter(mask.astype(float), 1.5), mask.astype(float))
out = full * (1 - w[..., None]) + src * w[..., None]
Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)).save(dst)
print('R %.2f c (%.1f, %.1f)  mask px %d' % (R, cx, cy, int(mask.sum())))
