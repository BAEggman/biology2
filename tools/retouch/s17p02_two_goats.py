#!/usr/bin/env python3
"""s17p02 — 개념 논리 M(NKCC2 는 관강에서 받아 세포 쪽으로 = 재흡수): 기계가 관 밖에 붙어 깔때기로 밖에서 받고 짐이 바깥 바닥에서 기계를 향하던 것 →
제미나이 v1(기계의 흡입관이 관 벽을 뚫고 관 안 알갱이로 · 밖으로 비탈진 배출 활송로에서 소금 자루와 칼이 미끄러져 나오고 염소들이 관에서 멀어짐)이
염소를 셋 그림(Cl 둘 = 염소 둘) → 맨 왼쪽 흰 염소(x 620..770 · y 830..990)와 그 그림자만 바탕 한 색 + 잔잡음으로 지움 · U 관 바깥 윤곽(줄마다 잰 맨 바깥 선 +4px) 왼쪽은 건드리지 않음.
사용: python3 s17p02_two_goats.py V1.png OUT.png"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
src, dst = sys.argv[1], sys.argv[2]
a = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
assert a.shape == (1024, 1024, 3), a.shape
rng = np.random.default_rng(172)
X0, X1, Y0, Y1 = 620, 771, 830, 990
# the U-tube's outer outline near the goat (x at given y) — everything left of it (+6 px) is protected
CY = [790, 800, 820, 840, 860, 870, 880, 890, 900, 910, 920, 990]
CX = [690, 686, 677, 666, 651, 643, 634, 625, 614, 601, 588, 560]   # measured outermost outline
sub = a[Y0:Y1, X0:X1]
ring = np.concatenate([a[Y1:Y1+6, X0:X1].reshape(-1, 3), a[Y0:Y1, X1-2:X1+2].reshape(-1, 3)])
lum_r = ring.mean(1)
bg = np.median(ring[lum_r > np.percentile(lum_r, 50)], axis=0)
diff = np.abs(sub - bg).sum(2)
m = diff > 14
yy, xx = np.mgrid[Y0:Y1, X0:X1]
curve = np.interp(yy, CY, CX)
m &= xx > curve + 5
m &= ~((yy >= 905) & (xx >= 748))      # the brown goat's hind hoof and its shadow start at x ≈ 758 below y 905
m = ndi.binary_dilation(m, iterations=2) & (xx > curve + 4) & ~((yy >= 905) & (xx >= 750))
sub[m] = np.clip(bg + rng.normal(0, 1.4, (m.sum(), 3)), 0, 255)
a[Y0:Y1, X0:X1] = sub
print('bg', bg.astype(int), 'px', int(m.sum()))
Image.fromarray(a.astype(np.uint8)).save(dst)
