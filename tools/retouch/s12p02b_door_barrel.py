#!/usr/bin/env python3
"""s12p02b_door_barrel.py ORIG FIX0 OUT — 제미나이가 왼쪽 벽에 아치문을 내면서 둑길 왼쪽 끝의 통 하나를 지웠다.
원본의 그 통(상자 36,286,96,392)을 문 앞에 도로 얹는다(통 색·윤곽 마스크 · 가장 큰 덩어리 · 1px 깎고 번짐)."""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
op, fp, dst = sys.argv[1], sys.argv[2], sys.argv[3]
O = np.asarray(Image.open(op).convert('RGB')).astype(float)
F = np.asarray(Image.open(fp).convert('RGB')).astype(float)
x0, y0, x1, y1 = 40, 293, 96, 392
sub = O[y0:y1, x0:x1]; R, G, B = sub[..., 0], sub[..., 1], sub[..., 2]; lum = sub.mean(2)
m = ((R - B > 35) & (G - B > 28)) | (lum < 70)
m = ndi.binary_closing(m, iterations=2); m = ndi.binary_fill_holes(m)
lab, n = ndi.label(m); sizes = ndi.sum(m, lab, range(1, n + 1)); m = lab == (int(np.argmax(sizes)) + 1)
m = ndi.binary_erosion(m, iterations=1)
a = ndi.gaussian_filter(m.astype(float), 0.7)
out = F.copy()
# 문이 틀 밖(왼쪽 여백)까지 뚫려 나온 것을 막는다 — 틀 선(x≈43~47)과 그 왼쪽 여백은 원본으로(y 0~430)
out[0:430, 0:47] = O[0:430, 0:47]
out[y0:y1, x0:x1] = F[y0:y1, x0:x1] * (1 - a[..., None]) + sub * a[..., None]
Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)).save(dst)
print('barrel px', int(m.sum()))
