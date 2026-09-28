#!/usr/bin/env python3
"""s03p02 — 우체부 가위의 아래 고리 안에 떠 있던 손가락 넷(손바닥·팔 없음 = 셋째 손)을 지운다.
고리 안쪽 다각형만 윗옷 청록 결(같은 윗옷의 깨끗한 조각을 타일로)으로 메운다 — 새 획 없음, 지우기만.
(해부 감사 2026-09-28 batch_00 에서 찾음)
사용: python3 tools/retouch/s03p02_ring_fingers.py <src.png> <out.png>"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')
a = np.asarray(im).astype(np.int32).copy()
poly = [(822,542),(828,543),(830,546),(831,550),(830,555),(829,560),(827,563),(825,566),
        (822,569),(817,572),(813,572),(810,569),(809,564),(810,558),(812,553),(814,549),(817,545)]
m = Image.new('L', im.size, 0); ImageDraw.Draw(m).polygon(poly, fill=255)
inside = np.asarray(m) > 0
# 깨끗한 윗옷 조각 (단추·주머니 없는 곳) — 어두운 화소가 없어야 한다
px0, py0, px1, py1 = 792, 610, 812, 645
patch = a[py0:py1, px0:px1]
assert (patch.sum(2) / 3).min() > 70, '조각에 어두운 화소가 있다'
ph, pw = patch.shape[:2]
ys, xs = np.nonzero(inside)
for y, x in zip(ys, xs):
    a[y, x] = patch[(y - 540) % ph, (x - 805) % pw]
res = Image.fromarray(a.clip(0, 255).astype(np.uint8))
# 이음새만 살짝: 다각형 테두리 1px 띠에 3x3 중앙값
edge = np.asarray(m.filter(ImageFilter.MaxFilter(3))) > 0
edge &= ~np.asarray(m.filter(ImageFilter.MinFilter(3))).astype(bool)
med = np.asarray(res.filter(ImageFilter.MedianFilter(3)))
b = np.asarray(res).copy(); b[edge & inside] = med[edge & inside]
Image.fromarray(b).save(out)
print('filled px', int(inside.sum()), 'patch mean', patch.reshape(-1, 3).mean(0).round(1))
