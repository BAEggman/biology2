#!/usr/bin/env python3
"""s19p02m — 제미나이 v3a(같은 대화 셋째 판) 손질: 맨 아래 염색체 곁에 남은 느슨한 끈 둘을 지운다.
① 왼쪽 아래 바닥의 매듭 끈(x 288..422 · y 446..498) ② Mad2 끈 가운데 매듭에서 늘어진 고리 꼬리(x 640..700 · y 453..470 과 x 640..782 · y 464..496).
팽팽한 두 염색체 밑의 떨어진 끈 둘과, 빈 걸쇠 → 걸이판 끈(매듭 둘)은 그대로. 바탕은 둘레 한 색 + 잔잡음.
사용: python3 s19p02m_clean_loose.py V3A.png OUT.png"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB'); W, H = im.size
assert (W, H) == (1024, 506), (W, H)
a = np.asarray(im).astype(np.float32)
rng = np.random.default_rng(19)
BOXES = [(288, 446, 422, 498), (640, 453, 700, 470), (640, 464, 782, 496)]
for (x0, y0, x1, y1) in BOXES:
    sub = a[y0:y1, x0:x1]
    # local background = median of a wider ring of light pixels
    X0, Y0, X1, Y1 = max(0, x0-30), max(0, y0-20), min(W, x1+30), min(H, y1+20)
    wide = a[Y0:Y1, X0:X1].reshape(-1, 3)
    lum = wide.mean(1)
    bg = np.median(wide[lum > np.percentile(lum, 60)], axis=0)
    dev = np.abs(sub - bg).sum(2) > 14
    dev = ndi.binary_dilation(dev, iterations=2)
    n = dev.sum()
    sub[dev] = np.clip(bg + rng.normal(0, 1.8, (n, 3)), 0, 255)
    a[y0:y1, x0:x1] = sub
    print((x0, y0, x1, y1), 'bg', bg.astype(int), 'px', int(n))
Image.fromarray(a.astype(np.uint8)).save(dst)
