#!/usr/bin/env python3
"""sparkscan.py — 설치본 전체에서 제미나이 반짝이 표식(네 꼭지 별)을 찾는다.
고역(L − 중앙값41) 위에서 별 모양 틀(astroid a=24)과 정규화 상관(TM_CCOEFF_NORMED)을 재어 점수 순으로 찍는다."""
import sys, glob, os
import numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi
a = 24
yy, xx = np.mgrid[-30:31, -30:31].astype(float)
T = ((np.abs(xx) / a) ** (2 / 3) + (np.abs(yy) / a) ** (2 / 3) <= 1).astype(np.float32)
T = ndi.gaussian_filter(T, 1.0).astype(np.float32)
res = []
files = sorted(glob.glob('img/*.webp')) if len(sys.argv) < 2 else sys.argv[1:]
for f in files:
    A = np.asarray(Image.open(f).convert('RGB')).astype(np.float32)
    H, W = A.shape[:2]
    L = A.mean(axis=2)
    y0, x0 = int(H * 0.78), int(W * 0.78)
    sub = L[y0:, x0:]
    hp = (sub - ndi.median_filter(sub, size=41)).astype(np.float32)
    r = cv2.matchTemplate(hp, T, cv2.TM_CCOEFF_NORMED)
    _, mx, _, loc = cv2.minMaxLoc(r)
    cx, cy = loc[0] + 30 + x0, loc[1] + 30 + y0
    # 별 안쪽 평균 밝기 초과
    inside = hp[loc[1]:loc[1] + 61, loc[0]:loc[0] + 61][T > 0.5]
    outside = hp[loc[1]:loc[1] + 61, loc[0]:loc[0] + 61][T < 0.05]
    res.append((mx, os.path.basename(f), cx, cy, float(inside.mean() - outside.mean())))
res.sort(reverse=True)
for mx, f, cx, cy, ex in res:
    print('%.3f  %-14s  (%d,%d)  excess %.1f' % (mx, f, cx, cy, ex))
