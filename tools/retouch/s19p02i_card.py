#!/usr/bin/env python3
"""s19p02i — 개념 논리 m 3·5(Ced-3 은 양쪽에 있다 — 상태만 다름): 점 셋 판이 오른쪽(벌어진 캐스터네츠 곁)에만 있던 것 →
제미나이 v1 이 왼쪽 닫힌 캐스터네츠 오른쪽에 납작하게 눕힌 점 셋 판만 옮긴다(캐스터네츠·벽 판 등은 v1 이 조금씩 다시 그려 원본 유지).
  판 가면 = 상자(x 415..510 · y 300..360) 안 v1 의 밝은 판 면(L > 215 · 채도 < 30)의 가장 큰 덩어리 → 구멍 메움(점 셋 포함) → 넓힘 4(윤곽 · 그림자) · σ1.2 섞음.
사용: python3 s19p02i_card.py ORIG.png V1.png OUT.png"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import color

op, vp, dst = sys.argv[1], sys.argv[2], sys.argv[3]
O = np.asarray(Image.open(op).convert('RGB')).astype(np.float64)
V = np.asarray(Image.open(vp).convert('RGB')).astype(np.float64)
H, W = O.shape[:2]
Lab = color.rgb2lab(V / 255)
yy, xx = np.mgrid[0:H, 0:W]
box = (xx >= 415) & (xx < 510) & (yy >= 300) & (yy < 360)
face = box & (Lab[..., 0] > 86) & (np.hypot(Lab[..., 1], Lab[..., 2]) < 14)
lab_, n_ = ndi.label(face)
sz = ndi.sum(face, lab_, range(1, n_ + 1))
face = lab_ == (1 + int(np.argmax(sz)))
face = ndi.binary_fill_holes(ndi.binary_closing(face, iterations=2))
m = ndi.binary_dilation(face, iterations=4) & box
w = ndi.gaussian_filter(m.astype(float), 1.2)
w = np.maximum(w, ndi.binary_erosion(m, iterations=1).astype(float))
out = O * (1 - w[..., None]) + V * w[..., None]
Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)).save(dst)
ys, xs = np.nonzero(m)
print('card px', int(m.sum()), 'bbox', (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())))
