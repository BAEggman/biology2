#!/usr/bin/env python3
"""s01p02 — 개념 논리 M(계류 밧줄 I 두 겹 · II 한 겹이 안 읽힘): 제미나이 같은 대화 v2 는 왼쪽 배 계류 밧줄 = 꼰 두 겹 밧줄 ·
오른쪽 배 = 가는 한 가닥 · 작업대 = 왼쪽에서 가는 한 가닥이 들어와 오른쪽 끝에 꼰 두 겹 밧줄이 늘어짐 으로 맞췄으나,
v1 에서 가는 끈으로 바꿔 둔 오른쪽 부두 가운데 궤짝(x 555..735 · y 655..805)을 다시 굵은 꼰 밧줄로 칭칭 감아 버림
→ 그 궤짝 윤곽(육각 다각형)만 v1 에서 옮겨 옴(가장자리 흐림 2.5px) — 바로 오른쪽 v1 작업대 밧줄 고리는 들이지 않음. 모든 궤짝 끈이 양쪽 똑같이 가는 끈 한 줄.
사용: python3 s01p02_crate_from_v1.py V2.png V1.png OUT.png"""
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
v2p, v1p, dst = sys.argv[1], sys.argv[2], sys.argv[3]
A = np.asarray(Image.open(v2p).convert('RGB')).astype(np.float32)
B = np.asarray(Image.open(v1p).convert('RGB')).astype(np.float32)
assert A.shape == B.shape == (1024, 1024, 3)
# the crate's outline (isometric box) with its cords and a little floor shadow — v1's bench-rope loop just right of it stays out
POLY = [(566, 700), (645, 648), (742, 700), (742, 797), (652, 824), (566, 787)]
M = Image.new('L', (1024, 1024), 0); ImageDraw.Draw(M).polygon(POLY, fill=255)
w = ndi.gaussian_filter(np.asarray(M).astype(np.float32) / 255.0, 2.5)[..., None]
out = A * (1 - w) + B * w
# v1's bench-rope loop grazes the crate's top-right corner (x 698..748 · y 660..706): where v1 is dark but v2 is not, take v2
bx0, bx1, by0, by1 = 698, 748, 660, 706
lA = A[by0:by1, bx0:bx1].mean(2); lB = B[by0:by1, bx0:bx1].mean(2)
loop = ndi.binary_dilation((lB < 140) & (lA > 170), iterations=2)
sub = out[by0:by1, bx0:bx1]
sub[loop] = A[by0:by1, bx0:bx1][loop]
out[by0:by1, bx0:bx1] = sub
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst); print('ok', dst)
