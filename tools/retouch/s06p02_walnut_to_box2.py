#!/usr/bin/env python3
"""s06p02 — 핵형질체(쪼그라든 호두)를 둘째 상자 안 바닥(셋째 상자 곁)에 놓는다.
제미나이 2라운드(v4)는 상자 넷을 또렷이 그렸지만 호두를 옮기지 못하고 지워 버렸다. 1라운드(v3)의 호두를 타원 가면으로 떼어
0.75배로 줄여 v4 의 둘째 상자 바닥(셋째 상자 오른쪽 벽과 둘째 상자 테 사이)에 붙인다 — 핵형질체 자리는 바깥 두 막과 안쪽 두 막 사이.
사용: python3 tools/retouch/s06p02_walnut_to_box2.py <v3.png> <v4.png> <out.png> [cx cy scale]"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
v3, v4, out = sys.argv[1:4]
cx, cy, sc = (float(a) for a in (sys.argv[4:7] if len(sys.argv) > 6 else (399, 446, 0.75)))
A = Image.open(v3).convert('RGB'); B = Image.open(v4).convert('RGB')
# 호두 타원 (v3): 가운데 (122,445), 반지름 (25,20) — 테두리 선 포함
x0, y0, x1, y1 = 97, 425, 148, 466
patch = A.crop((x0, y0, x1, y1))
m = Image.new('L', patch.size, 0)
ImageDraw.Draw(m).ellipse((0, 0, patch.size[0]-1, patch.size[1]-1), fill=255)
m = m.filter(ImageFilter.GaussianBlur(0.8))
w, h = patch.size
nw, nh = round(w*sc), round(h*sc)
patch = patch.resize((nw, nh), Image.LANCZOS); m = m.resize((nw, nh), Image.LANCZOS)
ox, oy = round(cx - nw/2), round(cy - nh/2)
B.paste(patch, (ox, oy), m)
B.save(out)
print('pasted', (ox, oy, ox+nw, oy+nh))
