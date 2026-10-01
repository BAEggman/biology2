#!/usr/bin/env python3
"""paste_boxes.py — 제미나이 출력에서 **바뀐 곳만** 옮겨 붙이는 일반 도구(판마다 쓰던 「σ2 차 > 문턱 · 상자 안」 방식을 한 줄로).
원본 ↔ 출력 밝기 차를 σ2 로 번진 것이 문턱보다 큰 화소 가운데, 준 상자들(각 6px 넓혀) 안의 것만 → 닫기 3 · 구멍 메움 · 넓힘 3 · σ1.5 섞음.
상자 밖(제미나이가 판 전체를 살짝 다시 그린 것)은 원본 그대로 둔다.
사용: python3 paste_boxes.py ORIG.png V.png OUT.png THR x0,y0,x1,y1 [x0,y0,x1,y1 ...]
      ORIG 와 V 는 크기가 같아야 한다(어긋남은 재지 않는다 — 제미나이 편집은 보통 0px)."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

op, vp, dst, thr = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
boxes = [tuple(int(v) for v in b.split(',')) for b in sys.argv[5:]]
O = np.asarray(Image.open(op).convert('RGB')).astype(np.float64)
V = np.asarray(Image.open(vp).convert('RGB')).astype(np.float64)
assert O.shape == V.shape, (O.shape, V.shape)
H, W = O.shape[:2]
d = ndi.gaussian_filter(np.abs(O - V).mean(axis=2), 2.0)
m = np.zeros((H, W), bool)
for (x0, y0, x1, y1) in boxes:
    b = np.zeros((H, W), bool)
    b[max(0, y0 - 6):min(H, y1 + 6), max(0, x0 - 6):min(W, x1 + 6)] = True
    mm = (d > thr) & b
    mm = ndi.binary_closing(mm, iterations=3)
    mm = ndi.binary_fill_holes(mm)
    mm = ndi.binary_dilation(mm, iterations=3) & b
    m |= mm
w = ndi.gaussian_filter(m.astype(float), 1.5)
out = O * (1 - w[..., None]) + V * w[..., None]
Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)).save(dst)
print('pasted px', int(m.sum()), 'boxes', boxes)
