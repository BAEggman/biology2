#!/usr/bin/env python3
"""s07p05 — 되먹임 가는 관이 본관 아래쪽에 T 이음(가로 토막 + T 이음쇠)으로 붙어 있던 것(= 내려가는 길에서 갈라져 거슬러 옴) → 이음 지움.
가는 관은 원래 판 아래 끝 밖에서 올라오므로, T 자리(x 399..466, y 944..983)를 바로 아래 40 줄(y 984..1023 — 본관 오른쪽 윤곽 · 바탕 · 곧은 가는 관)로 덮는다.
둘 다 세로로 고른 결이라 그대로 맞는다. 가장자리 σ1 섞음.
사용: python3 s07p05_untee.py ORIG.png OUT.png"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
op, dst = sys.argv[1], sys.argv[2]
O = np.asarray(Image.open(op).convert('RGB')).astype(np.float64)
H, W = O.shape[:2]
x0, x1, y0, y1, dy = 399, 467, 944, 984, 40
src = O.copy()
src[y0:y1, x0:x1] = O[y0 + dy:y1 + dy, x0:x1]
m = np.zeros((H, W)); m[y0:y1, x0:x1] = 1
w = np.maximum(ndi.gaussian_filter(m, 1.0), ndi.binary_erosion(m > 0, iterations=1).astype(float))
out = O * (1 - w[..., None]) + src * w[..., None]
Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)).save(dst)
print('ok', (x0, y0, x1, y1), 'from +%d rows' % dy)
