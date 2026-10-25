#!/usr/bin/env python3
"""finish.py — 통합판 마감: 바탕(base2x)과 달라진 곳(>18) ∧ 윤곽 근처(maximum_filter(gradient,9)>12)에만 UnsharpMask(1.4,50,2).
사용: finish.py cur.png base2x.png final.png   (크기는 2배 그대로 저장 · install_img.py 가 1024 로 줄인다)"""
import sys
import numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import maximum_filter, sobel

cur = Image.open(sys.argv[1]).convert('RGB'); base = Image.open(sys.argv[2]).convert('RGB')
A = np.asarray(cur).astype(float); B = np.asarray(base).astype(float)
diff = np.abs(A - B).mean(axis=2) > 18
lum = A.mean(axis=2); g = np.hypot(sobel(lum, 0), sobel(lum, 1)) / 8.0
edges = maximum_filter(g, 9) > 12
M = (diff & edges).astype(float)
S = np.asarray(cur.filter(ImageFilter.UnsharpMask(radius=1.4, percent=50, threshold=2))).astype(float)
out = A * (1 - M[..., None]) + S * M[..., None]
Image.fromarray(np.clip(out, 0, 255).astype('uint8')).save(sys.argv[3])
print('finish: 선명화 비율 %.1f%%' % (100 * M.mean()))
