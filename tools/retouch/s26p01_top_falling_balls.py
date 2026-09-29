#!/usr/bin/env python3
"""s26p01 — 위 곡선 아래로 떨어지던 구슬(과 움직임 선)을 지운다. 2라운드(v2)에서 위 여섯은 모두 두 손으로 매달려
배 주머니에 구슬을 담았는데, 옛 그림의 「위에서 떨어지는 구슬」이 남아 「위(폐, 포화)에서도 내준다」로 읽혔다.
위 = 붙든다 · 아래 = 내준다 를 또렷이 하려고 위 곡선 밑 구슬 일곱과 움직임 선만 지운다(새 획 없음).
구슬·선마다 작은 상자 안에서만(민 크림 바탕) — 레일·인물·주머니는 상자 밖.
사용: python3 tools/retouch/s26p01_top_falling_balls.py <src.png> <out.png>"""
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')
a = np.asarray(im).astype(np.float64)
H, W = a.shape[:2]
BOXES = [(531, 212, 542, 243), (525, 244, 550, 269), (536, 276, 549, 313), (533, 315, 551, 334),
         (624, 248, 637, 291), (620, 291, 643, 315), (607, 327, 628, 348), (631, 351, 644, 364),
         (728, 255, 749, 313), (735, 316, 761, 341), (727, 364, 748, 386)]
R = np.zeros((H, W), bool)
for x0, y0, x1, y1 in BOXES: R[y0:y1, x0:x1] = True
ring = binary_dilation(R, iterations=6) & ~binary_dilation(R, iterations=3)
bg = np.median(a[ring].reshape(-1, 3), axis=0)
dist = np.abs(a - bg).sum(2)
M = R & (dist > 30)
M = binary_dilation(M, iterations=2) & R
rng = np.random.default_rng(11)
b = a.copy()
b[M] = bg + rng.normal(0, 1.4, (int(M.sum()), 3))
Image.fromarray(b.clip(0, 255).astype(np.uint8)).save(out)
print('bg', bg.round(1), 'erased px', int(M.sum()))
