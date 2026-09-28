#!/usr/bin/env python3
"""s12p05 — 피리 부는 사람이 옮기는 꼬리표 안의 글자 같은 긁힘을 지운다(지우기만, 새 획 없음).
제미나이 2라운드(s12p05_v2)에 「plain, no marks」를 넣었지만 긁힘이 그대로 남아서 손 보정.
사용: python3 tools/retouch/s12p05_tag_plain.py <src.png> <out.png>"""
import sys
import numpy as np
from PIL import Image, ImageDraw
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')
a = np.asarray(im).astype(np.int32).copy()
# 꼬리표 안쪽(테두리·손끝 제외) 다각형
poly = [(568, 579), (581, 579), (586, 588), (578, 595), (570, 590)]
m = Image.new('L', im.size, 0); ImageDraw.Draw(m).polygon(poly, fill=255)
inside = np.asarray(m) > 0
lum = a.sum(2) / 3
light = inside & (lum >= 200)
col = np.median(a[light], axis=0)
dark = inside & (lum < 200)
a[dark] = col
# 가장자리 이음새를 누그러뜨리려고 다각형 안만 3x3 평균 한 번
b = a.copy()
ys, xs = np.nonzero(inside)
for y, x in zip(ys, xs):
    b[y, x] = a[y-1:y+2, x-1:x+2].reshape(-1, 3).mean(0)
Image.fromarray(b.clip(0, 255).astype(np.uint8)).save(out)
print('tag colour', col, 'erased px', int(dark.sum()))
