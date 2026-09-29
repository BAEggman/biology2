#!/usr/bin/env python3
"""s40p01 — 개념 논리 M: 두 가계도 모두 1대 부부의 자식 막대(가로)가 2대 넷 모두에 세로 막대를 내려
2대 두 부부가 다 형제끼리 짝지은 꼴이던 것 → 부부마다 가운데 쪽 한 사람(밖에서 들어온 배우자)의 세로 막대를 지운다.
왼쪽 판: x 186..194(둥근) · 290..296(네모) / 오른쪽 판: x 730..738(검은 둥근) · 832..840(검은 네모). y 169..189(바 아랫선 y 168 · 그늘 169..171 · 도형 윗선 y 190).
지운 자리(y 172..189)는 판 바탕 한 색 + 잔잡음, 가로 막대와 그늘(y 157..171)은 옆 12px 에서 옮겨 와 아랫선을 잇는다.
사용: python3 s40p01_inlaw_drops.py SRC.png OUT.png"""
import sys
import numpy as np
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB'); W, H = im.size
assert (W, H) == (1024, 559), (W, H)
a = np.asarray(im).astype(np.float32)
rng = np.random.default_rng(40)
DROPS = [(183, 198), (287, 300), (727, 742), (829, 844)]
for x0, x1 in DROPS:
    # board colour: median of the board just below the bar, left and right of the drop
    samp = np.concatenate([a[172:186, x0-14:x0-4].reshape(-1, 3), a[172:186, x1+4:x1+14].reshape(-1, 3)])
    bg = np.median(samp, axis=0)
    ys, ye = 172, 190
    a[ys:ye, x0:x1] = np.clip(bg + rng.normal(0, 1.6, (ye-ys, x1-x0, 3)), 0, 255)
    # rebuild the bar and its soft shadow (rows 157..171) across the joint from 13 px to the left
    a[157:172, x0:x1] = a[157:172, x0-13:x1-13]
Image.fromarray(a.astype(np.uint8)).save(dst)
print('ok', dst)
