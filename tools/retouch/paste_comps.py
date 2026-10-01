#!/usr/bin/env python3
"""paste_comps.py — 제미나이 출력에서 **고른 덩어리만** 옮겨 붙인다(paste_boxes 의 덩어리판).
판 전체를 살짝 다시 그린 출력에서 상자로 자르면 곁의 물건(다시 그려진 잉크 가장자리)까지 딸려 오므로,
σ2 차 > THR 를 열기 1 → 넓힘 DIL 로 이은 덩어리 가운데 **씨앗 점(x,y)이 든 것만** 고르고
닫기 3 · 구멍 메움 · 넓힘 3 · σ1.5 섞음. (씨앗은 원본 좌표)
사용: python3 paste_comps.py ORIG V OUT THR DIL x,y [x,y ...]"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

op, vp, dst, thr, dil = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), int(sys.argv[5])
seeds = [tuple(int(v) for v in s.split(',')) for s in sys.argv[6:]]
O = np.asarray(Image.open(op).convert('RGB')).astype(np.float64)
V = np.asarray(Image.open(vp).convert('RGB').resize((O.shape[1], O.shape[0]), Image.LANCZOS)).astype(np.float64)
d = ndi.gaussian_filter(np.abs(O - V).mean(axis=2), 2.0)
m = ndi.binary_opening(d > thr, iterations=1)
lab, n = ndi.label(ndi.binary_dilation(m, iterations=dil))
keep = np.zeros_like(m)
for (x, y) in seeds:
    k = lab[y, x]
    if k == 0:
        # 씨앗이 덩어리 밖이면 가장 가까운 덩어리
        dd, (iy, ix) = ndi.distance_transform_edt(lab == 0, return_indices=True)
        k = lab[iy[y, x], ix[y, x]]
        print('seed', (x, y), 'snapped to label', k, 'dist %.1f' % dd[y, x])
    keep |= (lab == k)
mm = keep & (d > thr * 0.5)
mm = ndi.binary_closing(mm, iterations=3)
mm = ndi.binary_fill_holes(mm)
mm = ndi.binary_dilation(mm, iterations=3)
w = ndi.gaussian_filter(mm.astype(float), 1.5)
out = O * (1 - w[..., None]) + V * w[..., None]
Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)).save(dst)
ys, xs = np.nonzero(mm)
print('pasted px', int(mm.sum()), 'bbox', (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())) if mm.any() else None)
