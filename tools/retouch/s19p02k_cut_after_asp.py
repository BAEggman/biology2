#!/usr/bin/env python3
"""s19p02k — 캐스터네츠(캐스페이스)가 아스파라거스(Asp) 뒤 **셋째** 구슬을 물고 그 뒤가 끊겨 있었다(logic_0929 s19p02k 2 M).
캐스페이스는 Asp **바로 뒤** 결합을 자른다 → 아스파라거스와 캐스터네츠 사이 구슬 둘(x 524..593)을 빼고,
그 오른쪽 띠(x ≥ 594 · y 240..470 — 위 못걸이는 y ≤ 200 이라 안 건드림)를 왼쪽으로 70px 당긴다.
맨 오른쪽 빈 70px 는 사슬 구슬 주기(37px)의 두 배(74px) 앞 기둥을 되풀이해 채운다(사슬 띠 y 340..412 만 · 나머지는 바탕).
사용: python3 tools/retouch/s19p02k_cut_after_asp.py <입력.png> <출력.png>"""
import sys
import numpy as np
from PIL import Image
src, out = sys.argv[1:3]
im = Image.open(src).convert('RGB')
assert im.size == (1024, 506), im.size
a = np.asarray(im).copy()
bg = np.array([251, 249, 234], dtype=np.uint8)
X0, X1, S = 524, 594, 70
Y0, Y1 = 240, 470
b = a.copy()
b[Y0:Y1, X0:1024 - S] = a[Y0:Y1, X1:1024]
# fill right strip
b[Y0:Y1, 1024 - S:1024] = bg
for x in range(1024 - S, 1024):
    b[340:412, x] = b[340:412, x - 74]
Image.fromarray(b).save(out)
print('saved', out)
