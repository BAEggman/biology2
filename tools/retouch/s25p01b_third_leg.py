#!/usr/bin/env python3
"""s25p01b — 겨자색 원피스 여자 치마 밑의 셋째 다리를 지운다(해부 감사 2026-09-28 batch_02).
치마 밑단 오른쪽에서 나와 회색 양복 사내 바짓가랑이 뒤로 들어가는 다리(보이는 부분 x362–370 · y494–516)와
그 바짓가랑이 오른쪽으로 삐져나온 구두 코(x384–390 · y521–527)만 지운다. 치마 밑단 선 · 바짓가랑이 윤곽은 그대로.
메우기: 줄마다 같은 줄의 가까운 바닥 화소(왼쪽 x355–360 / 오른쪽 x391–396)의 중앙값 + 작은 잡음. 새 획 없음.
사용: python3 tools/retouch/s25p01b_third_leg.py <src.png> <out.png>"""
import sys
import numpy as np
from PIL import Image, ImageDraw
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')
a = np.asarray(im).astype(np.float64).copy()
rng = np.random.default_rng(3)
def fill(poly, xs_ref):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).polygon(poly, fill=255)
    M = np.asarray(m) > 0
    ys, xs = np.nonzero(M)
    for y in sorted(set(ys.tolist())):
        ref = np.median(a[y, xs_ref[0]:xs_ref[1]], axis=0)
        row = M[y]
        a[y, row] = ref + rng.normal(0, 1.5, (int(row.sum()), 3))
    return int(M.sum())
n1 = fill([(362,494),(369,494),(369,505),(367,506),(367,515),(365,517),(362,512)], (355, 361))
n2 = fill([(384,521),(390,521),(391,527),(384,528)], (391, 397))
Image.fromarray(a.clip(0, 255).astype(np.uint8)).save(out)
print('leg px', n1, 'toe px', n2)
