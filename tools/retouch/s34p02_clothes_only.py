#!/usr/bin/env python3
"""s34p02 — 개념 논리 M 3–5(형제 판 s34p03 의 옷 색 규칙: 청록 = 난세포 하나뿐 · 회색 = 조세포·반족세포 · 겨자색 = 극핵 · 붉은 옷 = 정자뿐):
앉은 난세포 회갈색 · 조세포 둘 청록 · 바구니 둘 청록 + 붉은 · 반족세포 셋 청록 · 붉은 · 겨자색이던 것 →
제미나이 v1(옷 색만: 난세포 옷 청록 · 조세포 둘 회색 · 바구니 둘 겨자색 · 반족세포 셋 회색)을 쓰되, **옷 색이 바뀐 자리만** 옮겨 붙이고
나머지(대포·아치·바닥·얼굴의 선)는 원본(설치본) 그대로 둔다 — 제미나이 출력은 판 전체가 살짝 무르고 대비가 낮다(국소 차이 5~9).
정렬은 세 곳에서 재어 어긋남 0px.
  ① 마스크: Lab 색도 차이 √(Δa²+Δb²) > 6 인 화소(인물 띠 x 340..960 · y 280..470 안) → 닫기 2 · 구멍 메움 · 열기 1 · 60px 미만 덩어리 뺌 · 넓힘 2 · 가우스 σ1.2.
     밝기(L)는 v1 을 쓰지 않고 **원본 L 에 v1 의 색도(a·b)만** 얹는다 — 원본의 선·주름 음영이 그대로 남는다.
     단, 청록·회색으로 바꾼 옷은 원본보다 밝거나 어두워야 할 수 있어 L 도 조금 옮긴다: L = 원본 L + 0.6·(v1 L − 원본 L)(가우스 σ2 로 번진 차이만).
사용: python3 s34p02_clothes_only.py ORIG.png V1.png OUT.png"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import color

op, vp, dst = sys.argv[1], sys.argv[2], sys.argv[3]
O = np.asarray(Image.open(op).convert('RGB')).astype(np.float64) / 255
V = np.asarray(Image.open(vp).convert('RGB')).astype(np.float64) / 255
assert O.shape == V.shape, (O.shape, V.shape)
H, W = O.shape[:2]
Lo = color.rgb2lab(O)
Lv = color.rgb2lab(V)
dc = np.hypot(Lv[..., 1] - Lo[..., 1], Lv[..., 2] - Lo[..., 2])
yy, xx = np.mgrid[0:H, 0:W]
zone = (xx >= 340) & (xx < 960) & (yy >= 280) & (yy < 470)
m = (ndi.gaussian_filter(dc, 1.0) > 6) & zone
m = ndi.binary_closing(m, iterations=2)
m = ndi.binary_fill_holes(m)
m = ndi.binary_opening(m, iterations=1)
lab_, n_ = ndi.label(m)
sz = ndi.sum(m, lab_, index=np.arange(1, n_ + 1))
m = np.isin(lab_, 1 + np.flatnonzero(sz >= 60))   # 바구니·벽·통나무의 잔 얼룩(60px 미만)은 빼고 옷 덩어리만
m = ndi.binary_dilation(m, iterations=2)
w = ndi.gaussian_filter(m.astype(float), 1.2)
print('mask px', int(m.sum()))
dL = ndi.gaussian_filter(Lv[..., 0] - Lo[..., 0], 2.0)
out = Lo.copy()
out[..., 0] = Lo[..., 0] + 0.6 * dL * w
out[..., 1] = Lo[..., 1] * (1 - w) + Lv[..., 1] * w
out[..., 2] = Lo[..., 2] * (1 - w) + Lv[..., 2] * w
rgb = np.clip(color.lab2rgb(out), 0, 1)
Image.fromarray((rgb * 255 + 0.5).astype(np.uint8)).save(dst)
Image.fromarray((w * 255).astype(np.uint8)).save(dst.replace('.png', '_mask.png'))
print('saved', dst)
