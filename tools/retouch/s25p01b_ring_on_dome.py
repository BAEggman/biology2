#!/usr/bin/env python3
"""s25p01b — 왼쪽 문틀 위에서 고리(cAMP)가 돔 덮개(CRP) 오른쪽에 따로 서 있던 것 → 돔 오른쪽 어깨 앞에 겹쳐 걸린 한 덩이로(형제 판 s25p01 처럼).
개념 논리 M(logic_0929 s25p01b 2): cAMP 는 CRP 와 한 덩이(cAMP-CRP)로 DNA 에 얹힌다.
그림은 1024×572(가로 판). 고리 = 원 중심 (379.36, 81.63) · 테 반지름 19–32(원 맞춤) + 위 집게 상자 x 372..388 × y 43..66.
① 오림: 그 띠 안에서 바탕(251,241,217)과 색 거리 d 로 부드러운 가면 α = clip((d−6)/20) — 고리 속 구멍·바깥 바탕은 빠진다
② 제자리 지움: 띠(18.5–32.5)·집게 상자를 줄마다 — y<95 는 바탕색 + 잡음, y≥95 는 같은 줄 x 410..420(고리 오른쪽 맨 문틀)의 중앙값(문틀 윗선이 줄 단위로 이어진다)
③ 붙임: dx=−44 · dy=0 — 고리 왼쪽 반이 돔 오른쪽 어깨 앞에 겹치고 밑은 문틀 윗선 그대로
사용: python3 tools/retouch/s25p01b_ring_on_dome.py <입력.png> <출력.png>"""
import sys
import numpy as np
from PIL import Image
src, out = sys.argv[1:3]
im = Image.open(src).convert('RGB')
assert im.width == 1024, im.size
a = np.asarray(im, dtype=float)
H, W = a.shape[:2]
bg = np.array([251., 241., 217.])
d = np.sqrt(((a - bg) ** 2).sum(axis=2))
cx, cy = 379.36, 81.63
Y, X = np.mgrid[0:H, 0:W]
R = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
clip = (X >= 372) & (X <= 388) & (Y >= 43) & (Y <= 66)
band = ((R >= 19) & (R <= 32)) | clip
alpha = np.clip((d - 6) / 20, 0, 1) * band
# erase
er = a.copy()
rng = np.random.default_rng(3)
zone = ((R >= 18.5) & (R <= 32.5)) | clip
ys, xs = np.where(zone)
for y, x in zip(ys, xs):
    if y < 95:
        er[y, x] = bg + rng.normal(0, 0.5, 3)
    else:
        er[y, x] = np.median(a[y, 410:421], axis=0)
# paste
DX, DY = -44, 0
res = er.copy()
ys, xs = np.where(alpha > 0)
for y, x in zip(ys, xs):
    ty, tx = y + DY, x + DX
    w = alpha[y, x]
    res[ty, tx] = res[ty, tx] * (1 - w) + a[y, x] * w
Image.fromarray(res.round().clip(0, 255).astype(np.uint8)).save(out)
print('saved', out, 'ring px', int((alpha > 0.5).sum()))
